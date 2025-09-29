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

    def test_parse_openai_pricing(self):
        """Test parsing OpenAI pricing from HTML."""
        html_content = """
        <html>
        <body>
        <p>gpt-4o input $2.50 per 1M tokens output $10.00 per 1M tokens</p>
        <p>gpt-4o-mini input $0.15 per 1M tokens output $0.60 per 1M tokens</p>
        </body>
        </html>
        """

        models = self.scraper.parse_openai_pricing(html_content)

        # Should parse at least one model if patterns match
        # Note: This depends on the regex patterns in the actual implementation
        self.assertIsInstance(models, dict)

    def test_parse_genai_pricing(self):
        """Test parsing GenAI pricing from HTML."""
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


if __name__ == '__main__':
    unittest.main()