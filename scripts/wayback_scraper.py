#!/usr/bin/env python3
"""Simple Wayback Machine pricing scraper."""

import requests
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class WaybackScraper:
    """Simple Wayback Machine scraper for pricing data."""

    def __init__(self):
        """Initialize scraper."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Humanities Benchmark Pricing Scraper'
        })

        # Provider pricing URLs
        self.provider_urls = {
            'openai': 'https://platform.openai.com/docs/pricing',
            'anthropic': 'https://docs.claude.com/en/docs/about-claude/pricing',
            'genai': 'https://ai.google.dev/gemini-api/docs/pricing',
            'mistral': 'https://mistral.ai/pricing#api-pricing'
        }

    def get_snapshots(self, url: str, date: str) -> List[str]:
        """Get Wayback Machine snapshots for URL around date."""
        try:
            # Query CDX API for snapshots
            cdx_url = "http://web.archive.org/cdx/search/cdx"
            params = {
                'url': url,
                'from': date.replace('-', ''),
                'to': date.replace('-', ''),
                'output': 'json',
                'fl': 'timestamp'
            }

            response = self.session.get(cdx_url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if len(data) > 1:  # Skip header row
                    timestamps = [row[0] for row in data[1:]]
                    return [f"http://web.archive.org/web/{ts}/{url}" for ts in timestamps]

        except Exception as e:
            logging.error(f"Error getting snapshots for {url}: {e}")

        return []

    def fetch_content(self, url: str) -> Optional[str]:
        """Fetch content from URL (both live and Wayback Machine URLs)."""
        try:
            # Use enhanced headers for live URLs to avoid bot detection
            headers = {}
            if not url.startswith('http://web.archive.org/'):
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                    'Sec-Ch-Ua-Mobile': '?0',
                    'Sec-Ch-Ua-Platform': '"macOS"',
                }

            # For live URLs, try multiple strategies if first attempt fails
            if not url.startswith('http://web.archive.org/'):
                # Strategy 1: Enhanced browser headers
                response = self.session.get(url, headers=headers, timeout=60, allow_redirects=True)
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 403:
                    logging.info(f"First attempt got 403 for {url}, trying alternative approaches...")

                    # Strategy 2: Clear session and try again with different headers
                    import time
                    import requests
                    time.sleep(2)  # Brief delay

                    alt_session = requests.Session()
                    alt_headers = {
                        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                    }

                    response = alt_session.get(url, headers=alt_headers, timeout=60, allow_redirects=True)
                    alt_session.close()

                    if response.status_code == 200:
                        return response.text
                    else:
                        logging.warning(f"403 Forbidden when fetching {url} - site may be blocking bot access")
                        return None
                else:
                    logging.warning(f"HTTP {response.status_code} when fetching {url}")
                    return None
            else:
                # For Wayback Machine URLs, use simpler approach
                response = self.session.get(url, headers=headers, timeout=60)
                if response.status_code == 200:
                    return response.text
                else:
                    logging.warning(f"HTTP {response.status_code} when fetching Wayback URL {url}")
                    return None

        except Exception as e:
            logging.error(f"Error fetching {url}: {e}")

        return None

    def save_to_wayback(self, url: str) -> Optional[str]:
        """Save a URL to Wayback Machine and return the archive URL."""
        try:
            # Submit URL to Wayback Machine for archiving
            save_url = "https://web.archive.org/save/"
            response = self.session.get(save_url + url, timeout=30)

            if response.status_code == 200:
                # Extract the archived URL from the response
                # The Wayback Machine typically redirects to the archived version
                archived_url = response.url
                if "web.archive.org/web/" in archived_url:
                    logging.info(f"Successfully saved {url} to Wayback Machine: {archived_url}")
                    return archived_url
                else:
                    # Try to construct the URL based on current timestamp
                    from datetime import datetime
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    archived_url = f"http://web.archive.org/web/{timestamp}/{url}"
                    logging.info(f"Constructed Wayback URL: {archived_url}")
                    return archived_url
            else:
                logging.warning(f"Failed to save to Wayback Machine: {response.status_code}")

        except Exception as e:
            logging.error(f"Error saving to Wayback Machine: {e}")

        return None

    def extract_pricing_with_ai(self, html: str, provider: str) -> Dict[str, Tuple[float, float]]:
        """Extract pricing using AI API."""
        try:
            from simple_ai_clients import AiApiClient
            import os

            # Get OpenAI API key for parsing
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                logging.error("No OpenAI API key found for pricing extraction")
                return {}

            client = AiApiClient('openai', api_key)
            client.init_client()

            # Disable cost calculation to avoid circular dependency
            client.calculate_cost = False

            # Extract text content from HTML using regex (simple approach)
            text = re.sub(r'<[^>]+>', ' ', html)  # Remove HTML tags
            text = ' '.join(text.split())  # Normalize whitespace

            # Define expected models for each provider (from benchmarks_tests.csv)
            expected_models = {
                'openai': [
                    'gpt-4.1', 'gpt-4.1-mini', 'gpt-4.1-nano', 'gpt-4.5-preview',
                    'gpt-4o', 'gpt-4o-mini', 'gpt-5', 'gpt-5-mini', 'gpt-5-nano', 'o3'
                ],
                'genai': [
                    'gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-2.0-flash', 'gemini-2.0-flash-lite',
                    'gemini-2.0-pro-exp-02-05', 'gemini-2.5-flash', 'gemini-2.5-flash-lite',
                    'gemini-2.5-flash-lite-preview-09-2025', 'gemini-2.5-flash-preview-04-17',
                    'gemini-2.5-flash-preview-09-2025', 'gemini-2.5-pro', 'gemini-2.5-pro-exp-03-25',
                    'gemini-2.5-pro-preview-05-06', 'gemini-exp-1206'
                ],
                'mistral': [
                    'mistral-large-latest', 'mistral-medium-2505', 'mistral-medium-2508',
                    'pixtral-12b', 'pixtral-large-latest'
                ],
                'anthropic': [
                    'claude-3-5-haiku-20241022', 'claude-3-5-sonnet-20241022', 'claude-3-7-sonnet-20250219',
                    'claude-3-opus-20240229', 'claude-opus-4-1-20250805', 'claude-opus-4-20250514',
                    'claude-sonnet-4-20250514'
                ]
            }

            models_to_find = expected_models.get(provider, [])

            prompt = f"""Extract pricing information from the following {provider} pricing page content.

Look for these specific models: {', '.join(models_to_find)}

For each model found, extract:
- Input token price per 1M tokens (in USD)
- Output token price per 1M tokens (in USD)

Return the results in this exact JSON format:
{{
  "model_name": {{"input_price": X.XX, "output_price": Y.YY}},
  "model_name2": {{"input_price": X.XX, "output_price": Y.YY}}
}}

If a model is not found or pricing is unclear, don't include it. But note that sometimes a model falls under an 
umbrella term, for example, the pricing for 'claude-opus-4-1-20250805' might be found under "Claude Opus 4.1".
Only return valid JSON, no explanations, no mapping.

Page content:
{text}"""

            # Make API request
            response = client.prompt("gpt-4.1", prompt)

            if 'response_text' in response and response['response_text']:
                import json
                try:
                    ai_response = response['response_text'].strip()
                    logging.info(f"AI response for {provider} pricing: {ai_response[:200]}...")

                    # Try to parse the JSON response
                    pricing_data = json.loads(ai_response)

                    # Convert to expected format
                    models = {}
                    for model_name, prices in pricing_data.items():
                        if isinstance(prices, dict) and 'input_price' in prices and 'output_price' in prices:
                            models[model_name] = (float(prices['input_price']), float(prices['output_price']))

                    if models:
                        logging.info(f"AI extracted pricing for {provider}: {models}")
                        return models
                    else:
                        logging.warning(f"AI response parsed but no valid models found for {provider}")

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logging.error(f"Error parsing AI response for {provider}: {e}")
                    logging.error(f"Full AI response was: {response['response_text']}")

                    # No fallback - return empty
                    return {}

            else:
                logging.error(f"No response_text in AI response for {provider}: {response}")

        except Exception as e:
            logging.error(f"Error using AI to extract {provider} pricing: {e}")

        return {}

    def parse_openai_pricing(self, html: str) -> Dict[str, Tuple[float, float]]:
        """Parse OpenAI pricing from HTML using AI."""
        return self.extract_pricing_with_ai(html, 'openai')

    def parse_genai_pricing(self, html: str) -> Dict[str, Tuple[float, float]]:
        """Parse GenAI pricing from HTML using AI."""
        return self.extract_pricing_with_ai(html, 'genai')

    def parse_mistral_pricing(self, html: str) -> Dict[str, Tuple[float, float]]:
        """Parse Mistral pricing from HTML using AI."""
        return self.extract_pricing_with_ai(html, 'mistral')

    def parse_anthropic_pricing(self, html: str) -> Dict[str, Tuple[float, float]]:
        """Parse Anthropic pricing from HTML using AI."""
        return self.extract_pricing_with_ai(html, 'anthropic')

    def find_available_snapshots(self, url: str, start_date: str, days_back: int = 365) -> List[str]:
        """Find snapshots by searching backwards from start_date."""
        from datetime import datetime, timedelta

        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            logging.error(f"Invalid date format: {start_date}")
            return []

        # Try the original date first
        snapshots = self.get_snapshots(url, start_date)
        if snapshots:
            logging.info(f"Found snapshots for original date {start_date}")
            return snapshots

        # Search backwards day by day
        for days in range(1, days_back + 1):
            search_date = start_dt - timedelta(days=days)
            search_date_str = search_date.strftime('%Y-%m-%d')

            logging.info(f"Trying date {search_date_str} ({days} days back)")
            snapshots = self.get_snapshots(url, search_date_str)
            if snapshots:
                logging.info(f"Found snapshots for date {search_date_str}")
                return snapshots

        logging.warning(f"No snapshots found within {days_back} days of {start_date}")
        return []

    def scrape_pricing(self, provider: str, date: str) -> Dict[str, Tuple[float, float, str]]:
        """
        Scrape pricing for provider on date.

        Returns:
            Dict[model_name, (input_price, output_price, wayback_url)]
        """
        if provider not in self.provider_urls:
            logging.error(f"Unknown provider: {provider}")
            return {}

        url = self.provider_urls[provider]
        logging.info(f"Scraping {provider} pricing for {date}")

        # For current date, try fetching from live site first
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')

        if date == today:
            logging.info(f"Date is today ({today}), fetching current pricing and saving to Wayback Machine")
            try:
                # Fetch current content
                current_content = self.fetch_content(url)
                if current_content:
                    # Parse the content
                    if provider == 'openai':
                        models = self.parse_openai_pricing(current_content)
                    elif provider == 'genai':
                        models = self.parse_genai_pricing(current_content)
                    elif provider == 'mistral':
                        models = self.parse_mistral_pricing(current_content)
                    elif provider == 'anthropic':
                        models = self.parse_anthropic_pricing(current_content)
                    else:
                        models = {}

                    if models:
                        # Save current page to Wayback Machine to get a proper source URL
                        wayback_url = self.save_to_wayback(url)
                        if not wayback_url:
                            # Fallback: construct expected Wayback URL
                            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                            wayback_url = f"http://web.archive.org/web/{timestamp}/{url}"

                        logging.info(f"Successfully extracted current pricing for {provider}: {models}")
                        return {model: (input_p, output_p, wayback_url)
                               for model, (input_p, output_p) in models.items()}
                    else:
                        logging.warning(f"No models extracted from current {provider} pricing page")
                else:
                    logging.warning(f"No content retrieved from current {provider} pricing page")
            except Exception as e:
                logging.error(f"Error fetching current pricing: {e}")

            # If current pricing failed for today's date, fall back to recent historical snapshots
            logging.warning(f"Could not get current pricing for {provider} on today's date, falling back to recent historical snapshots")

        # Find snapshots, searching backwards if needed
        snapshots = self.find_available_snapshots(url, date)
        if not snapshots:
            logging.warning(f"No snapshots found for {provider} within search range")
            return {}

        logging.info(f"Found {len(snapshots)} snapshots for {provider}")

        # Try each snapshot until we get pricing data
        for snapshot_url in snapshots[:3]:  # Try up to 3 snapshots
            logging.info(f"Trying snapshot: {snapshot_url}")
            content = self.fetch_content(snapshot_url)
            if not content:
                logging.warning(f"No content retrieved from {snapshot_url}")
                continue

            # Parse based on provider
            if provider == 'openai':
                models = self.parse_openai_pricing(content)
            elif provider == 'genai':
                models = self.parse_genai_pricing(content)
            elif provider == 'mistral':
                models = self.parse_mistral_pricing(content)
            elif provider == 'anthropic':
                models = self.parse_anthropic_pricing(content)
            else:
                logging.warning(f"No parser for {provider}")
                continue

            logging.info(f"Extracted models: {models}")

            # Add snapshot URL to results
            if models:
                return {model: (input_p, output_p, snapshot_url)
                       for model, (input_p, output_p) in models.items()}

        # If no snapshots worked, try current pricing as fallback
        if date >= "2025-09-01":  # For recent dates, try current pricing
            logging.info(f"No historical snapshots found for {date}, trying current pricing")
            try:
                # Try fetching current pricing page directly
                current_content = self.fetch_content(self.provider_urls[provider])
                if current_content:
                    if provider == 'openai':
                        models = self.parse_openai_pricing(current_content)
                    elif provider == 'genai':
                        models = self.parse_genai_pricing(current_content)
                    elif provider == 'mistral':
                        models = self.parse_mistral_pricing(current_content)
                    elif provider == 'anthropic':
                        models = self.parse_anthropic_pricing(current_content)
                    else:
                        models = {}

                    if models:
                        return {model: (input_p, output_p, f"{self.provider_urls[provider]} (current pricing)")
                               for model, (input_p, output_p) in models.items()}
            except Exception as e:
                logging.error(f"Error fetching current pricing: {e}")


        # No pricing data found - add entries with None prices for manual intervention
        logging.warning(f"No pricing data extracted for {provider} on {date}, adding None entries for manual intervention")

        expected_models = {
            'openai': [
                'gpt-4.1', 'gpt-4.1-mini', 'gpt-4.1-nano', 'gpt-4.5-preview',
                'gpt-4o', 'gpt-4o-mini', 'gpt-5', 'gpt-5-mini', 'gpt-5-nano', 'o3'
            ],
            'genai': [
                'gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-2.0-flash', 'gemini-2.0-flash-lite',
                'gemini-2.0-pro-exp-02-05', 'gemini-2.5-flash', 'gemini-2.5-flash-lite',
                'gemini-2.5-flash-lite-preview-09-2025', 'gemini-2.5-flash-preview-04-17',
                'gemini-2.5-flash-preview-09-2025', 'gemini-2.5-pro', 'gemini-2.5-pro-exp-03-25',
                'gemini-2.5-pro-preview-05-06', 'gemini-exp-1206'
            ],
            'mistral': [
                'mistral-large-latest', 'mistral-medium-2505', 'mistral-medium-2508',
                'pixtral-12b', 'pixtral-large-latest'
            ],
            'anthropic': [
                'claude-3-5-haiku-20241022', 'claude-3-5-sonnet-20241022', 'claude-3-7-sonnet-20250219',
                'claude-3-opus-20240229', 'claude-opus-4-1-20250805', 'claude-opus-4-20250514',
                'claude-sonnet-4-20250514'
            ]
        }

        models_to_add = expected_models.get(provider, [])
        wayback_url = f"http://web.archive.org/web/{datetime.now().strftime('%Y%m%d%H%M%S')}/{self.provider_urls[provider]}"

        return {model: (None, None, f"{wayback_url} (MANUAL_INTERVENTION_REQUIRED)")
               for model in models_to_add}