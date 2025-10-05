"""Calculate total costs for benchmark runs across a date range."""
import argparse
import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path


def parse_date(date_str):
    """Parse a date string in YYYY-MM-DD format."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_str}. Use YYYY-MM-DD.")


def get_date_range(start_date, end_date):
    """Generate list of dates between start_date and end_date (inclusive)."""
    dates = []
    current = start_date
    while current <= end_date:
        dates.append(current.strftime('%Y-%m-%d'))
        current += timedelta(days=1)
    return dates


def load_scoring_file(file_path):
    """Load a scoring.json file and return its contents."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logging.warning(f"Could not load {file_path}: {e}")
        return None


def get_provider_model_from_request_files(test_dir):
    """Extract provider and model from request files in the test directory."""
    for request_file in test_dir.glob('request_*.json'):
        data = load_scoring_file(request_file)
        if data and 'provider' in data and 'model' in data:
            return data['provider'], data['model']
    return None, None


def calculate_costs_for_date_range(results_dir, start_date, end_date, provider=None, model=None):
    """Calculate total costs for all benchmarks in a date range."""
    dates = get_date_range(start_date, end_date)

    total_costs = {
        'total_input_tokens': 0,
        'total_output_tokens': 0,
        'total_tokens': 0,
        'input_cost_usd': 0.0,
        'output_cost_usd': 0.0,
        'total_cost_usd': 0.0,
        'by_date': {},
        'by_provider': {},
        'by_model': {},
        'benchmark_count': 0,
        'date_range': {
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d')
        }
    }

    for date_str in dates:
        date_dir = Path(results_dir) / date_str
        if not date_dir.exists():
            continue

        date_costs = {
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'total_tokens': 0,
            'input_cost_usd': 0.0,
            'output_cost_usd': 0.0,
            'total_cost_usd': 0.0,
            'benchmarks': []
        }

        # Iterate through all test directories for this date
        for test_dir in sorted(date_dir.iterdir()):
            if not test_dir.is_dir():
                continue

            scoring_file = test_dir / 'scoring.json'
            if not scoring_file.exists():
                continue

            data = load_scoring_file(scoring_file)
            if not data or 'cost_summary' not in data:
                continue

            cost_summary = data['cost_summary']

            # Get provider and model from request files
            test_provider, test_model = get_provider_model_from_request_files(test_dir)

            # Apply filters if provided
            if provider and test_provider != provider:
                continue
            if model and test_model != model:
                continue

            benchmark_id = test_dir.name
            date_costs['benchmarks'].append(benchmark_id)

            # Aggregate tokens
            input_tokens = cost_summary.get('total_input_tokens', 0)
            output_tokens = cost_summary.get('total_output_tokens', 0)
            total_tokens = cost_summary.get('total_tokens', 0)
            input_cost = cost_summary.get('input_cost_usd', 0.0)
            output_cost = cost_summary.get('output_cost_usd', 0.0)
            total_cost = cost_summary.get('total_cost_usd', 0.0)

            date_costs['total_input_tokens'] += input_tokens
            date_costs['total_output_tokens'] += output_tokens
            date_costs['total_tokens'] += total_tokens
            date_costs['input_cost_usd'] += input_cost
            date_costs['output_cost_usd'] += output_cost
            date_costs['total_cost_usd'] += total_cost

            # Aggregate by provider
            if test_provider:
                if test_provider not in total_costs['by_provider']:
                    total_costs['by_provider'][test_provider] = {
                        'total_input_tokens': 0,
                        'total_output_tokens': 0,
                        'total_tokens': 0,
                        'input_cost_usd': 0.0,
                        'output_cost_usd': 0.0,
                        'total_cost_usd': 0.0,
                        'benchmark_count': 0
                    }
                total_costs['by_provider'][test_provider]['total_input_tokens'] += input_tokens
                total_costs['by_provider'][test_provider]['total_output_tokens'] += output_tokens
                total_costs['by_provider'][test_provider]['total_tokens'] += total_tokens
                total_costs['by_provider'][test_provider]['input_cost_usd'] += input_cost
                total_costs['by_provider'][test_provider]['output_cost_usd'] += output_cost
                total_costs['by_provider'][test_provider]['total_cost_usd'] += total_cost
                total_costs['by_provider'][test_provider]['benchmark_count'] += 1

            # Aggregate by model
            if test_model:
                model_key = f"{test_provider}/{test_model}" if test_provider else test_model
                if model_key not in total_costs['by_model']:
                    total_costs['by_model'][model_key] = {
                        'total_input_tokens': 0,
                        'total_output_tokens': 0,
                        'total_tokens': 0,
                        'input_cost_usd': 0.0,
                        'output_cost_usd': 0.0,
                        'total_cost_usd': 0.0,
                        'benchmark_count': 0
                    }
                total_costs['by_model'][model_key]['total_input_tokens'] += input_tokens
                total_costs['by_model'][model_key]['total_output_tokens'] += output_tokens
                total_costs['by_model'][model_key]['total_tokens'] += total_tokens
                total_costs['by_model'][model_key]['input_cost_usd'] += input_cost
                total_costs['by_model'][model_key]['output_cost_usd'] += output_cost
                total_costs['by_model'][model_key]['total_cost_usd'] += total_cost
                total_costs['by_model'][model_key]['benchmark_count'] += 1

            total_costs['benchmark_count'] += 1

        if date_costs['benchmarks']:
            total_costs['by_date'][date_str] = date_costs

            # Add to overall totals
            total_costs['total_input_tokens'] += date_costs['total_input_tokens']
            total_costs['total_output_tokens'] += date_costs['total_output_tokens']
            total_costs['total_tokens'] += date_costs['total_tokens']
            total_costs['input_cost_usd'] += date_costs['input_cost_usd']
            total_costs['output_cost_usd'] += date_costs['output_cost_usd']
            total_costs['total_cost_usd'] += date_costs['total_cost_usd']

    return total_costs


def print_cost_summary(costs):
    """Print a formatted cost summary."""
    print("\n" + "="*70)
    print("COST SUMMARY")
    print("="*70)
    print(f"Date Range: {costs['date_range']['start']} to {costs['date_range']['end']}")
    print(f"Total Benchmarks: {costs['benchmark_count']}")
    print("-"*70)
    print(f"Total Input Tokens:  {costs['total_input_tokens']:,}")
    print(f"Total Output Tokens: {costs['total_output_tokens']:,}")
    print(f"Total Tokens:        {costs['total_tokens']:,}")
    print("-"*70)
    print(f"Input Cost (USD):    ${costs['input_cost_usd']:.6f}")
    print(f"Output Cost (USD):   ${costs['output_cost_usd']:.6f}")
    print(f"Total Cost (USD):    ${costs['total_cost_usd']:.6f}")
    print("="*70)

    if costs['by_provider']:
        print("\nCOSTS BY PROVIDER:")
        print("-"*70)
        for provider in sorted(costs['by_provider'].keys()):
            provider_cost = costs['by_provider'][provider]
            print(f"{provider:15s} ${provider_cost['total_cost_usd']:10.6f} "
                  f"({provider_cost['benchmark_count']:3d} benchmarks, "
                  f"{provider_cost['total_tokens']:,} tokens)")
        print("-"*70)

    if costs['by_model']:
        print("\nCOSTS BY MODEL:")
        print("-"*70)
        for model in sorted(costs['by_model'].keys()):
            model_cost = costs['by_model'][model]
            print(f"{model:40s} ${model_cost['total_cost_usd']:10.6f} "
                  f"({model_cost['benchmark_count']:3d} benchmarks)")
        print("-"*70)

    if costs['by_date']:
        print("\nCOSTS BY DATE:")
        print("-"*70)
        for date_str in sorted(costs['by_date'].keys()):
            date_cost = costs['by_date'][date_str]
            print(f"{date_str}: ${date_cost['total_cost_usd']:.6f} "
                  f"({len(date_cost['benchmarks'])} benchmarks)")
        print("-"*70)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Calculate total costs for benchmark runs across a date range.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Calculate costs for a single date
  python calculate_costs.py --start-date 2025-09-30 --end-date 2025-09-30

  # Calculate costs for a date range
  python calculate_costs.py --start-date 2025-09-01 --end-date 2025-09-30

  # Save results to a file
  python calculate_costs.py --start-date 2025-09-01 --end-date 2025-09-30 --output costs.json
        """
    )

    parser.add_argument(
        '--start-date',
        type=str,
        required=True,
        help='Start date in YYYY-MM-DD format'
    )

    parser.add_argument(
        '--end-date',
        type=str,
        required=True,
        help='End date in YYYY-MM-DD format'
    )

    parser.add_argument(
        '--results-dir',
        type=str,
        default='../results',
        help='Path to results directory (default: ../results)'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Output file path for JSON results (optional)'
    )

    parser.add_argument(
        '--provider',
        type=str,
        choices=['openai', 'genai', 'anthropic', 'mistral'],
        help='Filter by provider (optional)'
    )

    parser.add_argument(
        '--model',
        type=str,
        help='Filter by model (optional)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s %(levelname)s:%(name)s:%(message)s'
    )

    # Parse dates
    start_date = parse_date(args.start_date)
    end_date = parse_date(args.end_date)

    if start_date > end_date:
        parser.error("Start date must be before or equal to end date")

    # Get absolute path to results directory
    script_dir = Path(__file__).parent
    results_dir = (script_dir / args.results_dir).resolve()

    if not results_dir.exists():
        parser.error(f"Results directory not found: {results_dir}")

    logging.info(f"Calculating costs from {args.start_date} to {args.end_date}")
    logging.info(f"Results directory: {results_dir}")

    # Calculate costs
    costs = calculate_costs_for_date_range(
        results_dir,
        start_date,
        end_date,
        provider=args.provider,
        model=args.model
    )

    # Print summary
    print_cost_summary(costs)

    # Save to file if requested
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(costs, f, indent=4)
        print(f"\nDetailed results saved to: {output_path}")

    return 0


if __name__ == '__main__':
    exit(main())
