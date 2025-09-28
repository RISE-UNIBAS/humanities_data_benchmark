#!/usr/bin/env python3
"""Historical pricing database for accurate cost calculations based on benchmark run dates."""

import json
import os
from datetime import datetime
from typing import Dict, Optional, Tuple


class HistoricalPricingDB:
    """Manages historical pricing data with date-based lookups."""

    def __init__(self, db_path: str = "../pricing_history.json"):
        self.db_path = db_path
        self._pricing_data = None
        self._load_database()

    def _load_database(self):
        """Load pricing database from file."""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r') as f:
                    self._pricing_data = json.load(f)
            except Exception as e:
                print(f"Error loading pricing database: {e}")
                self._pricing_data = self._create_empty_database()
        else:
            self._pricing_data = self._create_empty_database()

    def _create_empty_database(self) -> dict:
        """Create empty pricing database structure."""
        return {
            "metadata": {
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "version": "1.0"
            },
            "pricing_history": {
                # Format: "YYYY-MM-DD": { provider: { model: [input_price, output_price] } }
            }
        }

    def save_database(self):
        """Save pricing database to file."""
        self._pricing_data["metadata"]["last_updated"] = datetime.now().isoformat()

        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else '.', exist_ok=True)

        with open(self.db_path, 'w') as f:
            json.dump(self._pricing_data, f, indent=2, sort_keys=True)

    def add_pricing_for_date(self, date: str, provider: str, model: str,
                           input_price: float, output_price: float, source: str = None):
        """Add pricing data for a specific date."""
        if date not in self._pricing_data["pricing_history"]:
            self._pricing_data["pricing_history"][date] = {}

        if provider not in self._pricing_data["pricing_history"][date]:
            self._pricing_data["pricing_history"][date][provider] = {}

        pricing_entry = {
            "input_price_per_1m": input_price,
            "output_price_per_1m": output_price
        }

        if source:
            pricing_entry["source"] = source

        pricing_entry["added"] = datetime.now().isoformat()

        self._pricing_data["pricing_history"][date][provider][model] = pricing_entry

    def get_pricing_for_date(self, date: str, provider: str, model: str) -> Optional[Tuple[float, float]]:
        """Get pricing for a specific date, with fallback to nearest available date."""

        # Try exact date match first
        if self._has_pricing_for_date(date, provider, model):
            pricing = self._pricing_data["pricing_history"][date][provider][model]
            return (pricing["input_price_per_1m"], pricing["output_price_per_1m"])

        # Fallback to nearest earlier date
        available_dates = sorted([d for d in self._pricing_data["pricing_history"].keys() if d <= date], reverse=True)

        for fallback_date in available_dates:
            if self._has_pricing_for_date(fallback_date, provider, model):
                pricing = self._pricing_data["pricing_history"][fallback_date][provider][model]
                return (pricing["input_price_per_1m"], pricing["output_price_per_1m"])

        # No historical pricing found
        return None

    def _has_pricing_for_date(self, date: str, provider: str, model: str) -> bool:
        """Check if pricing exists for specific date/provider/model."""
        return (date in self._pricing_data["pricing_history"] and
                provider in self._pricing_data["pricing_history"][date] and
                model in self._pricing_data["pricing_history"][date][provider])

    def get_available_dates(self) -> list:
        """Get all dates with pricing data."""
        return sorted(self._pricing_data["pricing_history"].keys())

    def get_providers_for_date(self, date: str) -> list:
        """Get all providers with pricing data for a date."""
        if date in self._pricing_data["pricing_history"]:
            return list(self._pricing_data["pricing_history"][date].keys())
        return []

    def get_models_for_date_provider(self, date: str, provider: str) -> list:
        """Get all models with pricing data for a date and provider."""
        if (date in self._pricing_data["pricing_history"] and
            provider in self._pricing_data["pricing_history"][date]):
            return list(self._pricing_data["pricing_history"][date][provider].keys())
        return []

    def bulk_import_pricing(self, pricing_data: dict):
        """Import bulk pricing data. Format: {date: {provider: {model: [input, output]}}}"""
        for date, providers in pricing_data.items():
            for provider, models in providers.items():
                for model, prices in models.items():
                    if isinstance(prices, (list, tuple)) and len(prices) >= 2:
                        self.add_pricing_for_date(date, provider, model, prices[0], prices[1])
                    elif isinstance(prices, dict):
                        self.add_pricing_for_date(
                            date, provider, model,
                            prices.get("input_price_per_1m", 0),
                            prices.get("output_price_per_1m", 0),
                            prices.get("source")
                        )

    def export_pricing_for_date(self, date: str) -> dict:
        """Export all pricing data for a specific date."""
        if date in self._pricing_data["pricing_history"]:
            return self._pricing_data["pricing_history"][date]
        return {}

    def get_pricing_summary(self) -> dict:
        """Get summary of pricing database."""
        dates = self.get_available_dates()
        total_entries = 0

        for date in dates:
            for provider in self.get_providers_for_date(date):
                total_entries += len(self.get_models_for_date_provider(date, provider))

        return {
            "total_dates": len(dates),
            "date_range": f"{dates[0]} to {dates[-1]}" if dates else "No data",
            "total_pricing_entries": total_entries,
            "latest_date": dates[-1] if dates else None,
            "providers": list(set(
                provider
                for date in dates
                for provider in self.get_providers_for_date(date)
            ))
        }

    def validate_pricing_completeness(self, required_models: dict) -> dict:
        """Validate that all required models have pricing for all dates.

        Args:
            required_models: {provider: [model1, model2, ...]}

        Returns:
            Dictionary with missing pricing information
        """
        dates = self.get_available_dates()
        missing = {}

        for date in dates:
            missing_for_date = []

            for provider, models in required_models.items():
                for model in models:
                    if not self._has_pricing_for_date(date, provider, model):
                        missing_for_date.append(f"{provider}/{model}")

            if missing_for_date:
                missing[date] = missing_for_date

        return missing

    def find_pricing_gaps(self) -> dict:
        """Find date ranges where pricing data is missing."""
        dates = self.get_available_dates()
        if not dates:
            return {"error": "No pricing data available"}

        gaps = []
        current_date = datetime.fromisoformat(dates[0])
        end_date = datetime.fromisoformat(dates[-1])

        i = 0
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')

            if date_str not in dates:
                # Found a gap
                gap_start = date_str

                # Find end of gap
                while (current_date <= end_date and
                       current_date.strftime('%Y-%m-%d') not in dates):
                    current_date = current_date.replace(day=current_date.day + 1)

                gap_end = (current_date.replace(day=current_date.day - 1)).strftime('%Y-%m-%d')
                gaps.append({"start": gap_start, "end": gap_end})

            current_date = current_date.replace(day=current_date.day + 1)

        return {"gaps": gaps, "total_gaps": len(gaps)}


# Convenience functions for common operations
def get_historical_pricing_db() -> HistoricalPricingDB:
    """Get singleton instance of historical pricing database."""
    if not hasattr(get_historical_pricing_db, '_instance'):
        get_historical_pricing_db._instance = HistoricalPricingDB()
    return get_historical_pricing_db._instance


def get_pricing_for_benchmark_date(date: str, provider: str, model: str) -> Optional[Tuple[float, float]]:
    """Get pricing for a benchmark run date."""
    db = get_historical_pricing_db()
    return db.get_pricing_for_date(date, provider, model)


if __name__ == "__main__":
    # Demo usage
    db = HistoricalPricingDB()

    print("Historical Pricing Database Demo")
    print("=" * 40)

    # Add some sample data
    db.add_pricing_for_date("2025-09-01", "openai", "gpt-5", 1.25, 10.00, "https://openai.com/pricing")
    db.add_pricing_for_date("2025-09-01", "openai", "gpt-5-mini", 0.25, 2.00)
    db.add_pricing_for_date("2025-09-28", "openai", "gpt-5", 1.25, 10.00)
    db.add_pricing_for_date("2025-09-28", "openai", "gpt-5-mini", 0.25, 2.00)

    # Test retrieval
    pricing = db.get_pricing_for_date("2025-09-28", "openai", "gpt-5-mini")
    if pricing:
        print(f"GPT-5-mini pricing for 2025-09-28: ${pricing[0]:.2f}/${pricing[1]:.2f} per 1M tokens")

    # Show summary
    summary = db.get_pricing_summary()
    print(f"Database summary: {summary}")

    # Save to file
    db.save_database()
    print(f"Database saved to: {db.db_path}")