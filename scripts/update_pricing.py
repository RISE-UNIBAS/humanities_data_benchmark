#!/usr/bin/env python3
"""
Semi-automated pricing updater for pricing.json

Usage:
    python scripts/update_pricing.py --date 2026-02-10 [--dry-run]

This script:
1. Finds non-legacy models in benchmarks_tests.csv
2. Identifies models missing from pricing.json for the given date
3. Scrapes pricing from provider websites
4. Shows a diff of proposed changes
5. Updates pricing.json after user confirmation
"""

import argparse
import csv
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import difflib

# Load environment variables from .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Not required, will use system environment

# Optional imports for web scraping
try:
    import requests
    from bs4 import BeautifulSoup
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False
    print("Warning: requests and/or beautifulsoup4 not installed. Web scraping disabled.")
    print("Install with: pip install requests beautifulsoup4")

# Optional playwright for pages with anti-bot protection
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class PricingUpdater:
    """Handles pricing updates for LLM models"""

    COHERE_MODEL_URLS = {
        'command-r-08-2024':        'https://docs.cohere.com/docs/command-r',
        'command-r-plus-08-2024':   'https://docs.cohere.com/docs/command-r-plus',
        'command-r7b-12-2024':      'https://docs.cohere.com/docs/command-r7b',
        'command-a-03-2025':        'https://docs.cohere.com/docs/command-a',
        'command-a-vision-07-2025': 'https://docs.cohere.com/docs/command-a-vision',
    }

    MISTRAL_MODEL_URLS = {
        'mistral-large-2512':    'https://docs.mistral.ai/models/mistral-large-3-25-12',
        'mistral-large-2411':    'https://docs.mistral.ai/models/mistral-large-2-1-24-11',
        'mistral-medium-2508':   'https://docs.mistral.ai/models/mistral-medium-3-1-25-08',
        'mistral-medium-2505':   'https://docs.mistral.ai/models/mistral-medium-3-25-05',
        'mistral-small-2506':    'https://docs.mistral.ai/models/mistral-small-3-2-25-06',
        'ministral-14b-2512':    'https://docs.mistral.ai/models/ministral-3-14b-25-12',
        'ministral-8b-2512':     'https://docs.mistral.ai/models/ministral-3-8b-25-12',
        'magistral-medium-2509': 'https://docs.mistral.ai/models/magistral-medium-1-2-25-09',
        'magistral-small-2509':  'https://docs.mistral.ai/models/magistral-small-1-2-25-09',
        'pixtral-large-2411':    'https://docs.mistral.ai/models/pixtral-large-24-11',
    }

    def __init__(self, base_dir: Path, debug_browser: bool = False):
        self.base_dir = base_dir
        self.csv_path = base_dir / "benchmarks" / "benchmarks_tests.csv"
        self.pricing_path = base_dir / "scripts" / "data" / "pricing.json"
        self.debug_browser = debug_browser

        self._csv_models_cache: Optional[Dict[str, List[str]]] = None

        # LLM configuration for parsing pricing pages
        self.parsing_model = "claude-sonnet-4-6"
        self.parsing_api_key = self._get_api_key()

    def _get_api_key(self) -> Optional[str]:
        """Get Anthropic API key from environment"""
        return os.environ.get('ANTHROPIC_API_KEY')

    def _get_browser_headers(self) -> Dict[str, str]:
        """Get headers that mimic a real browser to avoid 403 blocks"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }

    def _fetch_with_playwright(self, url: str) -> Optional[str]:
        """
        Fetch URL content using playwright (headless browser)

        This bypasses anti-bot protection by using a real browser.
        Falls back to None if playwright is not available.

        Args:
            url: URL to fetch

        Returns:
            Page HTML content or None
        """
        if not PLAYWRIGHT_AVAILABLE:
            return None

        try:
            if self.debug_browser:
                print(f"    Using browser (visible mode)...")
            else:
                print(f"    Using headless browser...")
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=not self.debug_browser)
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                page = context.new_page()

                # Navigate with more lenient wait condition and longer timeout
                try:
                    page.goto(url, wait_until='domcontentloaded', timeout=60000)
                    # Give the page a bit more time to load dynamic content
                    page.wait_for_timeout(2000)
                except Exception as nav_error:
                    print(f"    ⚠️  Navigation warning: {nav_error}")
                    # Continue anyway - we might have partial content

                # Get the rendered HTML
                content = page.content()

                browser.close()
                return content if content else None

        except Exception as e:
            print(f"    ✗ Playwright error: {e}")
            return None

    def load_models_from_csv(self) -> Dict[str, List[str]]:
        """Load all non-legacy models from benchmarks_tests.csv (cached)"""
        if self._csv_models_cache is not None:
            return self._csv_models_cache

        models = {}
        with open(self.csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Skip legacy models
                if row.get('legacy_test', '').lower() == 'true':
                    continue

                provider = row['provider']
                model = row['model']

                if provider not in models:
                    models[provider] = set()
                models[provider].add(model)

        # Convert sets to sorted lists and cache
        self._csv_models_cache = {
            provider: sorted(list(model_set)) for provider, model_set in models.items()
        }
        return self._csv_models_cache

    def load_pricing_json(self) -> Dict:
        """Load existing pricing.json"""
        with open(self.pricing_path, 'r') as f:
            return json.load(f)

    def get_previous_price(self, provider: str, model: str, target_date: str) -> Optional[Dict]:
        """Find the most recent pricing entry for a model before target_date."""
        pricing_data = self.load_pricing_json()
        best_date = None
        best_entry = None
        for date_str, providers in pricing_data.get('pricing', {}).items():
            if date_str >= target_date:
                continue
            entry = providers.get(provider, {}).get(model)
            if entry and entry.get('input_price') is not None:
                if best_date is None or date_str > best_date:
                    best_date = date_str
                    best_entry = entry
        return best_entry

    def check_price_changes(self, new_pricing: Dict, target_date: str) -> None:
        """Print alerts for any price changes compared to previous pricing."""
        for provider, models in new_pricing.items():
            for model, entry in models.items():
                if entry.get('input_price') is None:
                    continue
                prev = self.get_previous_price(provider, model, target_date)
                if prev is None:
                    continue
                old_in, old_out = prev['input_price'], prev['output_price']
                new_in, new_out = entry['input_price'], entry['output_price']
                if old_in != new_in or old_out != new_out:
                    print(f"  ⚠️  PRICE CHANGE {provider}/{model}: "
                          f"${old_in}/${old_out} -> ${new_in}/${new_out}")

    def get_models_needing_pricing(self, target_date: str, force: bool = False) -> Dict[str, List[str]]:
        """Find models that need pricing for the target date

        A model needs pricing if:
        - It doesn't have pricing for the target date, AND
        - (If not forced) It doesn't have pricing within the last 30 days

        Args:
            target_date: Target date in YYYY-MM-DD format
            force: If True, include all models regardless of recent pricing
        """
        csv_models = self.load_models_from_csv()
        pricing_data = self.load_pricing_json()

        # Parse target date
        target_dt = datetime.strptime(target_date, '%Y-%m-%d')

        # Get existing pricing for target date
        existing_pricing = pricing_data.get('pricing', {}).get(target_date, {})

        models_needing_pricing = {}

        for provider, models in csv_models.items():
            provider_pricing = existing_pricing.get(provider, {})

            missing_models = []
            for model in models:
                # Skip if model already has complete pricing for target date
                if model in provider_pricing:
                    entry = provider_pricing[model]
                    if entry.get('input_price') is not None and entry.get('output_price') is not None:
                        continue

                # If force flag is set, include all models
                if force:
                    missing_models.append(model)
                    continue

                # Check if model has pricing within last 30 days
                has_recent_pricing = False
                for date_str in pricing_data.get('pricing', {}).keys():
                    try:
                        date_dt = datetime.strptime(date_str, '%Y-%m-%d')
                        days_diff = (target_dt - date_dt).days

                        # Check if this date is within 30 days before target (0-30 days ago)
                        if 0 <= days_diff <= 30:
                            provider_data = pricing_data['pricing'][date_str].get(provider, {})
                            if model in provider_data:
                                entry = provider_data[model]
                                if entry.get('input_price') is not None and entry.get('output_price') is not None:
                                    has_recent_pricing = True
                                    break
                    except ValueError:
                        # Skip dates that don't parse correctly
                        continue

                # Only add if no recent pricing found
                if not has_recent_pricing:
                    missing_models.append(model)

            if missing_models:
                models_needing_pricing[provider] = missing_models

        return models_needing_pricing

    def _parse_with_llm(self, html_content: str, provider: str,
                        expected_models: List[str], url: str,
                        additional_instructions: str = "") -> Dict[str, Dict]:
        """
        Use LLM to extract pricing from HTML content

        Args:
            html_content: Raw HTML or text from pricing page
            provider: Provider name (for context)
            expected_models: List of model names we expect to find
            url: Source URL (for reference)
            additional_instructions: Provider-specific instructions for extraction

        Returns:
            Dict of {model_name: {input_price, output_price}}
        """
        if not self.parsing_api_key:
            print("  ⚠️  No ANTHROPIC_API_KEY found in environment")
            print("      Set it to enable LLM parsing")
            return {}

        try:
            # Truncate content if too long (stay within context limits)
            max_chars = 200000
            if len(html_content) > max_chars:
                html_content = html_content[:max_chars] + "\n... (truncated)"

            provider_instructions = f"\n\n{additional_instructions}" if additional_instructions else ""

            prompt = f"""Extract pricing information from this {provider} pricing page.

Expected models (find as many as possible):
{chr(10).join(f"- {model}" for model in expected_models)}

Requirements:
1. Return ONLY valid JSON, no other text
2. Format: {{"model-name": {{"input_price": X.XX, "output_price": X.XX}}}}
3. Prices must be USD per million tokens (not per 1K)
4. Match model names flexibly (case-insensitive, ignore hyphens/spaces/dots), but OUTPUT using exact names from the expected list above
5. Only include models you find pricing for
6. If a model has the same input/output price, that's okay
7. Skip models not in the expected list{provider_instructions}

Page content:
{html_content}

Return only JSON:"""

            # Call Anthropic API
            api_response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.parsing_api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.parsing_model,
                    "max_tokens": 4096,
                    "system": "You are a precise data extraction assistant. Return only valid JSON.",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0
                },
                timeout=60
            )

            if api_response.status_code != 200:
                print(f"  ✗ LLM API error: {api_response.status_code}: {api_response.text[:200]}")
                return {}

            # Extract and parse response
            response_json = api_response.json()
            content = response_json['content'][0]['text']

            # Strip markdown code fences if present (e.g. ```json ... ```)
            content = content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[-1]
                content = content.rsplit("```", 1)[0].strip()

            pricing = json.loads(content)

            # Validate structure
            if not isinstance(pricing, dict):
                print(f"  ✗ LLM returned invalid format")
                return {}

            print(f"  ✓ LLM extracted {len(pricing)} models")
            return pricing

        except json.JSONDecodeError as e:
            print(f"  ✗ LLM returned invalid JSON: {e}")
            return {}
        except Exception as e:
            print(f"  ✗ LLM parsing error: {e}")
            return {}

    def _validate_pricing(self, pricing: Dict[str, Dict],
                         expected_models: List[str],
                         provider: str) -> bool:
        """
        Validate LLM-extracted pricing

        Args:
            pricing: Dict of {model: {input_price, output_price}}
            expected_models: List of models we expected to find
            provider: Provider name (for logging)

        Returns:
            True if validation passes
        """
        if not pricing:
            print(f"    ✗ No pricing data extracted")
            return False

        # Check structure
        for model, data in pricing.items():
            if not isinstance(data, dict):
                print(f"    ✗ Invalid structure for {model}")
                return False

            if 'input_price' not in data or 'output_price' not in data:
                print(f"    ✗ Missing price fields for {model}")
                return False

            # Check prices are positive numbers
            try:
                input_price = float(data['input_price'])
                output_price = float(data['output_price'])

                if input_price <= 0 or output_price <= 0:
                    print(f"    ✗ Invalid price for {model}: ${input_price}/${output_price}")
                    return False

                # Sanity check: prices should be reasonable (< $1000/M tokens)
                if input_price > 1000 or output_price > 1000:
                    print(f"    ⚠️  Suspiciously high price for {model}: ${input_price}/${output_price}")
                    # Don't fail, but warn

            except (ValueError, TypeError):
                print(f"    ✗ Non-numeric price for {model}")
                return False

        # Check coverage
        found = set(pricing.keys())
        expected = set(expected_models)
        matched = found & expected
        coverage = len(matched) / len(expected) if expected else 0

        print(f"    Coverage: {len(matched)}/{len(expected)} models ({coverage:.0%})")

        if coverage < 0.5:  # Less than 50% coverage
            print(f"    ✗ Low coverage: only found {coverage:.0%} of expected models")
            return False

        # Log unmatched
        unmatched = expected - found
        if unmatched:
            print(f"    ℹ️  Not found: {', '.join(sorted(unmatched))}")

        return True

    # Domains that require a full browser (JS-rendered pricing tables)
    BROWSER_REQUIRED_DOMAINS = {'docs.mistral.ai'}  # Domains that require JS rendering

    def _fetch_page_content(self, url: str) -> Optional[str]:
        """Fetch a URL as plain text, using headless browser for JS-heavy sites"""
        # Some sites render pricing via JS — go straight to browser
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.lstrip('www.')
        if domain in self.BROWSER_REQUIRED_DOMAINS:
            if PLAYWRIGHT_AVAILABLE:
                html_content = self._fetch_with_playwright(url)
                if html_content:
                    soup = BeautifulSoup(html_content, 'html.parser')
                    return soup.get_text(separator='\n', strip=True)
                print(f"    ✗ Headless browser returned empty content")
            else:
                print(f"    ⚠️  Playwright required for {domain} but not available")
                print(f"        Install with: pip install playwright && playwright install chromium")
            return None

        try:
            response = requests.get(url, headers=self._get_browser_headers(), timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup.get_text(separator='\n', strip=True)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                print(f"    ✗ 403 Forbidden - trying headless browser...")
                if PLAYWRIGHT_AVAILABLE:
                    html_content = self._fetch_with_playwright(url)
                    if html_content:
                        soup = BeautifulSoup(html_content, 'html.parser')
                        return soup.get_text(separator='\n', strip=True)
                    print(f"    ✗ Headless browser returned empty content")
                else:
                    print(f"    ⚠️  Playwright not available")
                    print(f"        Install with: pip install playwright")
                    print(f"        Then run: playwright install chromium")
            else:
                print(f"    ✗ HTTP error: {e.response.status_code}")
            return None

    def _scrape_single_page(self, url: str, provider: str,
                            models: Optional[List[str]] = None,
                            additional_instructions: str = "") -> Dict[str, Dict]:
        """Fetch a single pricing page and extract models using LLM

        Args:
            models: Specific models to look for. If None, uses all from CSV.
        """
        if not SCRAPING_AVAILABLE:
            return {}

        try:
            expected_models = models
            if expected_models is None:
                csv_models = self.load_models_from_csv()
                expected_models = csv_models.get(provider, [])

            if not expected_models:
                print(f"  ⚠️  No {provider} models found in CSV")
                return {}

            print(f"  Fetching {url}...")
            content = self._fetch_page_content(url)

            if not content:
                print(f"  ✗ Could not fetch page content")
                return {}

            print(f"  Parsing with {self.parsing_model}...")
            pricing = self._parse_with_llm(
                html_content=content,
                provider=provider,
                expected_models=expected_models,
                url=url,
                additional_instructions=additional_instructions
            )

            if not self._validate_pricing(pricing, expected_models, provider):
                print(f"  ✗ Validation failed")
                return {}

            print(f"  ✓ Successfully parsed {provider} pricing")
            return pricing

        except Exception as e:
            print(f"  ✗ Error scraping {provider}: {e}")
            return {}

    def scrape_openai_pricing(self, models: Optional[List[str]] = None) -> Dict[str, Dict]:
        """Scrape OpenAI pricing page"""
        return self._scrape_single_page(
            url="https://platform.openai.com/docs/pricing",
            provider="openai",
            models=models,
            additional_instructions=(
                "IMPORTANT: Use the 'Standard' rate for input and output prices. "
                "Ignore Batch API rates, Cached rates, and any other rate types."
            )
        )

    def scrape_anthropic_pricing(self, models: Optional[List[str]] = None) -> Dict[str, Dict]:
        """Scrape Anthropic pricing page"""
        return self._scrape_single_page(
            url="https://www.anthropic.com/pricing",
            provider="anthropic",
            models=models,
            additional_instructions=(
                "IMPORTANT: Use the standard API input and output prices. "
                "Ignore Batch API rates, Prompt Caching rates, and any other rate types."
            )
        )

    def scrape_genai_pricing(self, models: Optional[List[str]] = None) -> Dict[str, Dict]:
        """Scrape Google GenAI pricing page"""
        return self._scrape_single_page(
            url="https://ai.google.dev/gemini-api/docs/pricing",
            provider="genai",
            models=models,
            additional_instructions=(
                "IMPORTANT: Use the standard (paid) input and output prices for text. "
                "Ignore free tier rates and batch rates."
            )
        )

    def scrape_mistral_pricing(self, models: Optional[List[str]] = None) -> Dict[str, Dict]:
        """Scrape Mistral pricing — each model has its own doc page"""
        if not SCRAPING_AVAILABLE:
            return {}

        expected_models = models
        if expected_models is None:
            csv_models = self.load_models_from_csv()
            expected_models = csv_models.get('mistral', [])

        all_pricing: Dict[str, Dict] = {}

        for model in expected_models:
            url = self.MISTRAL_MODEL_URLS.get(model)
            if not url:
                print(f"  ⚠️  No URL known for {model}, skipping")
                continue

            try:
                print(f"  Fetching {url}...")
                content = self._fetch_page_content(url)

                if not content:
                    print(f"  ✗ Could not fetch page for {model}")
                    continue

                print(f"  Parsing {model}...")
                pricing = self._parse_with_llm(
                    html_content=content,
                    provider="mistral",
                    expected_models=[model],
                    url=url,
                    additional_instructions=(
                        "IMPORTANT: Use the standard API input and output prices. "
                        "Ignore batch/async rates."
                    )
                )

                if model in pricing:
                    data = pricing[model]
                    try:
                        inp = float(data.get('input_price', -1))
                        out = float(data.get('output_price', -1))
                        if inp <= 0 or out <= 0:
                            print(f"  ✗ Invalid prices for {model}: ${inp}/${out}")
                            continue
                        if inp > 1000 or out > 1000:
                            print(f"  ⚠️  Suspiciously high price for {model}: ${inp}/${out}")
                    except (ValueError, TypeError):
                        print(f"  ✗ Non-numeric price for {model}")
                        continue
                    all_pricing[model] = data
                    print(f"  ✓ {model}: ${data['input_price']} / ${data['output_price']}")
                else:
                    print(f"  ✗ Could not extract pricing for {model}")

            except Exception as e:
                print(f"  ✗ Error fetching {model}: {e}")

        return all_pricing

    def scrape_cohere_pricing(self, models: Optional[List[str]] = None) -> Dict[str, Dict]:
        """Scrape Cohere pricing — each model has its own doc page

        Args:
            models: Specific models to look for. If None, uses all from CSV.
        """
        if not SCRAPING_AVAILABLE:
            return {}

        expected_models = models
        if expected_models is None:
            csv_models = self.load_models_from_csv()
            expected_models = csv_models.get('cohere', [])

        all_pricing: Dict[str, Dict] = {}

        for model in expected_models:
            url = self.COHERE_MODEL_URLS.get(model)
            if not url:
                print(f"  ⚠️  No URL known for {model}, skipping")
                continue

            try:
                print(f"  Fetching {url}...")
                content = self._fetch_page_content(url)

                if not content:
                    print(f"  ✗ Could not fetch page for {model}")
                    continue

                print(f"  Parsing {model}...")
                pricing = self._parse_with_llm(
                    html_content=content,
                    provider="cohere",
                    expected_models=[model],
                    url=url,
                    additional_instructions=(
                        "IMPORTANT: Use the standard API input and output prices. "
                        "Ignore batch rates."
                    )
                )

                if model in pricing:
                    data = pricing[model]
                    # Validate structure and price ranges
                    try:
                        inp = float(data.get('input_price', -1))
                        out = float(data.get('output_price', -1))
                        if inp <= 0 or out <= 0:
                            print(f"  ✗ Invalid prices for {model}: ${inp}/${out}")
                            continue
                        if inp > 1000 or out > 1000:
                            print(f"  ⚠️  Suspiciously high price for {model}: ${inp}/${out}")
                    except (ValueError, TypeError):
                        print(f"  ✗ Non-numeric price for {model}")
                        continue
                    all_pricing[model] = data
                    print(f"  ✓ {model}: ${data['input_price']} / ${data['output_price']}")
                else:
                    print(f"  ✗ Could not extract pricing for {model}")

            except Exception as e:
                print(f"  ✗ Error fetching {model}: {e}")

        return all_pricing

    def scrape_openrouter_pricing(self, models: List[str]) -> Dict[str, Dict]:
        """Fetch OpenRouter pricing via their models API"""
        if not SCRAPING_AVAILABLE:
            return {}

        try:
            url = "https://openrouter.ai/api/v1/models"
            print(f"  Fetching {url}...")
            response = requests.get(url, headers=self._get_browser_headers(), timeout=15)
            response.raise_for_status()

            data = response.json()
            model_list = data.get('data', [])

            # Build lookup: model_id -> pricing
            api_pricing = {}
            for entry in model_list:
                model_id = entry.get('id', '')
                pricing = entry.get('pricing', {})
                prompt_price = pricing.get('prompt')
                completion_price = pricing.get('completion')
                if prompt_price is not None and completion_price is not None:
                    try:
                        # OpenRouter prices are per token — convert to per million
                        api_pricing[model_id] = {
                            'input_price': round(float(prompt_price) * 1_000_000, 6),
                            'output_price': round(float(completion_price) * 1_000_000, 6),
                        }
                    except (ValueError, TypeError):
                        pass

            result = {}
            for model in models:
                if model in api_pricing:
                    result[model] = api_pricing[model]
                    print(f"  ✓ {model}: ${result[model]['input_price']} / ${result[model]['output_price']}")
                else:
                    print(f"  ✗ {model} not found in OpenRouter API")

            return result

        except Exception as e:
            print(f"  ✗ Error fetching OpenRouter pricing: {e}")
            return {}

    # Maps provider -> base URL for single-page providers
    PROVIDER_URLS = {
        'openai':    'https://platform.openai.com/docs/pricing',
        'anthropic': 'https://www.anthropic.com/pricing',
        'genai':     'https://ai.google.dev/gemini-api/docs/pricing',
    }

    def get_source_url(self, provider: str, model: str) -> str:
        """Return the raw source URL for a given provider/model."""
        if provider in self.PROVIDER_URLS:
            return self.PROVIDER_URLS[provider]
        elif provider == 'cohere':
            return self.COHERE_MODEL_URLS.get(model, "")
        elif provider == 'mistral':
            return self.MISTRAL_MODEL_URLS.get(model, "")
        elif provider == 'openrouter':
            return f"https://openrouter.ai/{model}"
        return ""

    def scrape_pricing(self, provider: str, models: List[str]) -> Dict[str, Dict]:
        """
        Scrape pricing for a specific provider.

        Returns only {model: {input_price, output_price}}.
        source_url and added are set by the caller.

        Args:
            provider: Provider name
            models: List of models needing pricing

        Returns:
            Dict of {model: {input_price, output_price}}
        """
        scraper_map = {
            'openai':    self.scrape_openai_pricing,
            'anthropic': self.scrape_anthropic_pricing,
            'genai':     self.scrape_genai_pricing,
            'mistral':   self.scrape_mistral_pricing,
            'cohere':    self.scrape_cohere_pricing,
        }

        if provider in scraper_map:
            return scraper_map[provider](models=models)
        elif provider == 'openrouter':
            return self.scrape_openrouter_pricing(models)
        else:
            print(f"  No scraper available for {provider}")
            return {}

    def create_manual_entry_template(self) -> Dict:
        """Create a template entry for manual pricing input"""
        return {
            "input_price": None,  # FILL IN - null indicates missing data
            "output_price": None,  # FILL IN - null indicates missing data
        }

    def _get_todays_snapshot(self, url: str) -> Optional[str]:
        """Check Wayback Machine CDX API for a snapshot of url from today"""
        try:
            today = datetime.now().strftime('%Y%m%d')
            cdx_url = (
                f"https://web.archive.org/cdx/search/cdx"
                f"?url={url}&output=json&limit=1&fl=timestamp"
                f"&filter=statuscode:200&from={today}"
            )
            response = requests.get(cdx_url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if len(data) > 1:  # First row is the header
                    timestamp = data[1][0]
                    return f"https://web.archive.org/web/{timestamp}/{url}"
        except Exception:
            pass
        return None

    def archive_url(self, url: str) -> Optional[str]:
        """Return an archive.org URL for url, using an existing snapshot or saving a new one"""
        if not SCRAPING_AVAILABLE:
            return None

        # Use today's snapshot if one already exists (avoids save rate limits)
        today = self._get_todays_snapshot(url)
        if today:
            print(f"  Using today's snapshot: {today}")
            return today

        # No recent snapshot — try to save a new one
        save_url = f"https://web.archive.org/save/{url}"
        max_retries = 3

        for attempt in range(max_retries):
            try:
                # Don't follow redirects — Content-Location is on the initial response
                response = requests.get(
                    save_url,
                    headers=self._get_browser_headers(),
                    timeout=60,
                    allow_redirects=False
                )

                if response.status_code in (200, 302):
                    archive_path = (
                        response.headers.get('Content-Location') or
                        response.headers.get('Location')
                    )
                    if archive_path:
                        if not archive_path.startswith('http'):
                            archive_path = f"https://web.archive.org{archive_path}"
                        return archive_path
                    print(f"  Warning: Archived but no URL returned for {url}")
                    return None

                elif response.status_code == 429:
                    wait = 10 * (attempt + 1)
                    print(f"  Rate limited by Wayback Machine, retrying in {wait}s...")
                    time.sleep(wait)
                    continue

                else:
                    print(f"  Warning: Could not archive {url} (status: {response.status_code})")
                    return None

            except Exception as e:
                print(f"  Error archiving {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)
                    continue
                return None

        print(f"  Warning: Failed to archive {url} after {max_retries} attempts")
        return None

    def archive_urls_parallel(self, urls: set) -> Dict[str, str]:
        """Archive a set of URLs in parallel.

        Args:
            urls: Set of raw URLs to archive

        Returns:
            Dict mapping raw_url -> archived_url for successful archives
        """
        if not urls:
            return {}

        print(f"\nArchiving {len(urls)} unique source URLs in parallel...")
        archived_map: Dict[str, str] = {}

        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_url = {
                executor.submit(self.archive_url, url): url
                for url in urls
            }

            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    if result:
                        archived_map[url] = result
                        print(f"  Archived: {url}")
                    else:
                        print(f"  Failed:   {url}")
                        print(f"    MANUAL: https://web.archive.org/save/{url}")
                except Exception as e:
                    print(f"  Error archiving {url}: {e}")

        print(f"Archived {len(archived_map)}/{len(urls)} URLs")
        return archived_map

    def generate_pricing_update(self, target_date: str, force: bool = False) -> Dict:
        """Generate pricing updates for the target date

        Args:
            target_date: Target date in YYYY-MM-DD format
            force: If True, update all models regardless of recent pricing
        """
        models_needing_pricing = self.get_models_needing_pricing(target_date, force=force)

        if not models_needing_pricing:
            print("✓ All non-legacy models have pricing for this date!")
            if not force:
                print("  (or have pricing within the last 30 days)")
            return {}

        print(f"\nModels needing pricing for {target_date}:")
        if force:
            print("(--force enabled: updating ALL models)")
        else:
            print("(Models with pricing within the last 30 days are skipped)")
        for provider, models in models_needing_pricing.items():
            print(f"  {provider}: {', '.join(models)}")

        print("\nAttempting to scrape pricing data...")
        new_pricing = {}

        for provider, models in models_needing_pricing.items():
            print(f"\n{provider}:")
            scraped = self.scrape_pricing(provider, models)

            if scraped:
                # Only keep models that actually needed pricing
                needed = set(models)
                new_pricing[provider] = {
                    m: v for m, v in scraped.items() if m in needed
                }
            else:
                # Create manual entry templates
                print(f"  Creating manual entry templates for {len(models)} models")
                new_pricing[provider] = {}
                for model in models:
                    new_pricing[provider][model] = self.create_manual_entry_template()

        return new_pricing

    def show_diff(self, original: str, updated: str) -> None:
        """Show a colored diff between original and updated JSON"""
        original_lines = original.splitlines(keepends=True)
        updated_lines = updated.splitlines(keepends=True)

        diff = difflib.unified_diff(
            original_lines,
            updated_lines,
            fromfile='pricing.json (current)',
            tofile='pricing.json (updated)',
            lineterm=''
        )

        print("\n" + "=" * 70)
        print("PROPOSED CHANGES:")
        print("=" * 70)
        for line in diff:
            print(line.rstrip())
        print("=" * 70)

    def update_pricing_json(self, target_date: str, new_pricing: Dict, dry_run: bool = False) -> Optional[Dict]:
        """Merge new pricing into pricing data, show diff, and confirm.

        Does NOT write to disk — caller is responsible for writing.

        Returns:
            Merged pricing_data dict if confirmed (or dry-run), None if declined.
        """
        pricing_data = self.load_pricing_json()

        # Ensure target date exists
        if target_date not in pricing_data['pricing']:
            pricing_data['pricing'][target_date] = {}

        # Merge new pricing
        for provider, models in new_pricing.items():
            if provider not in pricing_data['pricing'][target_date]:
                pricing_data['pricing'][target_date][provider] = {}

            for model, pricing_info in models.items():
                pricing_data['pricing'][target_date][provider][model] = pricing_info

        # Update metadata
        pricing_data['metadata']['last_updated'] = target_date
        old_version = pricing_data['metadata'].get('version', '1.0')
        major, minor = old_version.split('.')
        pricing_data['metadata']['version'] = f"{major}.{int(minor) + 1}"

        # Generate JSON strings for diff
        original_json = json.dumps(self.load_pricing_json(), indent=2)
        updated_json = json.dumps(pricing_data, indent=2)

        # Show diff
        self.show_diff(original_json, updated_json)

        if dry_run:
            print("\n🔍 DRY RUN: No changes written to file")
            return pricing_data

        # Ask for confirmation
        print("\n⚠️  Review the changes above.")
        print("Note: Manual entry templates (with null prices) need to be filled in.")
        response = input("Apply these changes? (yes/no): ").strip().lower()

        if response == 'yes':
            return pricing_data
        else:
            print("❌ Changes not applied")
            return None


def main():
    parser = argparse.ArgumentParser(
        description='Semi-automated pricing updater for pricing.json',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Update pricing for today's date:
    python scripts/update_pricing.py --date 2026-02-10

  Dry run (show changes without applying):
    python scripts/update_pricing.py --date 2026-02-10 --dry-run

  Force update all models (ignore 30-day rule):
    python scripts/update_pricing.py --date 2026-02-10 --force
        """
    )
    parser.add_argument('--date', required=True, help='Target date (YYYY-MM-DD)')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without applying')
    parser.add_argument('--force', action='store_true',
                        help='Update all models, ignoring 30-day pricing cache')
    parser.add_argument('--debug-browser', action='store_true',
                        help='Run browser in visible mode for debugging')

    args = parser.parse_args()

    # Validate date format
    try:
        datetime.strptime(args.date, '%Y-%m-%d')
    except ValueError:
        print(f"❌ Error: Invalid date format '{args.date}'. Use YYYY-MM-DD")
        sys.exit(1)

    base_dir = Path(__file__).parent.parent
    updater = PricingUpdater(base_dir, debug_browser=args.debug_browser)

    print("=" * 70)
    print(f"Pricing Updater for {args.date}")
    if args.force:
        print("Mode: FORCE (updating all models)")
    print("=" * 70)

    # Generate pricing updates
    new_pricing = updater.generate_pricing_update(args.date, force=args.force)

    if not new_pricing:
        return

    # Collect unique raw URLs that need archiving
    raw_urls = set()
    for provider, models in new_pricing.items():
        for model in models:
            url = updater.get_source_url(provider, model)
            if url:
                raw_urls.add(url)

    # Archive source URLs in parallel
    archived_map = updater.archive_urls_parallel(raw_urls)

    # Set source_url and added on each model entry (once)
    for provider, models in new_pricing.items():
        for model, entry in models.items():
            raw_url = updater.get_source_url(provider, model)
            entry['source_url'] = archived_map.get(raw_url, raw_url)
            entry['added'] = args.date

    # Alert on price changes vs previous data
    updater.check_price_changes(new_pricing, args.date)

    # Show diff and get confirmation (does not write to disk)
    pricing_data = updater.update_pricing_json(args.date, new_pricing, dry_run=args.dry_run)

    if pricing_data is None:
        return

    # Write pricing.json once
    if args.dry_run:
        print("\n🔍 DRY RUN: No changes written to file")
    else:
        with open(updater.pricing_path, 'w') as f:
            json.dump(pricing_data, f, indent=2)
        print(f"\n✅ Updated {updater.pricing_path}")
        print("\n💡 Next steps:")
        print("   1. Fill in any manual entry templates (search for 'null' prices)")
        print("   2. Verify source_url fields are correct")
        print("   3. Run tests to ensure pricing lookups work")


if __name__ == '__main__':
    main()
