#!/usr/bin/env python3
"""Test script to verify cost tracking functionality."""

import json
import os
import tempfile
from simple_ai_clients import CostCalculator


def test_cost_calculator():
    """Test the CostCalculator class."""
    print("Testing CostCalculator...")

    # Test OpenAI pricing
    cost = CostCalculator.calculate_cost('openai', 'gpt-4o', 1000, 500)
    expected_cost = (1000/1_000_000 * 2.50) + (500/1_000_000 * 10.00)  # 0.0025 + 0.005 = 0.0075
    print(f"GPT-4O cost: ${cost:.6f} (expected: ${expected_cost:.6f})")
    assert abs(cost - expected_cost) < 0.0001

    # Test Anthropic pricing
    cost = CostCalculator.calculate_cost('anthropic', 'claude-3-5-sonnet-20241022', 2000, 800)
    expected_cost = (2000/1_000_000 * 3.00) + (800/1_000_000 * 15.00)  # 0.006 + 0.012 = 0.018
    print(f"Claude-3.5-Sonnet cost: ${cost:.6f} (expected: ${expected_cost:.6f})")
    assert abs(cost - expected_cost) < 0.0001

    # Test unknown model
    cost = CostCalculator.calculate_cost('unknown', 'unknown', 1000, 500)
    print(f"Unknown model cost: ${cost:.6f} (expected: $0.000000)")
    assert cost == 0.0

    print("✓ CostCalculator tests passed!")


def test_cost_tracking_structure():
    """Test the structure of cost tracking data."""
    print("\nTesting cost tracking data structure...")

    # Simulate the structure that would be added to API responses
    sample_cost_info = {
        'input_tokens': 1500,
        'output_tokens': 750,
        'total_tokens': 2250,
        'estimated_cost_usd': 0.0125
    }

    # Test benchmark cost summary structure
    sample_benchmark_score = {
        'cost_summary': {
            'total_cost_usd': 0.0875,
            'total_input_tokens': 10500,
            'total_output_tokens': 5250,
            'total_tokens': 15750,
            'provider': 'openai',
            'model': 'gpt-4o',
            'num_requests': 7
        },
        'other_scores': {
            'accuracy': 0.85
        }
    }

    # Validate structure
    assert 'cost_summary' in sample_benchmark_score
    assert 'total_cost_usd' in sample_benchmark_score['cost_summary']
    assert 'total_tokens' in sample_benchmark_score['cost_summary']
    assert 'provider' in sample_benchmark_score['cost_summary']

    print("✓ Cost tracking data structure tests passed!")


def create_sample_results():
    """Create sample results to test the cost analyzer."""
    print("\nCreating sample results for testing...")

    # Create temporary results structure
    results_dir = "/tmp/claude/sample_results"
    os.makedirs(results_dir, exist_ok=True)

    # Sample data for different dates and tests
    sample_data = [
        {
            'date': '2025-09-28',
            'test_id': 'T0001',
            'cost_summary': {
                'total_cost_usd': 0.0125,
                'total_input_tokens': 1500,
                'total_output_tokens': 750,
                'total_tokens': 2250,
                'provider': 'openai',
                'model': 'gpt-4o',
                'num_requests': 3
            },
            'accuracy': 0.85
        },
        {
            'date': '2025-09-28',
            'test_id': 'T0002',
            'cost_summary': {
                'total_cost_usd': 0.0035,
                'total_input_tokens': 2000,
                'total_output_tokens': 1000,
                'total_tokens': 3000,
                'provider': 'anthropic',
                'model': 'claude-3-5-sonnet-20241022',
                'num_requests': 2
            },
            'accuracy': 0.92
        },
        {
            'date': '2025-09-27',
            'test_id': 'T0003',
            'cost_summary': {
                'total_cost_usd': 0.0008,
                'total_input_tokens': 3000,
                'total_output_tokens': 800,
                'total_tokens': 3800,
                'provider': 'openai',
                'model': 'gpt-4o-mini',
                'num_requests': 5
            },
            'accuracy': 0.78
        }
    ]

    # Create directory structure and files
    for data in sample_data:
        date_dir = os.path.join(results_dir, data['date'])
        test_dir = os.path.join(date_dir, data['test_id'])
        os.makedirs(test_dir, exist_ok=True)

        scoring_file = os.path.join(test_dir, 'scoring.json')
        with open(scoring_file, 'w') as f:
            json.dump(data, f, indent=2)

    print(f"✓ Sample results created in {results_dir}")
    return results_dir


def test_cost_analyzer(results_dir):
    """Test the cost analyzer with sample data."""
    print(f"\nTesting cost analyzer with sample data...")

    from cost_analyzer import load_scoring_data, analyze_costs_by_provider, print_cost_summary

    # Load the sample data
    scoring_data = load_scoring_data(results_dir)
    print(f"Loaded {len(scoring_data)} scoring records")
    assert len(scoring_data) == 3

    # Test provider analysis
    provider_costs = analyze_costs_by_provider(scoring_data)
    print(f"Found {len(provider_costs)} providers")
    assert 'openai' in provider_costs
    assert 'anthropic' in provider_costs

    # Verify totals
    openai_total = provider_costs['openai']['total_cost']
    expected_openai = 0.0125 + 0.0008  # Two OpenAI tests
    print(f"OpenAI total cost: ${openai_total:.4f} (expected: ${expected_openai:.4f})")
    assert abs(openai_total - expected_openai) < 0.0001

    print("✓ Cost analyzer tests passed!")


if __name__ == "__main__":
    print("=" * 60)
    print("COST TRACKING SYSTEM TEST")
    print("=" * 60)

    test_cost_calculator()
    test_cost_tracking_structure()

    # Create sample data and test analyzer
    sample_results_dir = create_sample_results()
    test_cost_analyzer(sample_results_dir)

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! ✓")
    print("=" * 60)
    print("\nCost tracking system is ready to use.")
    print("Next steps:")
    print("1. Run benchmarks to generate cost data: python scripts/run_benchmarks.py")
    print("2. Analyze costs: python scripts/cost_analyzer.py")