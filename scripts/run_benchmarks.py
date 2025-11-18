import csv
import importlib
import os
import sys
import time
from benchmark_base import DefaultBenchmark
from dotenv import load_dotenv
import logging

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

BENCHMARKS_DIR = '../benchmarks'
REPORTS_DIR = "../docs"
CONFIG_FILE = os.path.join(BENCHMARKS_DIR, 'benchmarks_tests.csv')

# Configure logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(name)s:%(message)s",
    handlers=[
        logging.FileHandler(f"{log_dir}/{time.strftime('%Y%m%d-%H%M%S')}.log"),
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
        logging.info(f"Loaded {benchmark_name} from DefaultBenchmark class")
        return DefaultBenchmark(test_config, api_key, benchmark_path)


def main(limit_to: list[str] = None, regenerate_existing_results: bool = False):
    """ Main function to run benchmarks.

    This function reads the configuration file, loads the benchmarks,
    and runs each benchmark based on the configuration.

    :param limit_to: Optional list of benchmark ids (such as T0001, T0099) to limit the execution to, defaults to None
    :param regenerate_existing_results
    """

    # Read the benchmark configuration file (csv)
    with open(CONFIG_FILE, newline='', encoding='utf-8') as csvfile:
        tests = csv.DictReader(csvfile)
        # For each test configuration
        for test_config in tests:
            # Only process if in limit_to list
            if limit_to and test_config['id'] not in limit_to:
                continue
            # Skip legacy tests
            if test_config.get('legacy_test', 'false').lower() == 'true':
                continue
            # Load benchmark
            benchmark = load_benchmark(test_config)
            # Run benchmark
            benchmark.run(regenerate_existing_results=regenerate_existing_results)


if __name__ == "__main__":
    main(limit_to=['T0002'])
