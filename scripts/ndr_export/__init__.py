from pathlib import Path

# Get the project root directory (two levels up from this file)
_PROJECT_ROOT = Path(__file__).parent.parent.parent

RESULTS_PATH = _PROJECT_ROOT / "results"
EXPORT_PATH = _PROJECT_ROOT / "collected_results"
BENCHMARKS_PATH = _PROJECT_ROOT / "benchmarks"
PRICING_PATH = _PROJECT_ROOT / "scripts" / "data" / "pricing.json"
CONTRIBUTORS_PATH = _PROJECT_ROOT / "scripts" / "data" / "contributors.json"
TESTS_CSV = _PROJECT_ROOT / "benchmarks" / "benchmarks_tests.csv"