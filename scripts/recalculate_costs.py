#!/usr/bin/env python3
"""Utility to recalculate costs in existing scoring.json files using current pricing."""

import json
import os
import sys
from pathlib import Path
from simple_ai_clients import CostCalculator


def recalculate_scoring_file_cost(scoring_file_path: str, use_historical: bool = True) -> dict:
    """Recalculate cost for a single scoring.json file."""
    try:
        with open(scoring_file_path, 'r') as f:
            data = json.load(f)

        if 'cost_summary' not in data:
            return {'status': 'no_cost_summary', 'message': 'No cost_summary found'}

        cost_summary = data['cost_summary']

        # Extract required information
        provider = cost_summary.get('provider')
        model = cost_summary.get('model')
        input_tokens = cost_summary.get('total_input_tokens', 0)
        output_tokens = cost_summary.get('total_output_tokens', 0)

        if not provider or not model:
            return {'status': 'missing_info', 'message': 'Missing provider or model information'}

        # Extract date from file path (results/YYYY-MM-DD/TEST_ID/scoring.json)
        path_parts = scoring_file_path.split(os.sep)
        date = None
        for part in path_parts:
            if len(part) == 10 and part.count('-') == 2:  # YYYY-MM-DD format
                try:
                    datetime.fromisoformat(part)  # Validate date format
                    date = part
                    break
                except:
                    continue

        # Calculate new cost using historical pricing if available
        old_cost = cost_summary.get('total_cost_usd', 0.0)

        if use_historical and date:
            new_cost = CostCalculator.calculate_cost_for_date(date, provider, model, input_tokens, output_tokens)
            calculation_method = f"historical pricing for {date}"
        else:
            new_cost = CostCalculator.calculate_cost(provider, model, input_tokens, output_tokens)
            calculation_method = "current pricing"

        # Update the cost
        data['cost_summary']['total_cost_usd'] = round(new_cost, 4)

        # Save updated file
        with open(scoring_file_path, 'w') as f:
            json.dump(data, f, indent=4)

        return {
            'status': 'success',
            'old_cost': old_cost,
            'new_cost': new_cost,
            'change': new_cost - old_cost,
            'change_percent': ((new_cost - old_cost) / old_cost * 100) if old_cost > 0 else 0,
            'calculation_method': calculation_method,
            'date': date
        }

    except Exception as e:
        return {'status': 'error', 'message': str(e)}


def recalculate_all_costs(results_dir: str = "../results", dry_run: bool = False):
    """Recalculate costs for all scoring.json files in results directory."""

    if not os.path.exists(results_dir):
        print(f"Results directory not found: {results_dir}")
        return

    scoring_files = []

    # Find all scoring.json files
    for root, dirs, files in os.walk(results_dir):
        if 'scoring.json' in files:
            scoring_files.append(os.path.join(root, 'scoring.json'))

    if not scoring_files:
        print("No scoring.json files found.")
        return

    print(f"Found {len(scoring_files)} scoring.json files")
    print("=" * 80)

    updated_count = 0
    total_old_cost = 0.0
    total_new_cost = 0.0
    errors = []

    for scoring_file in sorted(scoring_files):
        # Extract test ID from path for display
        path_parts = scoring_file.split(os.sep)
        test_id = path_parts[-2] if len(path_parts) >= 2 else 'unknown'
        date = path_parts[-3] if len(path_parts) >= 3 else 'unknown'

        print(f"Processing {date}/{test_id}...", end=' ')

        if dry_run:
            # Just check what would change without writing
            try:
                with open(scoring_file, 'r') as f:
                    data = json.load(f)

                if 'cost_summary' in data:
                    cost_summary = data['cost_summary']
                    provider = cost_summary.get('provider')
                    model = cost_summary.get('model')
                    input_tokens = cost_summary.get('total_input_tokens', 0)
                    output_tokens = cost_summary.get('total_output_tokens', 0)
                    old_cost = cost_summary.get('total_cost_usd', 0.0)

                    if provider and model:
                        new_cost = CostCalculator.calculate_cost(provider, model, input_tokens, output_tokens)
                        change_percent = ((new_cost - old_cost) / old_cost * 100) if old_cost > 0 else 0
                        print(f"${old_cost:.4f} → ${new_cost:.4f} ({change_percent:+.1f}%)")
                    else:
                        print("Missing provider/model info")
                else:
                    print("No cost_summary")
            except Exception as e:
                print(f"Error: {e}")

        else:
            result = recalculate_scoring_file_cost(scoring_file)

            if result['status'] == 'success':
                old_cost = result['old_cost']
                new_cost = result['new_cost']
                change_percent = result['change_percent']

                total_old_cost += old_cost
                total_new_cost += new_cost
                updated_count += 1

                print(f"${old_cost:.4f} → ${new_cost:.4f} ({change_percent:+.1f}%)")

            elif result['status'] == 'no_cost_summary':
                print("No cost_summary")
            elif result['status'] == 'missing_info':
                print("Missing provider/model info")
            else:
                print(f"Error: {result['message']}")
                errors.append((scoring_file, result['message']))

    print("=" * 80)

    if dry_run:
        print("DRY RUN - No files were modified")
    else:
        print(f"Updated {updated_count} files")
        if updated_count > 0:
            total_change = total_new_cost - total_old_cost
            total_change_percent = (total_change / total_old_cost * 100) if total_old_cost > 0 else 0
            print(f"Total cost change: ${total_old_cost:.4f} → ${total_new_cost:.4f} ({total_change_percent:+.1f}%)")

        if errors:
            print(f"\nErrors encountered in {len(errors)} files:")
            for file_path, error_msg in errors:
                print(f"  {file_path}: {error_msg}")


def recalculate_specific_test(test_id: str, date: str = None):
    """Recalculate cost for a specific test."""
    results_dir = "../results"

    if date:
        scoring_file = os.path.join(results_dir, date, test_id, "scoring.json")
    else:
        # Find the most recent
        test_dirs = []
        if os.path.exists(results_dir):
            for date_dir in os.listdir(results_dir):
                test_path = os.path.join(results_dir, date_dir, test_id, "scoring.json")
                if os.path.exists(test_path):
                    test_dirs.append((date_dir, test_path))

        if not test_dirs:
            print(f"No results found for test {test_id}")
            return

        # Use most recent
        test_dirs.sort(reverse=True)
        date, scoring_file = test_dirs[0]

    if not os.path.exists(scoring_file):
        print(f"Scoring file not found: {scoring_file}")
        return

    print(f"Recalculating cost for {test_id} ({date})...")

    result = recalculate_scoring_file_cost(scoring_file)

    if result['status'] == 'success':
        print(f"✓ Updated: ${result['old_cost']:.4f} → ${result['new_cost']:.4f} ({result['change_percent']:+.1f}%)")
    else:
        print(f"❌ Error: {result.get('message', result['status'])}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python recalculate_costs.py all [--dry-run]     # Recalculate all scoring files")
        print("  python recalculate_costs.py T0130 [date]        # Recalculate specific test")
        print("  python recalculate_costs.py --help              # Show this help")
        sys.exit(1)

    command = sys.argv[1]

    if command == "--help":
        print(__doc__)
    elif command == "all":
        dry_run = "--dry-run" in sys.argv
        recalculate_all_costs(dry_run=dry_run)
    elif command.startswith("T"):
        # Specific test
        date = sys.argv[2] if len(sys.argv) > 2 else None
        recalculate_specific_test(command, date)
    else:
        print(f"Unknown command: {command}")
        print("Use --help for usage information")