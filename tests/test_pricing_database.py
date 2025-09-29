#!/usr/bin/env python3
"""Unit tests for pricing_database.py"""

import sys
import os
# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))

import unittest
import json
import tempfile
from unittest.mock import patch, mock_open
from pricing_database import PricingDatabase, get_pricing_database


class TestPricingDatabase(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test_pricing.json")

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        os.rmdir(self.temp_dir)

    def test_init_new_database(self):
        """Test initializing a new database."""
        db = PricingDatabase(self.test_db_path)

        self.assertEqual(db.db_path, self.test_db_path)
        self.assertIn("metadata", db._data)
        self.assertIn("pricing", db._data)
        self.assertEqual(db._data["pricing"], {})

    def test_init_existing_database(self):
        """Test loading existing database."""
        # Create a test database file
        test_data = {
            "metadata": {"version": "1.0"},
            "pricing": {
                "2025-01-01": {
                    "openai": {
                        "gpt-4": {
                            "input_price": 10.0,
                            "output_price": 30.0,
                            "source_url": "test_url",
                            "added": "2025-01-01T00:00:00"
                        }
                    }
                }
            }
        }

        with open(self.test_db_path, 'w') as f:
            json.dump(test_data, f)

        db = PricingDatabase(self.test_db_path)

        self.assertEqual(db._data["pricing"]["2025-01-01"]["openai"]["gpt-4"]["input_price"], 10.0)

    def test_add_pricing(self):
        """Test adding pricing data."""
        db = PricingDatabase(self.test_db_path)

        db.add_pricing("2025-01-01", "openai", "gpt-4", 10.0, 30.0, "test_url")

        pricing_data = db.get_pricing("2025-01-01", "openai", "gpt-4")
        self.assertIsNotNone(pricing_data)
        self.assertEqual(pricing_data[0], 10.0)  # input_price
        self.assertEqual(pricing_data[1], 30.0)  # output_price
        self.assertEqual(pricing_data[2], "test_url")  # source_url

    def test_get_pricing_not_found(self):
        """Test getting pricing that doesn't exist."""
        db = PricingDatabase(self.test_db_path)

        pricing_data = db.get_pricing("2025-01-01", "openai", "gpt-4")

        self.assertIsNone(pricing_data)

    def test_get_pricing_found(self):
        """Test getting existing pricing."""
        db = PricingDatabase(self.test_db_path)
        db.add_pricing("2025-01-01", "genai", "gemini-2.0-flash", 0.1, 0.4, "wayback_url")

        pricing_data = db.get_pricing("2025-01-01", "genai", "gemini-2.0-flash")

        self.assertEqual(pricing_data, (0.1, 0.4, "wayback_url"))

    def test_database_persistence(self):
        """Test that database persists to file."""
        db = PricingDatabase(self.test_db_path)
        db.add_pricing("2025-01-01", "anthropic", "claude-3", 15.0, 75.0, "test_source")

        # Create new instance to test loading
        db2 = PricingDatabase(self.test_db_path)
        pricing_data = db2.get_pricing("2025-01-01", "anthropic", "claude-3")

        self.assertEqual(pricing_data, (15.0, 75.0, "test_source"))

    @patch('pricing_database.logging')
    def test_error_handling_load(self, mock_logging):
        """Test error handling when loading invalid JSON."""
        # Create invalid JSON file
        with open(self.test_db_path, 'w') as f:
            f.write("invalid json")

        db = PricingDatabase(self.test_db_path)

        # Should create empty database structure
        self.assertEqual(db._data["pricing"], {})
        mock_logging.error.assert_called()

    def test_global_database_instance(self):
        """Test global database instance function."""
        # Reset global instance
        import pricing_database
        pricing_database._db_instance = None

        db1 = get_pricing_database()
        db2 = get_pricing_database()

        # Should return same instance
        self.assertIs(db1, db2)


if __name__ == '__main__':
    unittest.main()