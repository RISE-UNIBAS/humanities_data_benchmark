#!/usr/bin/env python3
"""Simple pricing database with Wayback Machine fallback."""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple


class PricingDatabase:
    """Simple pricing database with automatic Wayback Machine lookup."""

    def __init__(self, db_path: str = "data/pricing.json"):
        """Initialize pricing database."""
        self.db_path = db_path
        self._data = self._load_database()

    def _load_database(self) -> dict:
        """Load pricing data from JSON file."""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Failed to load pricing database: {e}")

        # Create empty database structure
        return {
            "metadata": {
                "created": datetime.now().isoformat(),
                "version": "1.0"
            },
            "pricing": {}
        }

    def _save_database(self) -> None:
        """Save pricing data to JSON file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else '.', exist_ok=True)

            self._data["metadata"]["last_updated"] = datetime.now().isoformat()

            with open(self.db_path, 'w') as f:
                json.dump(self._data, f, indent=2)

        except Exception as e:
            logging.error(f"Failed to save pricing database: {e}")

    def get_pricing(self, date: str, provider: str, model: str) -> Optional[Tuple[float, float, str]]:
        """
        Get pricing for date/provider/model.

        Returns:
            Tuple of (input_price_per_1M, output_price_per_1M, wayback_url) or None
        """
        try:
            pricing_data = self._data.get("pricing", {}).get(date, {}).get(provider, {}).get(model)
            if pricing_data:
                return (
                    pricing_data["input_price"],
                    pricing_data["output_price"],
                    pricing_data["source_url"]
                )
        except Exception as e:
            logging.error(f"Error retrieving pricing: {e}")

        return None

    def add_pricing(self, date: str, provider: str, model: str,
                   input_price: float, output_price: float, source_url: str) -> None:
        """Add pricing data to database."""
        try:
            # Initialize nested structure if needed
            if date not in self._data["pricing"]:
                self._data["pricing"][date] = {}
            if provider not in self._data["pricing"][date]:
                self._data["pricing"][date][provider] = {}

            # Add pricing data
            self._data["pricing"][date][provider][model] = {
                "input_price": input_price,
                "output_price": output_price,
                "source_url": source_url,
                "added": datetime.now().isoformat()
            }

            self._save_database()
            logging.info(f"Added pricing: {date} {provider}/{model} = ${input_price}/${output_price}")

        except Exception as e:
            logging.error(f"Error adding pricing: {e}")


# Global database instance
_db_instance = None

def get_pricing_database() -> PricingDatabase:
    """Get global pricing database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = PricingDatabase()
    return _db_instance