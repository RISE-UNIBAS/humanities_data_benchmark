import json

from scripts.ndr_export import BENCHMARKS_PATH, EXPORT_PATH, RESULTS_PATH
from scripts.ndr_export.meta_utils import get_benchmarks, get_meta, load_json
from scripts.ndr_export.test_utils import get_all_tests


def load_prompt(benchmark_name, prompt_file):
    """Load prompt content from a benchmark's prompts directory.

    Args:
        benchmark_name: Name of the benchmark
        prompt_file: Filename of the prompt (e.g., "prompt.txt")

    Returns:
        String content of the prompt file, or None if not found
    """
    if not prompt_file:
        return None

    prompt_path = BENCHMARKS_PATH / benchmark_name / "prompts" / prompt_file

    if not prompt_path.exists():
        print(f"Warning: Prompt file not found: {prompt_path}")
        return None

    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading prompt file {prompt_path}: {e}")
        return None

def get_available_prompts(benchmark_name):
    """Get all available prompt files for a benchmark.

    Args:
        benchmark_name: Name of the benchmark

    Returns:
        List of dictionaries with prompt filename and content
    """
    prompts_dir = BENCHMARKS_PATH / benchmark_name / "prompts"

    if not prompts_dir.exists():
        print(f"Warning: Prompts directory not found: {prompts_dir}")
        return []

    prompts = []
    for prompt_file in prompts_dir.iterdir():
        if prompt_file.is_file() and prompt_file.suffix in [".txt", ".md"]:
            try:
                with open(prompt_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    prompts.append({
                        "filename": prompt_file.name,
                        "content": content
                    })
            except Exception as e:
                print(f"Error reading prompt file {prompt_file}: {e}")

    return prompts

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
        top_5_runs = get_top_test_runs(test_runs, top_n=5)
        latest_5_runs = get_latest_test_runs(test_runs, last_n=5)
        no_of_runs = len(test_runs)
        available_prompts = get_available_prompts(benchmark)

        # Collect unique providers and models used in test runs
        used_providers = list(set(run.get("provider") for run in test_runs if run.get("provider")))
        used_models = list(set(run.get("model") for run in test_runs if run.get("model")))

        benchmark_entry = meta.copy()
        benchmark_entry["name"] = benchmark
        benchmark_entry["test_count"] = no_of_runs
        benchmark_entry["used_providers"] = used_providers
        benchmark_entry["used_models"] = used_models
        benchmark_entry["available_prompts"] = available_prompts
        benchmark_entry["test_runs"] = test_runs
        benchmark_entry["top_5_runs"] = top_5_runs
        benchmark_entry["latest_5_runs"] = latest_5_runs
        benchmark_export.append(benchmark_entry)

    # Save the export data to a JSON file
    export_path = EXPORT_PATH / "benchmark_export.json"
    with open(export_path, "w", encoding="utf-8") as f:
        json.dump(benchmark_export, f, indent=2, ensure_ascii=False)


def calculate_normalized_score(scoring_data, benchmark_name):
    """Calculate a normalized score (0-100) based on benchmark ranking configuration.

    Args:
        scoring_data: Dictionary with scoring metrics
        benchmark_name: Name of the benchmark

    Returns:
        Normalized score (0-100) or None if not calculable
    """
    if not scoring_data:
        return None

    # Check for "niy" (not implemented yet)
    if scoring_data.get("score") == "niy":
        return None

    # Get the benchmark's ranking configuration
    meta = get_meta(benchmark_name)
    ranking_config = meta.get("ranking")

    if not ranking_config:
        # No ranking config - try to use any available metric
        for metric in ["fuzzy", "f1_macro", "accuracy", "precision", "recall"]:
            if metric in scoring_data and scoring_data[metric] not in [None, "niy"]:
                return min(100, max(0, scoring_data[metric] * 100))
        return None

    metric = ranking_config.get("metric")
    order = ranking_config.get("order", "desc")

    if not metric or metric not in scoring_data:
        return None

    score_value = scoring_data.get(metric)

    if score_value is None or score_value == "niy":
        return None

    try:
        score_value = float(score_value)
    except (ValueError, TypeError):
        return None

    # Normalize based on metric type and order
    if order == "desc":
        normalized = score_value * 100
    else:  # order == "asc"
        normalized = max(0, 100 - (score_value * 100))

    return min(100, max(0, normalized))

def get_benchmark_test_runs(benchmark_name, all_tests):
    """Get all actual test runs (with dates) for a given benchmark.

    Scans the results directory for all test executions of this benchmark.
    """
    # Create lookup for test configs
    tests_by_id = {test.get("id"): test for test in all_tests}

    test_runs = []

    if not RESULTS_PATH.exists():
        return test_runs

    # Iterate through all date folders
    date_folders = sorted(RESULTS_PATH.iterdir())

    for date_folder in date_folders:
        if not date_folder.is_dir():
            continue

        date_str = date_folder.name

        # Iterate through all test_id folders in this date
        for test_folder in date_folder.iterdir():
            if not test_folder.is_dir():
                continue

            test_id = test_folder.name

            # Get test configuration
            test_config = tests_by_id.get(test_id)
            if not test_config or test_config.get("name") != benchmark_name:
                continue

            # Load scoring data
            scoring_path = test_folder / "scoring.json"
            scoring_data = load_json(scoring_path) if scoring_path.exists() else None

            # Calculate normalized score
            normalized_score = calculate_normalized_score(scoring_data, benchmark_name)

            # Build test run entry
            test_run = {
                "test_id": test_id,
                "date": date_str,
                "provider": test_config.get("provider"),
                "model": test_config.get("model"),
                "normalized_score": normalized_score
            }

            # Remove None values to keep it clean
            test_run = {k: v for k, v in test_run.items() if v is not None}
            test_runs.append(test_run)

    return test_runs


def get_top_test_runs(test_runs, top_n=5):
    """
    Get the top N test runs based on normalized scores.

    Args:
        test_runs: List of test run dictionaries with normalized_score
        top_n: Number of top results to return

    Returns:
        List of top test runs sorted by normalized_score (highest first)
    """
    # Filter out runs without a normalized score
    scored_runs = [run for run in test_runs if run.get("normalized_score") is not None]

    if not scored_runs:
        return []

    # Sort by normalized_score (higher is always better for normalized scores)
    scored_runs.sort(key=lambda x: x["normalized_score"], reverse=True)

    # Return top N
    return scored_runs[:top_n]

def get_latest_test_runs(test_runs, last_n=5):
    """
    Get the most recent N test runs based on date.

    Args:
        test_runs: List of test run dictionaries with date
        last_n: Number of recent results to return

    Returns:
        List of most recent test runs sorted by date (newest first)
    """
    if not test_runs:
        return []

    # Sort by date (newest first)
    sorted_runs = sorted(test_runs, key=lambda x: x.get("date", ""), reverse=True)

    # Return last N
    return sorted_runs[:last_n]

if __name__ == "__main__":
    generate_benchmark_export()