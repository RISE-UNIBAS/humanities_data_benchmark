#!/usr/bin/env python3
"""CLI tool to inject cost calculations into existing test results.

This tool scans test results directories and recalculates costs for tests
that have missing or zero cost data, using the current pricing information.

Usage:
    # Bulk mode - scan all tests
    python scripts/inject_costs.py                     # Interactive mode
    python scripts/inject_costs.py --results           # Scan results/ only
    python scripts/inject_costs.py --test-runs         # Scan test_runs/ only
    python scripts/inject_costs.py --auto-update       # Update without prompting
    python scripts/inject_costs.py --dry-run           # Show what would be updated

    # Single test mode - calculate specific test
    python scripts/inject_costs.py --test-id T0614 --date 2026-02-10
    python scripts/inject_costs.py --test-id T0614 --date 2026-02-10 --dry-run
    python scripts/inject_costs.py --test-id ADHOC_20260106_154125 --date 2026-01-06 --test-runs
"""

import sys
import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent

# Add scripts directory to path for imports
sys.path.insert(0, str(SCRIPT_DIR))

# Change to scripts directory for relative path imports to work
original_cwd = os.getcwd()
os.chdir(SCRIPT_DIR)

from ai_client.pricing import calculate_cost, set_pricing_file
from data_loader import read_file, write_file

# Set custom pricing file (same as in __init__.py)
# Try both possible locations
if (SCRIPT_DIR / "data" / "pricing.json").exists():
    set_pricing_file(str(SCRIPT_DIR / "data" / "pricing.json"))
elif (SCRIPT_DIR / "ndr_export" / "pricing.json").exists():
    set_pricing_file(str(SCRIPT_DIR / "ndr_export" / "pricing.json"))
else:
    print(f"{Colors.YELLOW}[*] Warning: Custom pricing file not found. Using default pricing.{Colors.END}")


# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}")
    print(f"  {text}")
    print(f"{'=' * 80}{Colors.END}\n")


def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}[+] {text}{Colors.END}")


def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}[!] {text}{Colors.END}")


def print_info(text: str):
    """Print info message."""
    print(f"{Colors.CYAN}[i] {text}{Colors.END}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}[*] {text}{Colors.END}")


def get_yes_no(prompt: str, default: bool = True) -> bool:
    """Get yes/no input from user."""
    default_str = "Y/n" if default else "y/N"
    full_prompt = f"{Colors.CYAN}{prompt} [{default_str}]:{Colors.END} "

    max_attempts = 10
    attempts = 0

    while attempts < max_attempts:
        try:
            value = input(full_prompt).strip().lower()

            if not value:
                return default

            if value in ['y', 'yes']:
                return True
            elif value in ['n', 'no']:
                return False
            else:
                print_error("Please enter 'y' or 'n'.")
                attempts += 1
        except EOFError:
            return default
        except KeyboardInterrupt:
            raise

    print_warning(f"Max attempts reached, using default: {'yes' if default else 'no'}")
    return default


def find_test_runs(base_dir: Path) -> List[Path]:
    """Find all test runs with scoring.json files."""
    test_runs = []

    if not base_dir.exists():
        print_warning(f"Directory not found: {base_dir}")
        return test_runs

    # Scan for scoring.json files
    for scoring_file in base_dir.rglob("scoring.json"):
        test_runs.append(scoring_file.parent)

    return sorted(test_runs)


def analyze_test_run(test_dir: Path) -> Dict:
    """Analyze a test run to determine if it needs cost updates."""
    scoring_file = test_dir / "scoring.json"

    result = {
        'path': test_dir,
        'test_id': test_dir.name,
        'date': test_dir.parent.name,
        'needs_update': False,
        'reason': None,
        'scoring_exists': False,
        'cost_summary': None,
        'request_files': [],
        'requests_needing_update': [],
        'cannot_calculate': []
    }

    # Check if scoring.json exists and has cost data
    if scoring_file.exists():
        result['scoring_exists'] = True
        try:
            scoring_data = json.loads(read_file(str(scoring_file)))
            cost_summary = scoring_data.get('cost_summary', {})
            result['cost_summary'] = cost_summary

            # Check if cost_summary is missing or all costs are zero
            if not cost_summary:
                result['needs_update'] = True
                result['reason'] = "Missing cost_summary"
            elif cost_summary.get('total_cost_usd', 0) == 0:
                result['needs_update'] = True
                result['reason'] = "Zero total cost"
        except Exception as e:
            print_warning(f"Error reading scoring file {scoring_file}: {e}")
            return result

    # Find all request files
    request_files = list(test_dir.glob("request_*.json"))
    result['request_files'] = request_files

    # Analyze each request file
    for request_file in request_files:
        try:
            request_data = json.loads(read_file(str(request_file)))
            usage = request_data.get('usage', {})

            # Check if cost data is missing or zero
            input_cost = usage.get('input_cost_usd')
            output_cost = usage.get('output_cost_usd')
            estimated_cost = usage.get('estimated_cost_usd')

            if input_cost is None or output_cost is None or estimated_cost is None or estimated_cost == 0:
                # Check if we can calculate costs
                provider = request_data.get('provider', '')
                model = request_data.get('model', '')
                input_tokens = usage.get('input_tokens', 0)
                output_tokens = usage.get('output_tokens', 0)

                if not provider or not model or (input_tokens == 0 and output_tokens == 0):
                    result['cannot_calculate'].append({
                        'file': request_file.name,
                        'reason': f"Missing data (provider={provider}, model={model}, tokens={input_tokens}+{output_tokens})"
                    })
                else:
                    # Try to calculate cost to see if pricing exists
                    cost_result = calculate_cost(provider, model, input_tokens, output_tokens)
                    if cost_result:
                        result['needs_update'] = True
                        result['requests_needing_update'].append({
                            'file': request_file.name,
                            'provider': provider,
                            'model': model,
                            'input_tokens': input_tokens,
                            'output_tokens': output_tokens,
                            'new_cost': cost_result
                        })
                    else:
                        result['cannot_calculate'].append({
                            'file': request_file.name,
                            'reason': f"No pricing data for {provider}/{model}"
                        })
        except Exception as e:
            print_warning(f"Error reading request file {request_file}: {e}")
            continue

    return result


def update_test_run(analysis: Dict, dry_run: bool = False) -> bool:
    """Update a test run with recalculated costs."""
    if not analysis['needs_update']:
        return False

    test_dir = analysis['path']
    scoring_file = test_dir / "scoring.json"

    if dry_run:
        print_info(f"[DRY RUN] Would update: {test_dir}")
        return True

    try:
        # Update each request file
        updated_requests = []
        for req_info in analysis['requests_needing_update']:
            request_file = test_dir / req_info['file']
            request_data = json.loads(read_file(str(request_file)))

            # Update usage with new costs
            input_cost, output_cost, estimated_cost = req_info['new_cost']
            usage = request_data.get('usage', {})
            usage['input_cost_usd'] = input_cost
            usage['output_cost_usd'] = output_cost
            usage['estimated_cost_usd'] = estimated_cost
            request_data['usage'] = usage

            # Save updated request file
            write_file(str(request_file), request_data)
            updated_requests.append(request_data)

        # Recalculate cost_summary for scoring.json
        total_input_tokens = 0
        total_output_tokens = 0
        total_input_cost = 0.0
        total_output_cost = 0.0
        total_cost = 0.0

        # Process all request files (including ones that already had costs)
        for request_file in analysis['request_files']:
            try:
                request_data = json.loads(read_file(str(request_file)))
                usage = request_data.get('usage', {})

                total_input_tokens += usage.get('input_tokens', 0)
                total_output_tokens += usage.get('output_tokens', 0)
                total_input_cost += usage.get('input_cost_usd', 0)
                total_output_cost += usage.get('output_cost_usd', 0)
                total_cost += usage.get('estimated_cost_usd', 0)
            except Exception as e:
                print_warning(f"Error processing {request_file.name}: {e}")
                continue

        # Update scoring.json
        scoring_data = json.loads(read_file(str(scoring_file)))
        scoring_data['cost_summary'] = {
            'total_input_tokens': total_input_tokens,
            'total_output_tokens': total_output_tokens,
            'total_tokens': total_input_tokens + total_output_tokens,
            'input_cost_usd': total_input_cost,
            'output_cost_usd': total_output_cost,
            'total_cost_usd': total_cost
        }
        write_file(str(scoring_file), scoring_data)

        print_success(f"Updated {test_dir.parent.name}/{test_dir.name} - ${total_cost:.4f}")
        return True

    except Exception as e:
        print_error(f"Failed to update {test_dir}: {e}")
        return False


def display_analysis_summary(analyses: List[Dict], directory_name: str):
    """Display summary of analysis results."""
    print_header(f"Analysis Results for {directory_name}")

    needs_update = [a for a in analyses if a['needs_update']]
    cannot_calculate = [a for a in analyses if a['cannot_calculate']]

    print(f"{Colors.BOLD}Total test runs scanned:{Colors.END} {len(analyses)}")
    print(f"{Colors.YELLOW}{Colors.BOLD}Needs cost update:{Colors.END} {len(needs_update)}")
    print(f"{Colors.RED}{Colors.BOLD}Cannot calculate (missing pricing):{Colors.END} {len(cannot_calculate)}")
    print(f"{Colors.GREEN}{Colors.BOLD}Up to date:{Colors.END} {len(analyses) - len(needs_update)}\n")

    if needs_update:
        print(f"{Colors.BOLD}Test runs needing updates:{Colors.END}")
        for analysis in needs_update:
            test_path = f"{analysis['date']}/{analysis['test_id']}"
            num_requests = len(analysis['requests_needing_update'])
            reason = analysis['reason'] or f"{num_requests} requests need cost data"
            print(f"  • {test_path}: {reason}")
        print()

    if cannot_calculate:
        print(f"{Colors.RED}{Colors.BOLD}Test runs with missing pricing data:{Colors.END}")
        for analysis in cannot_calculate:
            test_path = f"{analysis['date']}/{analysis['test_id']}"
            print(f"  • {test_path}:")
            for item in analysis['cannot_calculate']:
                print(f"    - {item['file']}: {item['reason']}")
        print()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Inject cost calculations into existing test results"
    )
    parser.add_argument(
        '--results',
        action='store_true',
        help='Scan only the results/ directory (official results)'
    )
    parser.add_argument(
        '--test-runs',
        action='store_true',
        help='Scan only the test_runs/ directory (adhoc results)'
    )
    parser.add_argument(
        '--test-id',
        type=str,
        help='Calculate costs for a specific test ID (e.g., T0614 or ADHOC_20260106_154125)'
    )
    parser.add_argument(
        '--date',
        type=str,
        help='Date directory for the test (e.g., 2026-02-10). When used alone, processes all tests for that date.'
    )
    parser.add_argument(
        '--auto-update',
        action='store_true',
        help='Automatically update without prompting for confirmation'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be updated without making changes'
    )

    args = parser.parse_args()

    # Handle single test ID mode
    if args.test_id:
        if not args.date:
            print_error("--date is required when using --test-id")
            print_info("Example: --test-id T0614 --date 2026-02-10")
            return

        # Determine which directory to look in
        if args.test_runs:
            base_dir = PROJECT_ROOT / 'test_runs'
        else:
            # Default to results/
            base_dir = PROJECT_ROOT / 'results'

        test_dir = base_dir / args.date / args.test_id

        if not test_dir.exists():
            print_error(f"Test directory not found: {test_dir}")
            return

        try:
            print_header(f"Cost Injection for {args.test_id}")
            print_info(f"Test directory: {test_dir}")
            print()

            # Analyze the test
            analysis = analyze_test_run(test_dir)

            # Show details
            if not analysis['needs_update']:
                print_success(f"Test {args.test_id} already has cost data!")
                if analysis['cost_summary']:
                    print_info(f"Total cost: ${analysis['cost_summary'].get('total_cost_usd', 0):.4f}")
                return

            # Show what needs updating
            print(f"{Colors.BOLD}Status:{Colors.END}")
            print(f"  Requests needing update: {len(analysis['requests_needing_update'])}")
            print(f"  Cannot calculate: {len(analysis['cannot_calculate'])}")
            print()

            if analysis['requests_needing_update']:
                print(f"{Colors.BOLD}Requests that can be updated:{Colors.END}")
                for req in analysis['requests_needing_update']:
                    cost = req['new_cost'][2]  # estimated_cost_usd
                    print(f"  • {req['file']}: ${cost:.4f} ({req['provider']}/{req['model']})")
                print()

            if analysis['cannot_calculate']:
                print(f"{Colors.RED}{Colors.BOLD}Requests with missing pricing:{Colors.END}")
                for item in analysis['cannot_calculate']:
                    print(f"  • {item['file']}: {item['reason']}")
                print()

            # Update if requested
            if args.dry_run:
                print_info("[DRY RUN] Would update this test run")
            elif args.auto_update or get_yes_no(f"Update test {args.test_id} with cost data?", default=True):
                if update_test_run(analysis, dry_run=False):
                    print_success(f"Successfully updated {args.test_id}!")
                else:
                    print_error(f"Failed to update {args.test_id}")
            else:
                print_info("Update cancelled.")

        except Exception as e:
            print_error(f"Error processing test: {e}")
            import traceback
            traceback.print_exc()

        return

    # Determine which directories to scan (bulk mode)
    scan_dirs = []
    if args.results and not args.test_runs:
        base = PROJECT_ROOT / 'results'
        if args.date:
            base = base / args.date
        scan_dirs.append(('results', base))
    elif args.test_runs and not args.results:
        base = PROJECT_ROOT / 'test_runs'
        if args.date:
            base = base / args.date
        scan_dirs.append(('test_runs', base))
    elif args.date:
        # When filtering by date, default to results/ only
        scan_dirs.append(('results', PROJECT_ROOT / 'results' / args.date))
    else:
        # Default: scan both
        scan_dirs.append(('results', PROJECT_ROOT / 'results'))
        scan_dirs.append(('test_runs', PROJECT_ROOT / 'test_runs'))

    try:
        print_header("Test Cost Injection Tool")
        print_info("This tool recalculates costs for test runs using current pricing data.")
        print()

        all_analyses = []

        for dir_name, dir_path in scan_dirs:
            print_info(f"Scanning {dir_name}/ directory...")
            test_runs = find_test_runs(dir_path)
            print_info(f"Found {len(test_runs)} test runs")

            # Analyze each test run
            analyses = []
            for test_dir in test_runs:
                analysis = analyze_test_run(test_dir)
                analyses.append(analysis)

            # Display summary
            display_analysis_summary(analyses, dir_name)
            all_analyses.extend(analyses)

        # Filter to only those needing updates
        needs_update = [a for a in all_analyses if a['needs_update']]

        if not needs_update:
            print_success("All test runs already have cost data!")
            return

        # Ask for confirmation unless auto-update or dry-run
        if args.dry_run:
            print_info(f"Dry run mode - no changes will be made")
            for analysis in needs_update:
                update_test_run(analysis, dry_run=True)
        elif args.auto_update:
            print_info(f"Auto-updating {len(needs_update)} test runs...")
            updated_count = 0
            for analysis in needs_update:
                if update_test_run(analysis, dry_run=False):
                    updated_count += 1
            print_success(f"Updated {updated_count} test runs!")
        else:
            # Interactive mode
            if get_yes_no(f"Update {len(needs_update)} test runs with cost data?", default=True):
                updated_count = 0
                for analysis in needs_update:
                    if update_test_run(analysis, dry_run=False):
                        updated_count += 1
                print_success(f"Updated {updated_count} test runs!")
            else:
                print_info("Update cancelled.")

        # Show final summary of items that cannot be calculated
        cannot_calculate = [a for a in all_analyses if a['cannot_calculate']]
        if cannot_calculate:
            print()
            print_warning(f"{len(cannot_calculate)} test runs have requests with missing pricing data.")
            print_info("Update your pricing file (scripts/data/pricing.json) to calculate costs for these.")

    except KeyboardInterrupt:
        print_warning("\n\nOperation cancelled by user.")
    except Exception as e:
        print_error(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()