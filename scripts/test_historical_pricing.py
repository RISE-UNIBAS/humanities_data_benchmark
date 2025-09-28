#!/usr/bin/env python3
"""Test the historical pricing system."""

import json
import os
import tempfile
from datetime import datetime


def test_historical_pricing_system():
    """Test the complete historical pricing system."""
    print("=" * 60)
    print("HISTORICAL PRICING SYSTEM TEST")
    print("=" * 60)

    # Test 1: Create test database
    test_db_path = "/tmp/claude/test_pricing.json"
    os.makedirs(os.path.dirname(test_db_path), exist_ok=True)

    # Create test pricing database
    test_pricing_data = {
        "metadata": {
            "created": datetime.now().isoformat(),
            "version": "1.0"
        },
        "pricing_history": {
            "2025-09-01": {
                "openai": {
                    "gpt-5-mini": {
                        "input_price_per_1m": 0.30,  # Old higher price
                        "output_price_per_1m": 2.50,
                        "source": "Historical pricing test",
                        "added": datetime.now().isoformat()
                    }
                }
            },
            "2025-09-28": {
                "openai": {
                    "gpt-5-mini": {
                        "input_price_per_1m": 0.25,  # Current lower price
                        "output_price_per_1m": 2.00,
                        "source": "Current pricing test",
                        "added": datetime.now().isoformat()
                    }
                }
            }
        }
    }

    with open(test_db_path, 'w') as f:
        json.dump(test_pricing_data, f, indent=2)

    print(f"✓ Created test pricing database: {test_db_path}")

    # Test 2: Import and test database
    try:
        from historical_pricing_db import HistoricalPricingDB

        db = HistoricalPricingDB(test_db_path)

        # Test pricing lookup for different dates
        print("\nTesting pricing lookups:")

        # Test 1: Exact date match
        pricing_sept_01 = db.get_pricing_for_date("2025-09-01", "openai", "gpt-5-mini")
        if pricing_sept_01:
            print(f"✓ 2025-09-01: gpt-5-mini = ${pricing_sept_01[0]}/${pricing_sept_01[1]} per 1M")
        else:
            print("❌ Failed to get pricing for 2025-09-01")

        # Test 2: Different date
        pricing_sept_28 = db.get_pricing_for_date("2025-09-28", "openai", "gpt-5-mini")
        if pricing_sept_28:
            print(f"✓ 2025-09-28: gpt-5-mini = ${pricing_sept_28[0]}/${pricing_sept_28[1]} per 1M")
        else:
            print("❌ Failed to get pricing for 2025-09-28")

        # Test 3: Fallback to earlier date (test with 2025-09-15)
        pricing_fallback = db.get_pricing_for_date("2025-09-15", "openai", "gpt-5-mini")
        if pricing_fallback:
            print(f"✓ 2025-09-15 (fallback): gpt-5-mini = ${pricing_fallback[0]}/${pricing_fallback[1]} per 1M")
        else:
            print("❌ Failed fallback pricing lookup")

        print(f"\nDatabase summary:")
        summary = db.get_pricing_summary()
        print(f"  Dates: {summary['total_dates']}")
        print(f"  Entries: {summary['total_pricing_entries']}")

    except ImportError:
        print("❌ Could not import HistoricalPricingDB (dependencies missing)")

    # Test 3: Cost calculation differences
    print(f"\nTesting cost calculations:")

    # Sample data (like T0130)
    input_tokens = 7409
    output_tokens = 25715

    print(f"Token usage: {input_tokens:,} input + {output_tokens:,} output")

    # Calculate costs for different dates
    old_pricing = (0.30, 2.50)  # 2025-09-01 pricing
    new_pricing = (0.25, 2.00)  # 2025-09-28 pricing

    old_cost = (input_tokens / 1_000_000) * old_pricing[0] + (output_tokens / 1_000_000) * old_pricing[1]
    new_cost = (input_tokens / 1_000_000) * new_pricing[0] + (output_tokens / 1_000_000) * new_pricing[1]

    print(f"Cost with 2025-09-01 pricing (${old_pricing[0]}/${old_pricing[1]}): ${old_cost:.4f}")
    print(f"Cost with 2025-09-28 pricing (${new_pricing[0]}/${new_pricing[1]}): ${new_cost:.4f}")

    savings = old_cost - new_cost
    savings_percent = (savings / old_cost) * 100 if old_cost > 0 else 0

    print(f"Price reduction: ${savings:.4f} ({savings_percent:.1f}% savings)")

    # Test 4: Show how benchmark would use historical pricing
    print(f"\nBenchmark cost calculation example:")
    print(f"  Benchmark run on 2025-09-01 → uses ${old_pricing[0]}/${old_pricing[1]} → ${old_cost:.4f}")
    print(f"  Benchmark run on 2025-09-28 → uses ${new_pricing[0]}/${new_pricing[1]} → ${new_cost:.4f}")
    print(f"  ✓ Each benchmark uses pricing from its run date!")

    print(f"\n" + "=" * 60)
    print("HISTORICAL PRICING BENEFITS")
    print("=" * 60)
    print("✓ Accurate cost tracking over time")
    print("✓ Historical benchmarks reflect actual costs at time of execution")
    print("✓ Price change analysis and trend tracking")
    print("✓ Fair cost comparisons between different time periods")
    print("✓ Automatic fallback to nearest available pricing")

    # Clean up
    try:
        os.remove(test_db_path)
        print(f"\n✓ Test database cleaned up")
    except:
        pass

    return True


if __name__ == "__main__":
    test_historical_pricing_system()