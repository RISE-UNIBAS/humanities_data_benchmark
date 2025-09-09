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
        #logging.FileHandler(f"logs/{time.strftime('%Y%m%d-%H%M%S')}.log"),
        logging.StreamHandler(),
    ]
)


def get_api_key(provider):
    """Get the API key for the provider."""
    api_key = os.getenv(f'{provider.upper()}_API_KEY')
    if not api_key:
        raise ValueError(f"No API key found for {provider.upper()}")
    return api_key


def load_benchmark(test_config, date=None):
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
        return benchmark_class(test_config, api_key, benchmark_path, date)
    else:
        logging.info(f"Loaded {benchmark_name} from Benchmark class")
        return DefaultBenchmark(test_config, api_key, benchmark_path, date)


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


def main(limit_to: list[str] = None, dates: list[str] = None):
    """ Main function to run benchmarks.

    This function reads the configuration file, loads the benchmarks,
    and runs each benchmark based on the configuration.

    :param limit_to: Optional list of benchmark ids (such as T0001, T0099) to limit the execution to, defaults to None
    :param dates: Optional list of dates (YYYY-MM-DD format) to limit the execution to, defaults to None
    """

    with open(CONFIG_FILE, newline='', encoding='utf-8') as csvfile:
        tests = csv.DictReader(csvfile)
        for test_config in tests:
            if limit_to and test_config['id'] not in limit_to:
                continue
            if test_config.get('legacy_test', 'false').lower() == 'false':
                if dates:
                    for date in dates:
                        benchmark = load_benchmark(test_config, date)
                        if benchmark.is_runnable():
                            logging.info(f"Running {benchmark.get_title()} for date {date}...")
                            benchmark.run(regenerate_existing_results=REGENERATE_RESULTS)
                        else:
                            logging.error(f"Skipping {benchmark.get_title()} for date {date} (not runnable).")
                else:
                    benchmark = load_benchmark(test_config)
                    if benchmark.is_runnable():
                        logging.info(f"Running {benchmark.get_title()}...")
                        benchmark.run(regenerate_existing_results=REGENERATE_RESULTS)
                    else:
                        logging.error(f"Skipping {benchmark.get_title()} (not runnable).")

if __name__ == "__main__":
    main(limit_to=["T0142", "T0143", "T0144", "T0145", "T0146", "T0147", "T0148",
                   "T0159",
                   "T0160", "T0161", "T0162", "T0163", "T0164", "T0165", "T0166", "T0066",

        "T0149", "T0150", "T0151", "T0152", "T0153", "T0154", "T0155", "T0156", "T0157", "T0158",

                   ], dates=["2025-09-02"])
#
"""




"""

