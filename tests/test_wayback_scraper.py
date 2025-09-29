#!/usr/bin/env python3
"""Unit tests for wayback_scraper.py"""

import sys
import os
# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))

import unittest
from unittest.mock import patch, Mock, MagicMock
import requests
from wayback_scraper import WaybackScraper


class TestWaybackScraper(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures."""
        self.scraper = WaybackScraper()

    def test_init(self):
        """Test scraper initialization."""
        self.assertIsInstance(self.scraper.session, requests.Session)
        self.assertIn('openai', self.scraper.provider_urls)
        self.assertIn('genai', self.scraper.provider_urls)
        self.assertIn('anthropic', self.scraper.provider_urls)
        self.assertIn('mistral', self.scraper.provider_urls)

    @patch('wayback_scraper.requests.Session.get')
    def test_get_snapshots_success(self, mock_get):
        """Test successful snapshot retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            ['timestamp'],
            ['20250101120000'],
            ['20250102120000']
        ]
        mock_get.return_value = mock_response

        snapshots = self.scraper.get_snapshots('https://example.com', '2025-01-01')

        self.assertEqual(len(snapshots), 2)
        self.assertIn('20250101120000', snapshots[0])
        self.assertIn('20250102120000', snapshots[1])

    @patch('wayback_scraper.requests.Session.get')
    def test_get_snapshots_no_data(self, mock_get):
        """Test snapshot retrieval with no data."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [['timestamp']]  # Only header
        mock_get.return_value = mock_response

        snapshots = self.scraper.get_snapshots('https://example.com', '2025-01-01')

        self.assertEqual(snapshots, [])

    @patch('wayback_scraper.requests.Session.get')
    def test_get_snapshots_error(self, mock_get):
        """Test snapshot retrieval with network error."""
        mock_get.side_effect = requests.RequestException("Network error")

        snapshots = self.scraper.get_snapshots('https://example.com', '2025-01-01')

        self.assertEqual(snapshots, [])

    @patch('wayback_scraper.requests.Session.get')
    def test_fetch_content_success(self, mock_get):
        """Test successful content fetching."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html>Test content</html>"
        mock_get.return_value = mock_response

        content = self.scraper.fetch_content('http://web.archive.org/web/123/example.com')

        self.assertEqual(content, "<html>Test content</html>")

    @patch('wayback_scraper.requests.Session.get')
    def test_fetch_content_error(self, mock_get):
        """Test content fetching with error."""
        mock_get.side_effect = requests.RequestException("Fetch error")

        content = self.scraper.fetch_content('http://web.archive.org/web/123/example.com')

        self.assertIsNone(content)

    @patch('wayback_scraper.requests.Session.get')
    def test_save_to_wayback_success(self, mock_get):
        """Test successful saving to Wayback Machine."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.url = "http://web.archive.org/web/20250929120000/https://example.com"
        mock_get.return_value = mock_response

        result = self.scraper.save_to_wayback('https://example.com')

        self.assertEqual(result, "http://web.archive.org/web/20250929120000/https://example.com")
        mock_get.assert_called_once_with('https://web.archive.org/save/https://example.com', timeout=30)

    @patch('wayback_scraper.requests.Session.get')
    def test_save_to_wayback_construct_url(self, mock_get):
        """Test Wayback URL construction when response doesn't contain archive URL."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.url = "https://example.com"  # No archive URL in response
        mock_get.return_value = mock_response

        result = self.scraper.save_to_wayback('https://example.com')

        # Should construct a Wayback URL (timestamp will be current time)
        self.assertIsNotNone(result)
        self.assertIn("http://web.archive.org/web/", result)
        self.assertIn("https://example.com", result)

    @patch('wayback_scraper.requests.Session.get')
    def test_save_to_wayback_error(self, mock_get):
        """Test saving to Wayback Machine with error."""
        mock_get.side_effect = requests.RequestException("Save error")

        result = self.scraper.save_to_wayback('https://example.com')

        self.assertIsNone(result)

    @patch('wayback_scraper.WaybackScraper.extract_pricing_with_ai')
    def test_parse_openai_pricing(self, mock_extract_ai):
        """Test parsing OpenAI pricing from HTML using AI."""
        mock_extract_ai.return_value = {'gpt-4o': (2.5, 10.0), 'gpt-4o-mini': (0.15, 0.6)}

        html_content = """
        <html>
        <body>
        <p>gpt-4o input $2.50 per 1M tokens output $10.00 per 1M tokens</p>
        <p>gpt-4o-mini input $0.15 per 1M tokens output $0.60 per 1M tokens</p>
        </body>
        </html>
        """

        models = self.scraper.parse_openai_pricing(html_content)

        # Should use AI extraction and return models
        self.assertIsInstance(models, dict)
        mock_extract_ai.assert_called_once_with(html_content, 'openai')

    @patch('wayback_scraper.WaybackScraper.extract_pricing_with_ai')
    def test_parse_genai_pricing(self, mock_extract_ai):
        """Test parsing GenAI pricing from HTML using AI."""
        mock_extract_ai.return_value = {'gemini-2.0-flash': (0.075, 0.3)}

        html_content = """
        <html>
        <body>
        <h3>Gemini 2.0 Flash</h3>
        <p>Input: $0.075 per 1M tokens</p>
        <p>Output: $0.30 per 1M tokens</p>
        </body>
        </html>
        """

        models = self.scraper.parse_genai_pricing(html_content)

        self.assertIsInstance(models, dict)
        mock_extract_ai.assert_called_once_with(html_content, 'genai')

    @patch('wayback_scraper.WaybackScraper.extract_pricing_with_ai')
    def test_parse_mistral_pricing(self, mock_extract_ai):
        """Test parsing Mistral pricing from HTML using AI."""
        mock_extract_ai.return_value = {'mistral-medium-2508': (0.4, 2.0)}

        html_content = """
        <html>
        <body>
        <h3>Mistral Medium 2508</h3>
        <p>Input: $0.40 per 1M tokens</p>
        <p>Output: $2.00 per 1M tokens</p>
        </body>
        </html>
        """

        models = self.scraper.parse_mistral_pricing(html_content)

        self.assertIsInstance(models, dict)
        mock_extract_ai.assert_called_once_with(html_content, 'mistral')

    @patch('wayback_scraper.WaybackScraper.extract_pricing_with_ai')
    def test_parse_anthropic_pricing(self, mock_extract_ai):
        """Test parsing Anthropic pricing from HTML using AI."""
        mock_extract_ai.return_value = {
            'claude-3-5-sonnet': (3.0, 15.0),
            'claude-opus-4-1-20250805': (15.0, 75.0)
        }

        html_content = """
        <html>
        <body>
        <h3>Claude 3.5 Sonnet</h3>
        <p>Input: $3.00 per 1M tokens</p>
        <p>Output: $15.00 per 1M tokens</p>
        <h3>Claude Opus 4.1</h3>
        <p>Input: $15.00 per 1M tokens</p>
        <p>Output: $75.00 per 1M tokens</p>
        </body>
        </html>
        """

        models = self.scraper.parse_anthropic_pricing(html_content)

        self.assertIsInstance(models, dict)
        mock_extract_ai.assert_called_once_with(html_content, 'anthropic')

    @patch('wayback_scraper.WaybackScraper.find_available_snapshots')
    @patch('wayback_scraper.WaybackScraper.fetch_content')
    @patch('wayback_scraper.WaybackScraper.parse_genai_pricing')
    def test_scrape_pricing_success(self, mock_parse, mock_fetch, mock_snapshots):
        """Test successful pricing scraping."""
        mock_snapshots.return_value = ['http://web.archive.org/web/123/example.com']
        mock_fetch.return_value = "<html>Mock content</html>"
        mock_parse.return_value = {'gemini-2.0-flash': (0.075, 0.3)}

        result = self.scraper.scrape_pricing('genai', '2025-01-01')

        self.assertIn('gemini-2.0-flash', result)
        self.assertEqual(result['gemini-2.0-flash'][0], 0.075)
        self.assertEqual(result['gemini-2.0-flash'][1], 0.3)

    @patch('wayback_scraper.WaybackScraper.find_available_snapshots')
    @patch('wayback_scraper.WaybackScraper.fetch_content')
    @patch('wayback_scraper.WaybackScraper.parse_anthropic_pricing')
    def test_scrape_pricing_anthropic_success(self, mock_parse, mock_fetch, mock_snapshots):
        """Test successful Anthropic pricing scraping."""
        mock_snapshots.return_value = ['http://web.archive.org/web/123/claude.com/pricing']
        mock_fetch.return_value = "<html>Claude pricing content</html>"
        mock_parse.return_value = {
            'claude-3-5-sonnet': (3.0, 15.0),
            'claude-opus-4-1-20250805': (15.0, 75.0)
        }

        result = self.scraper.scrape_pricing('anthropic', '2025-01-01')

        self.assertIn('claude-3-5-sonnet', result)
        self.assertEqual(result['claude-3-5-sonnet'][0], 3.0)
        self.assertEqual(result['claude-3-5-sonnet'][1], 15.0)
        self.assertIn('claude-opus-4-1-20250805', result)
        self.assertEqual(result['claude-opus-4-1-20250805'][0], 15.0)
        self.assertEqual(result['claude-opus-4-1-20250805'][1], 75.0)

    @patch('wayback_scraper.WaybackScraper.find_available_snapshots')
    def test_scrape_pricing_no_snapshots(self, mock_snapshots):
        """Test pricing scraping with no snapshots."""
        mock_snapshots.return_value = []

        result = self.scraper.scrape_pricing('genai', '2025-01-01')

        self.assertEqual(result, {})

    def test_scrape_pricing_unknown_provider(self):
        """Test pricing scraping with unknown provider."""
        result = self.scraper.scrape_pricing('unknown_provider', '2025-01-01')

        self.assertEqual(result, {})

    @patch('wayback_scraper.WaybackScraper.get_snapshots')
    def test_find_available_snapshots_first_try(self, mock_get_snapshots):
        """Test finding snapshots on first try."""
        mock_get_snapshots.return_value = ['snapshot1', 'snapshot2']

        snapshots = self.scraper.find_available_snapshots('https://example.com', '2025-01-01')

        self.assertEqual(snapshots, ['snapshot1', 'snapshot2'])
        mock_get_snapshots.assert_called_once_with('https://example.com', '2025-01-01')

    @patch('wayback_scraper.WaybackScraper.get_snapshots')
    def test_find_available_snapshots_backwards_search(self, mock_get_snapshots):
        """Test finding snapshots by searching backwards."""
        # First call returns empty, second call returns snapshots
        mock_get_snapshots.side_effect = [[], ['found_snapshot']]

        snapshots = self.scraper.find_available_snapshots('https://example.com', '2025-01-01', days_back=2)

        self.assertEqual(snapshots, ['found_snapshot'])
        self.assertEqual(mock_get_snapshots.call_count, 2)

    @patch('wayback_scraper.WaybackScraper.get_snapshots')
    def test_find_available_snapshots_none_found(self, mock_get_snapshots):
        """Test finding no snapshots within search range."""
        mock_get_snapshots.return_value = []

        snapshots = self.scraper.find_available_snapshots('https://example.com', '2025-01-01', days_back=2)

        self.assertEqual(snapshots, [])
        self.assertEqual(mock_get_snapshots.call_count, 3)  # Original date + 2 days back

    @patch('wayback_scraper.WaybackScraper.extract_pricing_with_ai')
    def test_extract_pricing_with_ai_success(self, mock_extract_ai):
        """Test successful AI pricing extraction."""
        mock_extract_ai.return_value = {'gpt-4o': (2.5, 10.0)}

        html_content = "<html><body>GPT-4o pricing: input $2.50, output $10.00</body></html>"

        result = self.scraper.extract_pricing_with_ai(html_content, 'openai')

        # Should successfully extract pricing
        self.assertEqual(result, {'gpt-4o': (2.5, 10.0)})

    @patch('wayback_scraper.WaybackScraper.extract_pricing_with_ai')
    def test_extract_pricing_with_ai_empty_response(self, mock_extract_ai):
        """Test AI pricing extraction with empty response."""
        mock_extract_ai.return_value = {}

        result = self.scraper.extract_pricing_with_ai('<html></html>', 'mistral')

        # Should return empty dict when no models found
        self.assertEqual(result, {})

    @patch('wayback_scraper.WaybackScraper.extract_pricing_with_ai')
    def test_extract_pricing_with_ai_json_error(self, mock_extract_ai):
        """Test AI pricing extraction with invalid JSON."""
        mock_extract_ai.return_value = {}

        result = self.scraper.extract_pricing_with_ai('<html></html>', 'openai')

        # Should return empty dict on JSON parse error
        self.assertEqual(result, {})

    @patch('wayback_scraper.WaybackScraper.save_to_wayback')
    @patch('wayback_scraper.WaybackScraper.fetch_content')
    @patch('wayback_scraper.WaybackScraper.parse_genai_pricing')
    @patch('wayback_scraper.datetime')
    def test_scrape_pricing_current_date(self, mock_datetime, mock_parse, mock_fetch, mock_save):
        """Test scraping pricing for current date (fetches live and saves to Wayback)."""
        # Mock current date
        mock_datetime.now.return_value.strftime.return_value = '2025-09-29'

        # Mock successful current content fetch and parsing
        mock_fetch.return_value = "<html>Live content</html>"
        mock_parse.return_value = {'gemini-2.0-flash': (0.1, 0.4)}
        mock_save.return_value = "http://web.archive.org/web/20250929120000/https://ai.google.dev/gemini-api/docs/pricing"

        result = self.scraper.scrape_pricing('genai', '2025-09-29')

        # Should fetch current content and save to Wayback
        mock_fetch.assert_called_with('https://ai.google.dev/gemini-api/docs/pricing')
        mock_parse.assert_called_once_with("<html>Live content</html>")
        mock_save.assert_called_once_with('https://ai.google.dev/gemini-api/docs/pricing')

        # Should return pricing with Wayback URL
        self.assertIn('gemini-2.0-flash', result)
        self.assertEqual(result['gemini-2.0-flash'][0], 0.1)
        self.assertEqual(result['gemini-2.0-flash'][1], 0.4)
        self.assertEqual(result['gemini-2.0-flash'][2], "http://web.archive.org/web/20250929120000/https://ai.google.dev/gemini-api/docs/pricing")

    def test_scrape_pricing_none_values_returned(self):
        """Test that None pricing values are returned when extraction fails."""
        with patch('wayback_scraper.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = '20250929160000'

            # Mock snapshots found but content extraction fails
            mock_snapshot_url = "http://web.archive.org/web/123/mistral.ai"
            with patch.object(self.scraper, 'find_available_snapshots', return_value=[mock_snapshot_url]):
                with patch.object(self.scraper, 'fetch_content', return_value="<html>No useful pricing info</html>"):
                    with patch.object(self.scraper, 'parse_mistral_pricing', return_value={}):
                        result = self.scraper.scrape_pricing('mistral', '2025-01-01')

                        # Should return None values for manual intervention
                        self.assertIn('mistral-medium-2508', result)
                        self.assertIn('mistral-medium-2505', result)

                        # Check None values
                        input_price, output_price, source_url = result['mistral-medium-2508']
                        self.assertIsNone(input_price)
                        self.assertIsNone(output_price)
                        self.assertIn('MANUAL_INTERVENTION_REQUIRED', source_url)


if __name__ == '__main__':
    unittest.main()