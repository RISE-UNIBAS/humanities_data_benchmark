#!/usr/bin/env python3
"""CLI tool to run a single benchmark test interactively.

Usage:
    python scripts/run_single_test.py                              # Interactive mode
    python scripts/run_single_test.py --test_id T0001             # Run specific test
    python scripts/run_single_test.py --test_id T0001 --regenerate # Regenerate results
    python scripts/run_single_test.py --adhoc                      # Run ad-hoc test
"""

import sys
import csv
import argparse
from pathlib import Path
from typing import Dict, List, Optional
import os
from datetime import datetime

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent

# Add scripts directory to path for imports
sys.path.insert(0, str(SCRIPT_DIR))

# Change to scripts directory for relative path imports to work
original_cwd = os.getcwd()
os.chdir(SCRIPT_DIR)

from run_benchmarks import load_benchmark


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
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}")
    print(f"  {text}")
    print(f"{'=' * 70}{Colors.END}\n")


def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_info(text: str):
    """Print info message."""
    print(f"{Colors.CYAN}ℹ {text}{Colors.END}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def load_test_configs() -> List[Dict]:
    """Load all test configurations from benchmarks_tests.csv."""
    csv_path = Path("..") / "benchmarks" / "benchmarks_tests.csv"

    if not csv_path.exists():
        print_error(f"Test configuration file not found: {csv_path}")
        return []

    try:
        tests = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Skip legacy tests
                if row.get('legacy_test', '').lower() == 'true':
                    continue
                tests.append(row)

        return tests
    except Exception as e:
        print_error(f"Error loading test configurations: {e}")
        return []


def display_tests_table(tests: List[Dict], page: int = 0, page_size: int = 20):
    """Display tests in a paginated table format."""
    if not tests:
        print_warning("No tests available.")
        return 0, 0

    start_idx = page * page_size
    end_idx = min(start_idx + page_size, len(tests))
    page_tests = tests[start_idx:end_idx]

    print(f"\n{Colors.BOLD}Available Tests (showing {start_idx + 1}-{end_idx} of {len(tests)}):{Colors.END}\n")

    # Table header
    print(f"{Colors.BOLD}{'#':<4} {'Test ID':<8} {'Benchmark':<25} {'Provider':<12} {'Model':<30}{Colors.END}")
    print("-" * 90)

    # Table rows
    for i, test in enumerate(page_tests, start=start_idx + 1):
        test_id = test.get('id', 'N/A')
        benchmark = test.get('name', 'N/A')
        provider = test.get('provider', 'N/A')
        model = test.get('model', 'N/A')

        # Truncate long names
        if len(benchmark) > 24:
            benchmark = benchmark[:21] + "..."
        if len(model) > 29:
            model = model[:26] + "..."

        print(f"{i:<4} {test_id:<8} {benchmark:<25} {provider:<12} {model:<30}")

    print()
    return start_idx, end_idx


def get_int_input(prompt: str, default: int = 1, min_val: int = 1, max_val: int = 1000) -> int:
    """Get integer input with validation."""
    while True:
        try:
            full_prompt = f"{Colors.CYAN}{prompt} [{default}]:{Colors.END} "
            value = input(full_prompt).strip()

            if not value:
                return default

            try:
                int_value = int(value)
                if min_val <= int_value <= max_val:
                    return int_value
                else:
                    print_error(f"Please enter a number between {min_val} and {max_val}.")
            except ValueError:
                print_error(f"Invalid input. Please enter a number.")
        except EOFError:
            return default
        except KeyboardInterrupt:
            raise


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


def select_test_interactive(tests: List[Dict]) -> Optional[Dict]:
    """Interactive test selection with pagination and search."""
    if not tests:
        return None

    page = 0
    page_size = 20
    filtered_tests = tests

    while True:
        print_header("Select a Test to Run")

        start_idx, end_idx = display_tests_table(filtered_tests, page, page_size)
        total_pages = (len(filtered_tests) + page_size - 1) // page_size

        print(f"{Colors.YELLOW}Options:{Colors.END}")
        print(f"  • Enter a number (1-{len(filtered_tests)}) to select a test")
        print(f"  • Enter 'n' for next page, 'p' for previous page")
        print(f"  • Enter 's' to search/filter tests")
        print(f"  • Enter 'a' to run an ad-hoc test (custom parameters)")
        print(f"  • Enter 'q' to quit")
        if filtered_tests != tests:
            print(f"  • Enter 'c' to clear filter")
        print()

        choice = input(f"{Colors.CYAN}Your choice:{Colors.END} ").strip().lower()

        if choice == 'q':
            return None
        elif choice == 'a':
            return {'_adhoc': True}  # Special marker for ad-hoc test
        elif choice == 'n':
            if page < total_pages - 1:
                page += 1
            else:
                print_warning("Already on last page.")
        elif choice == 'p':
            if page > 0:
                page -= 1
            else:
                print_warning("Already on first page.")
        elif choice == 's':
            search_term = input(f"{Colors.CYAN}Search (benchmark name, provider, model):{Colors.END} ").strip().lower()
            if search_term:
                filtered_tests = [
                    t for t in tests
                    if search_term in t.get('name', '').lower()
                    or search_term in t.get('provider', '').lower()
                    or search_term in t.get('model', '').lower()
                    or search_term in t.get('id', '').lower()
                ]
                if filtered_tests:
                    print_success(f"Found {len(filtered_tests)} matching tests.")
                    page = 0
                else:
                    print_warning("No tests match your search.")
                    filtered_tests = tests
        elif choice == 'c':
            filtered_tests = tests
            page = 0
            print_info("Filter cleared.")
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(filtered_tests):
                    return filtered_tests[idx]
                else:
                    print_error(f"Please enter a number between 1 and {len(filtered_tests)}.")
            except ValueError:
                print_error("Invalid input.")


def display_test_config(test: Dict):
    """Display detailed test configuration."""
    print_header("Test Configuration")

    print(f"{Colors.BOLD}Test ID:{Colors.END} {test.get('id', 'N/A')}")
    print(f"{Colors.BOLD}Benchmark:{Colors.END} {test.get('name', 'N/A')}")
    print(f"{Colors.BOLD}Provider:{Colors.END} {test.get('provider', 'N/A')}")
    print(f"{Colors.BOLD}Model:{Colors.END} {test.get('model', 'N/A')}")
    print(f"{Colors.BOLD}Temperature:{Colors.END} {test.get('temperature', 'N/A')}")
    print(f"{Colors.BOLD}Dataclass:{Colors.END} {test.get('dataclass', 'None')}")
    print(f"{Colors.BOLD}Prompt File:{Colors.END} {test.get('prompt_file', 'N/A')}")

    role_desc = test.get('role_description', '')
    if role_desc:
        role_preview = role_desc[:100] + ('...' if len(role_desc) > 100 else '')
        print(f"{Colors.BOLD}Role Description:{Colors.END} {role_preview}")

    rules = test.get('rules', '')
    if rules:
        print(f"{Colors.BOLD}Rules:{Colors.END} {rules}")

    print()


def check_api_key(provider: str) -> bool:
    """Check if API key is available for provider."""
    key_name = f"{provider.upper()}_API_KEY"

    if os.environ.get(key_name):
        return True

    print_error(f"API key not found for {provider}.")
    print_info(f"Please set environment variable: {key_name}")
    return False


def get_input(prompt: str, default: Optional[str] = None, required: bool = True) -> str:
    """Get user input with optional default value."""
    if default:
        full_prompt = f"{Colors.CYAN}{prompt} [{default}]:{Colors.END} "
    else:
        full_prompt = f"{Colors.CYAN}{prompt}:{Colors.END} "

    while True:
        try:
            value = input(full_prompt).strip()

            if not value and default:
                return default

            if not value and required:
                print_error("This field is required. Please provide a value.")
                continue

            return value
        except EOFError:
            if default:
                return default
            elif not required:
                return ""
            else:
                print_error("Input required but EOF encountered.")
                continue
        except KeyboardInterrupt:
            raise


def list_available_benchmarks() -> List[str]:
    """List all available benchmarks (directories in benchmarks/)."""
    benchmarks_dir = Path("..") / "benchmarks"
    if not benchmarks_dir.exists():
        return []

    benchmarks = []
    for item in benchmarks_dir.iterdir():
        if item.is_dir() and not item.name.startswith('.') and not item.name.startswith('_'):
            # Check if it has required structure
            if (item / "benchmark.py").exists():
                benchmarks.append(item.name)

    return sorted(benchmarks)


def get_available_providers() -> List[str]:
    """Get list of providers with configured API keys."""
    all_providers = ["openai", "anthropic", "genai", "mistral", "openrouter", "scicore"]
    available = []

    for provider in all_providers:
        key_name = f"{provider.upper()}_API_KEY"
        if os.environ.get(key_name):
            available.append(provider)

    return available


def collect_adhoc_test_params() -> Optional[Dict]:
    """Collect parameters for an ad-hoc test interactively."""
    print_header("Create Ad-Hoc Test")

    params = {}

    # Benchmark selection
    benchmarks = list_available_benchmarks()
    if not benchmarks:
        print_error("No benchmarks found in benchmarks/ directory.")
        return None

    print(f"{Colors.BOLD}Available Benchmarks:{Colors.END}")
    for i, bm in enumerate(benchmarks, 1):
        print(f"  {i}. {bm}")
    print()

    benchmark_idx = get_int_input("Select benchmark number", default=1, min_val=1, max_val=len(benchmarks)) - 1
    params['name'] = benchmarks[benchmark_idx]

    # Provider selection - only show providers with API keys
    providers = get_available_providers()

    if not providers:
        print_error("No API keys configured.")
        print_info("Please set at least one of: OPENAI_API_KEY, ANTHROPIC_API_KEY, GENAI_API_KEY, MISTRAL_API_KEY, OPENROUTER_API_KEY, SCICORE_API_KEY")
        return None

    print(f"\n{Colors.BOLD}Available Providers (with API keys):{Colors.END}")
    for i, prov in enumerate(providers, 1):
        print(f"  {i}. {prov}")
    print()

    provider_idx = get_int_input("Select provider number", default=1, min_val=1, max_val=len(providers)) - 1
    params['provider'] = providers[provider_idx]

    # Model
    print()
    model_suggestions = {
        "openai": "gpt-4o",
        "anthropic": "claude-3-5-sonnet-20241022",
        "genai": "gemini-2.0-flash-exp",
        "mistral": "pixtral-large-latest",
        "openrouter": "openai/gpt-4o",
        "scicore": "meta-llama/Meta-Llama-3.1-70B-Instruct"
    }
    suggested_model = model_suggestions.get(params['provider'], "")
    params['model'] = get_input("Model name", default=suggested_model)

    # Temperature
    params['temperature'] = get_input("Temperature", default="0.0", required=False)

    # Prompt file
    benchmark_dir = Path("..") / "benchmarks" / params['name'] / "prompts"
    prompt_files = []
    if benchmark_dir.exists():
        prompt_files = [f.name for f in benchmark_dir.iterdir() if f.is_file() and f.suffix in ['.txt', '.md']]

    if prompt_files:
        print(f"\n{Colors.BOLD}Available Prompt Files:{Colors.END}")
        for i, pf in enumerate(prompt_files, 1):
            print(f"  {i}. {pf}")
        print()
        prompt_idx = get_int_input("Select prompt file number", default=1, min_val=1, max_val=len(prompt_files)) - 1
        params['prompt_file'] = prompt_files[prompt_idx]
    else:
        params['prompt_file'] = get_input("Prompt filename", default="prompt.txt", required=False)

    # Dataclass
    benchmark_dir = Path("..") / "benchmarks" / params['name']
    if (benchmark_dir / "dataclass.py").exists():
        # Try to parse dataclass names from the file
        use_dataclass = get_yes_no("Use structured dataclass output?", default=True)
        if use_dataclass:
            params['dataclass'] = get_input("Dataclass name (leave empty if unsure)", default="", required=False)
        else:
            params['dataclass'] = ""
    else:
        params['dataclass'] = ""

    # Role description
    print()
    params['role_description'] = get_input(
        "Role description",
        default="You are a historian analyzing historical documents.",
        required=False
    )

    # Rules
    params['rules'] = ""

    # Generate ad-hoc test ID
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    params['id'] = f"ADHOC_{timestamp}"

    return params


def run_adhoc_test(test_config: Dict, regenerate: bool = True):
    """Run an ad-hoc test with custom results directory."""
    print_header(f"Running Ad-Hoc Test {test_config['id']}")

    try:
        # Load the benchmark
        benchmark = load_benchmark(test_config)

        # Monkey-patch the results directory methods to use test_runs instead of results
        original_get_request_answer_path = benchmark.get_request_answer_path
        original_save_benchmark_score = benchmark.save_benchmark_score

        def custom_get_request_answer_path():
            return str(os.path.join('..', 'test_runs', benchmark.date, benchmark.id))

        def custom_save_benchmark_score(score: dict):
            save_path = os.path.join('..', "test_runs", benchmark.date, benchmark.id, "scoring.json")
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            from data_loader import write_file
            write_file(save_path, score)

        benchmark.get_request_answer_path = custom_get_request_answer_path
        benchmark.save_benchmark_score = custom_save_benchmark_score

        # Run the benchmark
        benchmark.run(regenerate_existing_results=regenerate)

        print_success(f"\nAd-hoc test {test_config['id']} completed!")
        print_info(f"Results saved to: test_runs/{benchmark.date}/{benchmark.id}/")

    except Exception as e:
        print_error(f"Error running ad-hoc test: {e}")
        import traceback
        traceback.print_exc()


def run_test(test_id: str, regenerate: bool = False):
    """Run a single test from CSV using the existing run_benchmarks infrastructure."""
    print_header(f"Running Test {test_id}")

    try:
        # Load test config from CSV
        tests = load_test_configs()
        test = next((t for t in tests if t.get('id') == test_id), None)

        if not test:
            print_error(f"Test {test_id} not found.")
            return

        # Load and run benchmark
        benchmark = load_benchmark(test)
        benchmark.run(regenerate_existing_results=regenerate)

        print_success(f"\nTest {test_id} completed!")
        print_info(f"Results saved to: results/{benchmark.date}/{benchmark.id}/")

    except Exception as e:
        print_error(f"Error running test: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run a single benchmark test interactively or by test ID"
    )
    parser.add_argument(
        '--test_id',
        type=str,
        help='Test ID to run directly (e.g., T0001)'
    )
    parser.add_argument(
        '--regenerate',
        action='store_true',
        help='Regenerate results even if they already exist'
    )
    parser.add_argument(
        '--adhoc',
        action='store_true',
        help='Run an ad-hoc test with custom parameters (interactive)'
    )

    args = parser.parse_args()

    try:
        # Ad-hoc test mode
        if args.adhoc:
            adhoc_params = collect_adhoc_test_params()

            if adhoc_params is None:
                return

            # Display configuration
            display_test_config(adhoc_params)

            # Check API key
            provider = adhoc_params.get('provider', '')
            if not check_api_key(provider):
                return

            # Confirm and run
            test_id = adhoc_params.get('id')
            if get_yes_no(f"Run ad-hoc test {test_id}?", default=True):
                run_adhoc_test(adhoc_params, regenerate=True)
            return

        # Load all tests
        tests = load_test_configs()

        if not tests:
            print_error("No tests found. Please check benchmarks/benchmarks_tests.csv")
            return

        # If test_id provided via command line, run it directly
        if args.test_id:
            # Find the test config
            test = next((t for t in tests if t.get('id') == args.test_id), None)

            if not test:
                print_error(f"Test {args.test_id} not found in configuration.")
                return

            # Check API key
            provider = test.get('provider', '')
            if not check_api_key(provider):
                return

            # Run the test
            run_test(args.test_id, regenerate=args.regenerate)
            return

        # Interactive mode
        while True:
            # Select test
            selected_test = select_test_interactive(tests)

            if selected_test is None:
                print_info("Goodbye!")
                break

            # Check if ad-hoc test was selected
            if selected_test.get('_adhoc'):
                # Collect ad-hoc test parameters
                adhoc_params = collect_adhoc_test_params()

                if adhoc_params is None:
                    continue

                # Display configuration
                display_test_config(adhoc_params)

                # Check API key
                provider = adhoc_params.get('provider', '')
                if not check_api_key(provider):
                    continue

                # Confirm run
                test_id = adhoc_params.get('id')
                if not get_yes_no(f"Run ad-hoc test {test_id}?", default=True):
                    continue

                # Ad-hoc tests always regenerate
                run_adhoc_test(adhoc_params, regenerate=True)

            else:
                # Regular CSV test
                # Display configuration
                display_test_config(selected_test)

                # Check API key
                provider = selected_test.get('provider', '')
                if not check_api_key(provider):
                    continue

                # Confirm run
                test_id = selected_test.get('id')
                if not get_yes_no(f"Run test {test_id}?", default=True):
                    continue

                # Ask about regeneration
                regenerate = get_yes_no("Regenerate existing results?", default=False)

                # Run the test
                run_test(test_id, regenerate=regenerate)

            # Ask if user wants to run another test
            if not get_yes_no("\nRun another test?", default=True):
                print_info("Goodbye!")
                break

    except KeyboardInterrupt:
        print_warning("\n\nTest execution cancelled by user.")
    except Exception as e:
        print_error(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
