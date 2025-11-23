import json

from scripts.ndr_export import BENCHMARKS_PATH, RESULTS_PATH, EXPORT_PATH
from scripts.ndr_export.meta_utils import get_meta, load_json
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
        # Prefer common metrics in order
        for metric in ["fuzzy", "f1_macro", "accuracy", "precision", "recall"]:
            if metric in scoring_data and scoring_data[metric] not in [None, "niy"]:
                # Assume these are 0-1 metrics where higher is better
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
        # Higher is better (fuzzy, f1_macro, etc.)
        # Assume 0-1 range, multiply by 100
        normalized = score_value * 100
    else:  # order == "asc"
        # Lower is better (cer, error rates, etc.)
        # For CER: 0 is perfect (100), 1 is bad (0)
        # Use formula: max(0, 100 - score*100)
        # This handles CER values > 1 by capping at 0
        normalized = max(0, 100 - (score_value * 100))

    # Ensure score is in 0-100 range
    return min(100, max(0, normalized))


def generate_test_runs_export():
    """Generate export data for all test runs.

    A test run is a specific execution of a test on a particular date.
    Each test run includes configuration, prompt, results, and scoring.
    """
    all_tests = get_all_tests()

    # Create a lookup dict for quick test config access
    tests_by_id = {test.get("id"): test for test in all_tests}

    test_runs_export = []

    if not RESULTS_PATH.exists():
        print(f"Results path not found: {RESULTS_PATH}")
        return

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
            if not test_config:
                print(f"Warning: No test config found for {test_id}")
                continue

            # Load prompt content
            benchmark_name = test_config.get("name")
            prompt_file = test_config.get("prompt_file")
            prompt_content = load_prompt(benchmark_name, prompt_file)

            # Load scoring data
            scoring_path = test_folder / "scoring.json"
            scoring_data = load_json(scoring_path) if scoring_path.exists() else None

            # Load request/response data (find the request_*.json file)
            request_files = list(test_folder.glob("request_*.json"))
            request_data = None
            if request_files:
                request_data = load_json(request_files[0])

            # Calculate normalized score
            normalized_score = calculate_normalized_score(scoring_data, benchmark_name)

            # Get benchmark metadata
            meta = get_meta(benchmark_name)

            # Extract tags from benchmark
            tags = meta.get("tags", [])

            # Extract contributors (flat list, no roles)
            contributors = []
            for role_group in meta.get("contributors", []):
                contributors.extend(role_group.get("contributors", []))
            # Remove duplicates while preserving order
            contributors = list(dict.fromkeys(contributors))

            # Determine if test run is hidden
            is_legacy = test_config.get("legacy_test", False)
            is_display_false = not meta.get("display", True)
            hidden = is_legacy or is_display_false

            # Build the test run entry
            test_run = {
                "test_id": test_id,
                "benchmark": benchmark_name,
                "date": date_str,
                "tags": tags,
                "contributors": contributors,
                "hidden": hidden,
                "config": {
                    "provider": test_config.get("provider"),
                    "model": test_config.get("model"),
                    "dataclass": test_config.get("dataclass"),
                    "temperature": test_config.get("temperature"),
                    "role_description": test_config.get("role_description"),
                    "prompt_file": prompt_file,
                    "rules": test_config.get("rules"),
                    "legacy_test": test_config.get("legacy_test", False)
                },
                "prompt": prompt_content,
                "results": request_data,
                "scoring": scoring_data,
                "normalized_score": normalized_score
            }

            # Remove None values from config to keep it clean
            test_run["config"] = {k: v for k, v in test_run["config"].items() if v is not None}

            test_runs_export.append(test_run)

    # Save the export data to a JSON file
    export_path = EXPORT_PATH / "test_runs_export.json"
    with open(export_path, "w", encoding="utf-8") as f:
        json.dump(test_runs_export, f, indent=2, ensure_ascii=False)

    print(f"Exported {len(test_runs_export)} test runs to {export_path}")

if __name__ == "__main__":
    generate_test_runs_export()
