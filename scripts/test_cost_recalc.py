#!/usr/bin/env python3
"""Test cost recalculation for T0130."""

import json
import os

# Standalone CostCalculator for testing
class TestCostCalculator:
    PRICING = {
        'openai': {
            'gpt-5-mini': (0.25, 2.00),  # Correct pricing
        }
    }

    @classmethod
    def calculate_cost(cls, provider, model, input_tokens, output_tokens):
        if provider not in cls.PRICING or model not in cls.PRICING[provider]:
            return 0.0
        input_price, output_price = cls.PRICING[provider][model]
        return (input_tokens / 1_000_000) * input_price + (output_tokens / 1_000_000) * output_price

def test_t0130_recalculation():
    scoring_file = "../results/2025-09-28/T0130/scoring.json"

    if not os.path.exists(scoring_file):
        print(f"File not found: {scoring_file}")
        return

    # Read current data
    with open(scoring_file, 'r') as f:
        data = json.load(f)

    if 'cost_summary' not in data:
        print("No cost_summary found")
        return

    cost_summary = data['cost_summary']

    print("T0130 Cost Recalculation Test")
    print("=" * 40)
    print(f"Provider: {cost_summary['provider']}")
    print(f"Model: {cost_summary['model']}")
    print(f"Input tokens: {cost_summary['total_input_tokens']:,}")
    print(f"Output tokens: {cost_summary['total_output_tokens']:,}")
    print(f"Current cost in file: ${cost_summary['total_cost_usd']:.4f}")

    # Calculate correct cost
    correct_cost = TestCostCalculator.calculate_cost(
        cost_summary['provider'],
        cost_summary['model'],
        cost_summary['total_input_tokens'],
        cost_summary['total_output_tokens']
    )

    print(f"Correct cost should be: ${correct_cost:.4f}")

    if abs(cost_summary['total_cost_usd'] - correct_cost) > 0.001:
        savings = cost_summary['total_cost_usd'] - correct_cost
        savings_percent = (savings / cost_summary['total_cost_usd']) * 100
        print(f"❌ Cost is incorrect!")
        print(f"   Savings: ${savings:.4f} ({savings_percent:.1f}%)")

        # Show what would be updated
        print("\nProposed fix:")
        print(f"   Change total_cost_usd from {cost_summary['total_cost_usd']:.4f} to {correct_cost:.4f}")

        return {
            'needs_fix': True,
            'old_cost': cost_summary['total_cost_usd'],
            'new_cost': correct_cost,
            'file_path': scoring_file
        }
    else:
        print("✓ Cost is correct!")
        return {'needs_fix': False}

if __name__ == "__main__":
    result = test_t0130_recalculation()

    if result and result.get('needs_fix'):
        print(f"\nTo fix this, the cost calculation should happen when scoring.json is created,")
        print(f"not reuse old API response costs that may have used incorrect pricing.")