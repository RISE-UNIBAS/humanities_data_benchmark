#!/usr/bin/env python3
"""Cost analysis utility for benchmark results."""

import json
import os
import sys
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional


def load_scoring_data(results_dir: str) -> List[Dict]:
    """Load all scoring.json files from results directory."""
    scoring_data = []

    if not os.path.exists(results_dir):
        print(f"Results directory not found: {results_dir}")
        return scoring_data

    for date_dir in os.listdir(results_dir):
        date_path = os.path.join(results_dir, date_dir)
        if not os.path.isdir(date_path):
            continue

        for test_dir in os.listdir(date_path):
            test_path = os.path.join(date_path, test_dir)
            scoring_file = os.path.join(test_path, "scoring.json")

            if os.path.exists(scoring_file):
                try:
                    with open(scoring_file, 'r') as f:
                        data = json.load(f)
                    if 'cost_summary' in data:
                        data['date'] = date_dir
                        data['test_id'] = test_dir
                        scoring_data.append(data)
                except Exception as e:
                    print(f"Error reading {scoring_file}: {e}")

    return scoring_data


def analyze_costs_by_provider(scoring_data: List[Dict]) -> Dict:
    """Analyze costs grouped by provider."""
    provider_costs = defaultdict(lambda: {
        'total_cost': 0.0,
        'total_tokens': 0,
        'total_requests': 0,
        'models': defaultdict(lambda: {
            'cost': 0.0,
            'tokens': 0,
            'requests': 0
        })
    })

    for data in scoring_data:
        if 'cost_summary' not in data:
            continue

        cost_info = data['cost_summary']
        provider = cost_info.get('provider', 'unknown')
        model = cost_info.get('model', 'unknown')

        provider_costs[provider]['total_cost'] += cost_info.get('total_cost_usd', 0.0)
        provider_costs[provider]['total_tokens'] += cost_info.get('total_tokens', 0)
        provider_costs[provider]['total_requests'] += cost_info.get('num_requests', 0)

        provider_costs[provider]['models'][model]['cost'] += cost_info.get('total_cost_usd', 0.0)
        provider_costs[provider]['models'][model]['tokens'] += cost_info.get('total_tokens', 0)
        provider_costs[provider]['models'][model]['requests'] += cost_info.get('num_requests', 0)

    return dict(provider_costs)


def analyze_costs_by_date(scoring_data: List[Dict]) -> Dict:
    """Analyze costs grouped by date."""
    date_costs = defaultdict(lambda: {
        'total_cost': 0.0,
        'total_tokens': 0,
        'total_requests': 0,
        'tests': 0
    })

    for data in scoring_data:
        if 'cost_summary' not in data:
            continue

        cost_info = data['cost_summary']
        date = data.get('date', 'unknown')

        date_costs[date]['total_cost'] += cost_info.get('total_cost_usd', 0.0)
        date_costs[date]['total_tokens'] += cost_info.get('total_tokens', 0)
        date_costs[date]['total_requests'] += cost_info.get('num_requests', 0)
        date_costs[date]['tests'] += 1

    return dict(date_costs)


def find_most_expensive_tests(scoring_data: List[Dict], limit: int = 10) -> List[Dict]:
    """Find the most expensive individual tests."""
    expensive_tests = []

    for data in scoring_data:
        if 'cost_summary' not in data:
            continue

        cost_info = data['cost_summary']
        expensive_tests.append({
            'test_id': data.get('test_id', 'unknown'),
            'date': data.get('date', 'unknown'),
            'provider': cost_info.get('provider', 'unknown'),
            'model': cost_info.get('model', 'unknown'),
            'cost': cost_info.get('total_cost_usd', 0.0),
            'tokens': cost_info.get('total_tokens', 0),
            'requests': cost_info.get('num_requests', 0)
        })

    expensive_tests.sort(key=lambda x: x['cost'], reverse=True)
    return expensive_tests[:limit]


def print_cost_summary(results_dir: str = "../results"):
    """Print comprehensive cost analysis."""
    print("=" * 80)
    print("BENCHMARK COST ANALYSIS")
    print("=" * 80)

    scoring_data = load_scoring_data(results_dir)

    if not scoring_data:
        print("No cost data found.")
        return

    print(f"Found cost data for {len(scoring_data)} tests")

    # Overall totals
    total_cost = sum(data['cost_summary'].get('total_cost_usd', 0.0)
                    for data in scoring_data if 'cost_summary' in data)
    total_tokens = sum(data['cost_summary'].get('total_tokens', 0)
                      for data in scoring_data if 'cost_summary' in data)
    total_requests = sum(data['cost_summary'].get('num_requests', 0)
                        for data in scoring_data if 'cost_summary' in data)

    print(f"\nOVERALL TOTALS:")
    print(f"Total Cost: ${total_cost:.4f}")
    print(f"Total Tokens: {total_tokens:,}")
    print(f"Total Requests: {total_requests:,}")
    print(f"Average cost per test: ${total_cost/len(scoring_data):.4f}")

    # Cost by provider
    print("\n" + "=" * 50)
    print("COSTS BY PROVIDER")
    print("=" * 50)

    provider_costs = analyze_costs_by_provider(scoring_data)
    for provider, data in sorted(provider_costs.items(),
                                key=lambda x: x[1]['total_cost'], reverse=True):
        print(f"\n{provider.upper()}:")
        print(f"  Total Cost: ${data['total_cost']:.4f}")
        print(f"  Total Tokens: {data['total_tokens']:,}")
        print(f"  Total Requests: {data['total_requests']:,}")

        print("  Models:")
        for model, model_data in sorted(data['models'].items(),
                                       key=lambda x: x[1]['cost'], reverse=True):
            print(f"    {model}: ${model_data['cost']:.4f} "
                  f"({model_data['tokens']:,} tokens, {model_data['requests']} requests)")

    # Most expensive tests
    print("\n" + "=" * 50)
    print("MOST EXPENSIVE TESTS (TOP 10)")
    print("=" * 50)

    expensive_tests = find_most_expensive_tests(scoring_data, 10)
    for i, test in enumerate(expensive_tests, 1):
        print(f"{i:2d}. {test['test_id']} ({test['date']}) - {test['provider']}/{test['model']}")
        print(f"     Cost: ${test['cost']:.4f}, Tokens: {test['tokens']:,}, Requests: {test['requests']}")

    # Cost by date
    print("\n" + "=" * 50)
    print("COSTS BY DATE")
    print("=" * 50)

    date_costs = analyze_costs_by_date(scoring_data)
    for date, data in sorted(date_costs.items()):
        print(f"{date}: ${data['total_cost']:.4f} "
              f"({data['tests']} tests, {data['total_tokens']:,} tokens)")


def save_cost_report(results_dir: str = "../results", output_file: str = "../cost_report.json"):
    """Save detailed cost analysis to JSON file."""
    scoring_data = load_scoring_data(results_dir)

    if not scoring_data:
        return

    report = {
        'generated_at': datetime.now().isoformat(),
        'total_tests': len(scoring_data),
        'summary': {
            'total_cost_usd': sum(data['cost_summary'].get('total_cost_usd', 0.0)
                                 for data in scoring_data if 'cost_summary' in data),
            'total_tokens': sum(data['cost_summary'].get('total_tokens', 0)
                               for data in scoring_data if 'cost_summary' in data),
            'total_requests': sum(data['cost_summary'].get('num_requests', 0)
                                 for data in scoring_data if 'cost_summary' in data)
        },
        'by_provider': analyze_costs_by_provider(scoring_data),
        'by_date': analyze_costs_by_date(scoring_data),
        'most_expensive_tests': find_most_expensive_tests(scoring_data, 20),
        'raw_data': scoring_data
    }

    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    print(f"Detailed cost report saved to: {output_file}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        results_dir = sys.argv[1]
    else:
        results_dir = "../results"

    print_cost_summary(results_dir)
    save_cost_report(results_dir)