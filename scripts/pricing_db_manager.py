#!/usr/bin/env python3
"""Tools to manage the historical pricing database."""

import json
import os
import sys
from datetime import datetime
from historical_pricing_db import HistoricalPricingDB


def initialize_pricing_database():
    """Initialize pricing database with current pricing as starting point."""
    db = HistoricalPricingDB()

    # Import current pricing from CostCalculator as baseline
    try:
        from simple_ai_clients import CostCalculator

        current_date = datetime.now().strftime('%Y-%m-%d')
        print(f"Initializing pricing database with current pricing for {current_date}")

        for provider, models in CostCalculator.PRICING.items():
            for model, (input_price, output_price) in models.items():
                db.add_pricing_for_date(
                    current_date, provider, model,
                    input_price, output_price,
                    f"Initialized from CostCalculator.PRICING on {current_date}"
                )
                print(f"  Added {provider}/{model}: ${input_price}/${output_price}")

        db.save_database()
        print(f"\n✓ Database initialized and saved to: {db.db_path}")

        summary = db.get_pricing_summary()
        print(f"  Total entries: {summary['total_pricing_entries']}")
        print(f"  Providers: {', '.join(summary['providers'])}")

    except ImportError as e:
        print(f"Error importing CostCalculator: {e}")
        return False

    return True


def add_historical_pricing(date: str, provider: str, model: str,
                         input_price: float, output_price: float, source: str = None):
    """Add historical pricing for a specific date."""
    db = HistoricalPricingDB()

    db.add_pricing_for_date(date, provider, model, input_price, output_price, source)
    db.save_database()

    print(f"✓ Added pricing for {date}: {provider}/{model} = ${input_price}/${output_price}")

    if source:
        print(f"  Source: {source}")


def import_pricing_from_json(json_file: str):
    """Import pricing data from JSON file.

    Expected format:
    {
      "2025-09-01": {
        "openai": {
          "gpt-5": [1.25, 10.00],
          "gpt-5-mini": [0.25, 2.00]
        },
        "anthropic": {
          "claude-3-5-sonnet": [3.00, 15.00]
        }
      }
    }
    """
    if not os.path.exists(json_file):
        print(f"JSON file not found: {json_file}")
        return False

    try:
        with open(json_file, 'r') as f:
            pricing_data = json.load(f)

        db = HistoricalPricingDB()
        db.bulk_import_pricing(pricing_data)
        db.save_database()

        print(f"✓ Successfully imported pricing data from {json_file}")

        summary = db.get_pricing_summary()
        print(f"  Database now contains {summary['total_pricing_entries']} pricing entries")
        print(f"  Date range: {summary['date_range']}")

        return True

    except Exception as e:
        print(f"Error importing from JSON: {e}")
        return False


def export_pricing_to_json(output_file: str, date: str = None):
    """Export pricing data to JSON file."""
    db = HistoricalPricingDB()

    if date:
        # Export specific date
        pricing_data = {date: db.export_pricing_for_date(date)}
        if not pricing_data[date]:
            print(f"No pricing data found for date: {date}")
            return False
    else:
        # Export all pricing data
        pricing_data = db._pricing_data["pricing_history"]

    try:
        with open(output_file, 'w') as f:
            json.dump(pricing_data, f, indent=2, sort_keys=True)

        print(f"✓ Pricing data exported to: {output_file}")

        if date:
            print(f"  Exported data for date: {date}")
        else:
            dates = sorted(pricing_data.keys())
            print(f"  Exported {len(dates)} dates: {dates[0]} to {dates[-1]}")

        return True

    except Exception as e:
        print(f"Error exporting to JSON: {e}")
        return False


def validate_database():
    """Validate pricing database completeness."""
    db = HistoricalPricingDB()

    print("Pricing Database Validation")
    print("=" * 40)

    summary = db.get_pricing_summary()
    print(f"Total dates: {summary['total_dates']}")
    print(f"Total entries: {summary['total_pricing_entries']}")
    print(f"Date range: {summary['date_range']}")
    print(f"Providers: {', '.join(summary['providers'])}")

    # Check for required models from benchmark config
    try:
        import csv
        config_file = "../benchmarks/benchmarks_tests.csv"

        if os.path.exists(config_file):
            required_models = {}

            with open(config_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('legacy_test', 'false').lower() == 'false':
                        provider = row['provider']
                        model = row['model']

                        if provider not in required_models:
                            required_models[provider] = set()
                        required_models[provider].add(model)

            # Convert sets to lists
            required_models = {k: list(v) for k, v in required_models.items()}

            print(f"\nRequired models from benchmarks:")
            for provider, models in required_models.items():
                print(f"  {provider}: {', '.join(models)}")

            missing = db.validate_pricing_completeness(required_models)

            if missing:
                print(f"\n⚠ Missing pricing data:")
                for date, models in missing.items():
                    print(f"  {date}: {', '.join(models)}")
            else:
                print(f"\n✓ All required models have pricing data")

    except Exception as e:
        print(f"Error validating against benchmarks: {e}")

    # Check for pricing gaps
    gaps = db.find_pricing_gaps()
    if gaps.get("gaps"):
        print(f"\n⚠ Found {gaps['total_gaps']} date gaps in pricing data:")
        for gap in gaps["gaps"]:
            print(f"  {gap['start']} to {gap['end']}")
    else:
        print(f"\n✓ No date gaps found in pricing data")


def show_pricing_for_date(date: str):
    """Show all pricing data for a specific date."""
    db = HistoricalPricingDB()

    pricing_data = db.export_pricing_for_date(date)

    if not pricing_data:
        print(f"No pricing data found for date: {date}")
        return

    print(f"Pricing data for {date}:")
    print("=" * 40)

    for provider, models in pricing_data.items():
        print(f"\n{provider.upper()}:")
        for model, pricing in models.items():
            input_price = pricing["input_price_per_1m"]
            output_price = pricing["output_price_per_1m"]
            print(f"  {model}: ${input_price}/${output_price} per 1M tokens")

            if "source" in pricing:
                print(f"    Source: {pricing['source']}")


def main():
    """Command line interface for pricing database management."""
    if len(sys.argv) < 2:
        print("Historical Pricing Database Manager")
        print("=" * 40)
        print("Usage:")
        print("  python pricing_db_manager.py init                           # Initialize database")
        print("  python pricing_db_manager.py add DATE PROVIDER MODEL INPUT OUTPUT [SOURCE]")
        print("  python pricing_db_manager.py import FILE.json              # Import from JSON")
        print("  python pricing_db_manager.py export FILE.json [DATE]       # Export to JSON")
        print("  python pricing_db_manager.py validate                      # Validate database")
        print("  python pricing_db_manager.py show DATE                     # Show pricing for date")
        print("  python pricing_db_manager.py summary                       # Show database summary")
        print("")
        print("Examples:")
        print("  python pricing_db_manager.py add 2025-09-01 openai gpt-5 1.25 10.00")
        print("  python pricing_db_manager.py show 2025-09-28")
        return

    command = sys.argv[1]

    if command == "init":
        initialize_pricing_database()

    elif command == "add":
        if len(sys.argv) < 7:
            print("Usage: add DATE PROVIDER MODEL INPUT_PRICE OUTPUT_PRICE [SOURCE]")
            return

        date = sys.argv[2]
        provider = sys.argv[3]
        model = sys.argv[4]
        input_price = float(sys.argv[5])
        output_price = float(sys.argv[6])
        source = sys.argv[7] if len(sys.argv) > 7 else None

        add_historical_pricing(date, provider, model, input_price, output_price, source)

    elif command == "import":
        if len(sys.argv) < 3:
            print("Usage: import FILE.json")
            return

        import_pricing_from_json(sys.argv[2])

    elif command == "export":
        if len(sys.argv) < 3:
            print("Usage: export FILE.json [DATE]")
            return

        output_file = sys.argv[2]
        date = sys.argv[3] if len(sys.argv) > 3 else None

        export_pricing_to_json(output_file, date)

    elif command == "validate":
        validate_database()

    elif command == "show":
        if len(sys.argv) < 3:
            print("Usage: show DATE")
            return

        show_pricing_for_date(sys.argv[2])

    elif command == "summary":
        db = HistoricalPricingDB()
        summary = db.get_pricing_summary()
        print("Database Summary:")
        print(f"  Total dates: {summary['total_dates']}")
        print(f"  Total entries: {summary['total_pricing_entries']}")
        print(f"  Date range: {summary['date_range']}")
        print(f"  Providers: {', '.join(summary['providers'])}")

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()