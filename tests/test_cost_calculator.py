#!/usr/bin/env python3
"""Unit tests for CostCalculator in simple_ai_clients.py"""

import sys
import os
# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))

import unittest
from unittest.mock import patch, Mock, MagicMock
from simple_ai_clients import CostCalculator


class TestCostCalculator(unittest.TestCase):

    @patch('pricing_database.get_pricing_database')
    def test_calculate_cost_for_date_cached_pricing(self, mock_get_db):
        """Test cost calculation with cached pricing."""
        mock_db = Mock()
        mock_db.get_pricing.return_value = (10.0, 30.0, "cached_url")
        mock_get_db.return_value = mock_db

        cost = CostCalculator.calculate_cost_for_date(
            "2025-01-01", "openai", "gpt-4", 1000, 500
        )

        expected_cost = (1000 / 1_000_000) * 10.0 + (500 / 1_000_000) * 30.0
        self.assertAlmostEqual(cost, expected_cost, places=6)

    @patch('wayback_scraper.WaybackScraper')
    @patch('pricing_database.get_pricing_database')
    def test_calculate_cost_for_date_wayback_fallback(self, mock_get_db, mock_scraper_class):
        """Test cost calculation with Wayback Machine fallback."""
        mock_db = Mock()
        mock_db.get_pricing.return_value = None  # No cached pricing
        mock_get_db.return_value = mock_db

        mock_scraper = Mock()
        mock_scraper.scrape_pricing.return_value = {
            'gpt-4': (15.0, 45.0, "wayback_url")
        }
        mock_scraper_class.return_value = mock_scraper

        cost = CostCalculator.calculate_cost_for_date(
            "2025-01-01", "openai", "gpt-4", 2000, 1000
        )

        expected_cost = (2000 / 1_000_000) * 15.0 + (1000 / 1_000_000) * 45.0
        self.assertAlmostEqual(cost, expected_cost, places=6)

        # Verify pricing was added to database
        mock_db.add_pricing.assert_called_once_with(
            "2025-01-01", "openai", "gpt-4", 15.0, 45.0, "wayback_url"
        )

    @patch('wayback_scraper.WaybackScraper')
    @patch('pricing_database.get_pricing_database')
    def test_calculate_cost_for_date_no_pricing_found(self, mock_get_db, mock_scraper_class):
        """Test cost calculation when no pricing is found."""
        mock_db = Mock()
        mock_db.get_pricing.return_value = None
        mock_get_db.return_value = mock_db

        mock_scraper = Mock()
        mock_scraper.scrape_pricing.return_value = {}  # No pricing found
        mock_scraper_class.return_value = mock_scraper

        cost = CostCalculator.calculate_cost_for_date(
            "2025-01-01", "openai", "gpt-4", 1000, 500
        )

        self.assertEqual(cost, 0.0)

    @patch('simple_ai_clients.CostCalculator.calculate_cost_for_date')
    @patch('simple_ai_clients.datetime')
    def test_calculate_cost_current_date(self, mock_datetime, mock_calculate_for_date):
        """Test calculate_cost uses current date."""
        mock_datetime.now.return_value.strftime.return_value = "2025-01-15"
        mock_calculate_for_date.return_value = 0.05

        cost = CostCalculator.calculate_cost("openai", "gpt-4", 1000, 500)

        self.assertEqual(cost, 0.05)
        mock_calculate_for_date.assert_called_once_with(
            "2025-01-15", "openai", "gpt-4", 1000, 500
        )

    @patch('pricing_database.get_pricing_database')
    def test_get_pricing_info_found(self, mock_get_db):
        """Test getting pricing info when data exists."""
        mock_db = Mock()
        mock_db.get_pricing.return_value = (12.0, 36.0, "test_url")
        mock_get_db.return_value = mock_db

        info = CostCalculator.get_pricing_info("openai", "gpt-4", "2025-01-01")

        expected = {
            'provider': 'openai',
            'model': 'gpt-4',
            'date': '2025-01-01',
            'input_price_per_1m': 12.0,
            'output_price_per_1m': 36.0,
            'source_url': 'test_url'
        }
        self.assertEqual(info, expected)

    @patch('pricing_database.get_pricing_database')
    def test_get_pricing_info_not_found(self, mock_get_db):
        """Test getting pricing info when no data exists."""
        mock_db = Mock()
        mock_db.get_pricing.return_value = None
        mock_get_db.return_value = mock_db

        info = CostCalculator.get_pricing_info("openai", "gpt-4", "2025-01-01")

        self.assertIn('error', info)
        self.assertIn('No pricing found', info['error'])

    @patch('pricing_database.get_pricing_database')
    def test_verify_model_availability_true(self, mock_get_db):
        """Test model availability verification when pricing exists."""
        mock_db = Mock()
        mock_db.get_pricing.return_value = (10.0, 30.0, "url")
        mock_get_db.return_value = mock_db

        available = CostCalculator.verify_model_availability("openai", "gpt-4", "2025-01-01")

        self.assertTrue(available)

    @patch('pricing_database.get_pricing_database')
    def test_verify_model_availability_false(self, mock_get_db):
        """Test model availability verification when no pricing exists."""
        mock_db = Mock()
        mock_db.get_pricing.return_value = None
        mock_get_db.return_value = mock_db

        available = CostCalculator.verify_model_availability("openai", "gpt-4", "2025-01-01")

        self.assertFalse(available)

    @patch('simple_ai_clients.logging')
    def test_calculate_cost_for_date_error_handling(self, mock_logging):
        """Test error handling in cost calculation."""
        with patch('pricing_database.get_pricing_database', side_effect=Exception("Test error")):
            cost = CostCalculator.calculate_cost_for_date(
                "2025-01-01", "openai", "gpt-4", 1000, 500
            )

        self.assertEqual(cost, 0.0)
        mock_logging.error.assert_called()

    def test_token_calculation_precision(self):
        """Test precision of token cost calculations."""
        with patch('pricing_database.get_pricing_database') as mock_get_db:
            mock_db = Mock()
            mock_db.get_pricing.return_value = (2.5, 10.0, "test_url")
            mock_get_db.return_value = mock_db

            # Test with specific token counts
            cost = CostCalculator.calculate_cost_for_date(
                "2025-01-01", "openai", "gpt-4o", 19557, 0
            )

            expected_cost = (19557 / 1_000_000) * 2.5
            self.assertAlmostEqual(cost, expected_cost, places=6)

    @patch('simple_ai_clients.datetime')
    def test_get_pricing_info_default_date(self, mock_datetime):
        """Test get_pricing_info uses current date when none provided."""
        mock_datetime.now.return_value.strftime.return_value = "2025-01-20"

        with patch('pricing_database.get_pricing_database') as mock_get_db:
            mock_db = Mock()
            mock_db.get_pricing.return_value = (5.0, 15.0, "url")
            mock_get_db.return_value = mock_db

            info = CostCalculator.get_pricing_info("genai", "gemini-2.0-flash")

            self.assertEqual(info['date'], "2025-01-20")
            mock_db.get_pricing.assert_called_with("2025-01-20", "genai", "gemini-2.0-flash")


if __name__ == '__main__':
    unittest.main()