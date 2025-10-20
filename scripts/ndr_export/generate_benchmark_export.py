import json
from pathlib import Path

from scripts.ndr_export.meta_utils import get_benchmarks, get_meta, load_json
from scripts.ndr_export.test_utils import get_all_tests

RESULTS_PATH = Path("../../results")
EXPORT_PATH = Path("../../ndr_export")

def generate_benchmark_export():
    """Generate export data for benchmarks in NDR Core. Result is a list of dictionaries,
    one per benchmark. Contains <benchmark>/meta.json information, a count of tests, the list
    of test IDs, and the best five runs."""

    benchmarks = get_benchmarks()   # list of benchmark IDs (= folder names)
    all_tests = get_all_tests()
    benchmark_export = []

    for benchmark in benchmarks:
        meta = get_meta(benchmark)  # data from <benchmark>/meta.json
        test_runs = get_benchmark_test_runs(benchmark, all_tests)
        top_5_runs = get_top_test_runs(benchmark, test_runs, meta.get("ranking"), top_n=5)
        no_of_runs = len(test_runs)

        benchmark_entry = meta.copy()
        benchmark_entry["name"] = benchmark
        benchmark_entry["test_count"] = no_of_runs
        benchmark_entry["test_runs"] = test_runs
        benchmark_entry["top_5_runs"] = top_5_runs
        benchmark_export.append(benchmark_entry)

    # Save the export data to a JSON file
    export_path = EXPORT_PATH / "benchmark_export.json"
    with open(export_path, "w", encoding="utf-8") as f:
        json.dump(benchmark_export, f, indent=2, ensure_ascii=False)


def get_benchmark_test_runs(benchmark_name, all_tests):
    """Get all test runs for a given benchmark."""
    test_runs = []
    for test in all_tests:
        if test.get("name") == benchmark_name:
            # Build a test run entry with configuration details
            test_run = {
                "test_id": test.get("id"),
                "provider": test.get("provider"),
                "model": test.get("model"),
                "dataclass": test.get("dataclass"),
                "temperature": test.get("temperature"),
                "role_description": test.get("role_description"),
                "prompt_file": test.get("prompt_file"),
                "rules": test.get("rules"),
                "legacy_test": test.get("legacy_test", False)
            }
            # Remove None values to keep it clean
            test_run = {k: v for k, v in test_run.items() if v is not None}
            test_runs.append(test_run)

    return test_runs


def get_top_test_runs(benchmark_name, all_tests, ranking_config=None, top_n=5):
    """
    Get the top N test runs for a benchmark based on ranking configuration.

    Args:
        benchmark_name: Name of the benchmark
        all_tests: List of all test configurations
        ranking_config: Dict with 'metric' and 'order' ('asc' or 'desc')
        top_n: Number of top results to return

    Returns:
        List of top test runs with their scores
    """
    if not ranking_config:
        print(f"No ranking config for {benchmark_name}, skipping top runs")
        return []

    metric = ranking_config.get("metric")
    order = ranking_config.get("order", "desc")

    if not metric:
        print(f"No metric specified for {benchmark_name}")
        return []

    # Get all test IDs for this benchmark
    test_ids = [test.get("id") for test in all_tests if test.get("name") == benchmark_name]

    # Collect scores for all tests
    scored_runs = []
    for test_id in test_ids:
        result = find_latest_test_result(test_id)
        if not result:
            continue

        date_str, scoring_path = result
        scoring_data = load_json(scoring_path)

        if not scoring_data:
            continue

        score = scoring_data.get(metric)
        if score is None or score == "niy":  # Skip "not implemented yet"
            continue

        # Find test config
        test_config = next((t for t in all_tests if t.get("id") == test_id), None)
        if not test_config:
            continue

        scored_runs.append({
            "test_id": test_id,
            "provider": test_config.get("provider"),
            "model": test_config.get("model"),
            "date": date_str,
            "score": score,
            "metric": metric,
            "all_metrics": scoring_data
        })

    # Sort by score
    reverse = (order == "desc")
    scored_runs.sort(key=lambda x: x["score"], reverse=reverse)

    # Return top N
    return scored_runs[:top_n]

def find_latest_test_result(test_id):
    """
    Find the most recent result for a given test_id.

    Returns:
        Tuple of (date_str, scoring_path) or None if not found
    """
    if not RESULTS_PATH.exists():
        return None

    # Scan all date folders in reverse order (newest first)
    date_folders = sorted(RESULTS_PATH.iterdir(), reverse=True)

    for date_folder in date_folders:
        if not date_folder.is_dir():
            continue

        test_folder = date_folder / test_id
        if test_folder.exists() and test_folder.is_dir():
            scoring_path = test_folder / "scoring.json"
            if scoring_path.exists():
                return (date_folder.name, scoring_path)

    return None

if __name__ == "__main__":
    generate_benchmark_export()