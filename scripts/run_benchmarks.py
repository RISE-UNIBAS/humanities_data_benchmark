import csv
import importlib
import os
import sys
import time
from benchmark_base import Benchmark, DefaultBenchmark
from dotenv import load_dotenv
import logging

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

REGENERATE_RESULTS = False

BENCHMARKS_DIR = '../benchmarks'
REPORTS_DIR = "../docs"
CONFIG_FILE = os.path.join(BENCHMARKS_DIR, 'benchmarks_tests.csv')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(name)s:%(message)s",
    handlers=[
        logging.FileHandler(f"logs/{time.strftime('%Y%m%d-%H%M%S')}.log"),
        logging.StreamHandler(),
    ]
)

def get_api_key(provider):
    """Get the API key for the provider."""
    api_key = os.getenv(f'{provider.upper()}_API_KEY')
    if not api_key:
        raise ValueError(f"No API key found for {provider.upper()}")
    return api_key


def load_benchmark(test_config):
    """Load the benchmark class from the benchmark folder."""
    benchmark_name = test_config['name']
    api_key = get_api_key(test_config['provider'])
    benchmark_path = os.path.join(BENCHMARKS_DIR, benchmark_name)
    benchmark_file = os.path.join(benchmark_path, 'benchmark.py')

    if os.path.isfile(benchmark_file):
        spec = importlib.util.spec_from_file_location("benchmark_module", benchmark_file)
        benchmark_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(benchmark_module)
        # Class must have the same name as the benchmark folder but in CamelCase
        class_name = ''.join(part.capitalize() for part in benchmark_name.split('_'))
        benchmark_class = getattr(benchmark_module, class_name)
        logging.info(f"Loaded {benchmark_name} from {benchmark_file}")
        return benchmark_class(test_config, api_key, benchmark_path)
    else:
        logging.info(f"Loaded {benchmark_name} from Benchmark class")
        return DefaultBenchmark(test_config, api_key, benchmark_path)


def create_result_table(results):
    # First, gather all possible scores to handle missing data
    scores = set()
    for val in results.values():
        scores.update(val.keys())

    scores = sorted(scores)

    # Create header
    header = "key | " + " | ".join(scores)
    separator = " | ".join(['---'] * (len(scores) + 1))

    # Build rows
    rows = []
    for key, val in results.items():
        row = [key]
        for score in scores:
            row.append(str(val.get(score, '-')))
        rows.append(" | ".join(row))

    # Combine everything
    md_table = f"{header}\n{separator}\n" + "\n".join(rows)

    table_path = os.path.join("..", "benchmarks", 'result_table.md')
    with open(table_path, 'w', encoding='utf-8') as f:
        f.write(md_table)


def main():
    # Open Config File and run each test in it
    with open(CONFIG_FILE, newline='', encoding='utf-8') as csvfile:
        tests = csv.DictReader(csvfile)
        for test_config in tests:
            if test_config.get('legacy_test', 'false').lower() == 'false':
                benchmark = load_benchmark(test_config)
                if benchmark.is_runnable():
                    logging.info(f"Running {benchmark.get_title()}...")
                    benchmark.run(regenerate_existing_results=REGENERATE_RESULTS)
                else:
                    logging.error(f"Skipping {benchmark.get_title()} (not runnable).")


if __name__ == "__main__":
    main()