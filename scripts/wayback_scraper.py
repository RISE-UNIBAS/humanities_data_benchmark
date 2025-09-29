#!/usr/bin/env python3
"""Simple Wayback Machine pricing scraper."""

import requests
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup


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
            'openai': 'https://openai.com/pricing',
            'anthropic': 'https://claude.ai/pricing',
            'genai': 'https://ai.google.dev/gemini-api/docs/pricing',
            'mistral': 'https://mistral.ai/pricing'
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

    def fetch_content(self, wayback_url: str) -> Optional[str]:
        """Fetch content from Wayback Machine URL."""
        try:
            response = self.session.get(wayback_url, timeout=60)
            if response.status_code == 200:
                return response.text
        except Exception as e:
            logging.error(f"Error fetching {wayback_url}: {e}")

        return None

    def parse_openai_pricing(self, html: str) -> Dict[str, Tuple[float, float]]:
        """Parse OpenAI pricing from HTML."""
        models = {}
        try:
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text()

            # Common OpenAI models and their pricing patterns
            model_patterns = [
                r'gpt-4o[^a-z]*?input.*?(\d+\.?\d*)[^\d]*?output.*?(\d+\.?\d*)',
                r'gpt-4o-mini[^a-z]*?input.*?(\d+\.?\d*)[^\d]*?output.*?(\d+\.?\d*)',
            ]

            # Try to find model pricing
            for pattern in model_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    model_name = 'gpt-4o' if 'gpt-4o' in match.group(0).lower() else 'gpt-4o-mini'
                    input_price = float(match.group(1))
                    output_price = float(match.group(2))
                    models[model_name] = (input_price, output_price)
                    break  # Use first match

        except Exception as e:
            logging.error(f"Error parsing OpenAI pricing: {e}")

        return models

    def parse_genai_pricing(self, html: str) -> Dict[str, Tuple[float, float]]:
        """Parse GenAI pricing from HTML."""
        models = {}
        try:
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text()

            logging.info("Searching for GenAI pricing patterns...")

            # Look for Gemini pricing patterns with input/output indicators
            patterns = [
                r'gemini-2\.0-flash.*?input.*?(\d+\.?\d*).*?output.*?(\d+\.?\d*)',
                r'gemini-1\.5-pro.*?input.*?(\d+\.?\d*).*?output.*?(\d+\.?\d*)',
                r'gemini.*?2\.0.*?flash.*?input.*?(\d+\.?\d*).*?output.*?(\d+\.?\d*)',
                r'gemini.*?1\.5.*?pro.*?input.*?(\d+\.?\d*).*?output.*?(\d+\.?\d*)',
                # Also try reverse order (output first)
                r'gemini-2\.0-flash.*?output.*?(\d+\.?\d*).*?input.*?(\d+\.?\d*)',
                r'gemini-1\.5-pro.*?output.*?(\d+\.?\d*).*?input.*?(\d+\.?\d*)',
            ]

            for i, pattern in enumerate(patterns):
                logging.debug(f"Trying pattern {i+1}: {pattern}")
                matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    logging.debug(f"Found match: {match.group(0)[:300]}...")
                    model_name = 'gemini-2.0-flash' if ('2.0' in match.group(0).lower() or '2-0' in match.group(0).lower()) else 'gemini-1.5-pro'

                    # Check if pattern has output first (patterns 4-5)
                    if i >= 4:
                        # output first, input second
                        output_price = float(match.group(1))
                        input_price = float(match.group(2))
                    else:
                        # input first, output second
                        input_price = float(match.group(1))
                        output_price = float(match.group(2))

                    models[model_name] = (input_price, output_price)
                    logging.info(f"Extracted pricing for {model_name}: input=${input_price}, output=${output_price}")
                    break
                if models:
                    break

        except Exception as e:
            logging.error(f"Error parsing GenAI pricing: {e}")

        return models

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
                    else:
                        models = {}

                    if models:
                        return {model: (input_p, output_p, f"{self.provider_urls[provider]} (current pricing)")
                               for model, (input_p, output_p) in models.items()}
            except Exception as e:
                logging.error(f"Error fetching current pricing: {e}")


        logging.warning(f"No pricing data extracted for {provider} on {date}")
        return {}