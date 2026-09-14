import json
import os
from datetime import datetime

from scripts.ndr_export import BENCHMARKS_PATH, RESULTS_PATH, EXPORT_PATH
from scripts.results_index import iter_run_dirs, read_run
from scripts.ndr_export.meta_utils import calculate_normalized_score, get_meta, load_json
from scripts.ndr_export.pricing_resolver import resolve_pricing
from scripts.ndr_export.test_utils import get_all_tests


def run_timing(request_files):
    """How long a run's inputs took, summed from the stored responses.

    There is no run-level timing anywhere in results/, so it is derived here. Two things
    it deliberately does not claim:

    `total_response_s` is the sum of the per-input durations, which is model time and not
    elapsed time. Runs execute in a ThreadPoolExecutor whose `workers` is a runtime
    argument that is never stored, so elapsed time cannot be recovered from it: one
    magazine_pages run sums to 215s of model time across 46 inputs but spans 10s.

    `span_s` is first to last stored response, which is not run duration either. It
    includes whatever idle sat between requests: a business_letters run spans 62 minutes
    around 5 minutes of model time.

    `mean_response_s` is the honest per-input figure, and the one to compare runs on.
    """
    durations, stamps = [], []
    for path in request_files:
        record = load_json(path)
        if not isinstance(record, dict):
            continue
        value = record.get("duration")
        if isinstance(value, (int, float)):
            durations.append(value)
        stamp = record.get("timestamp")
        if stamp:
            try:
                stamps.append(datetime.fromisoformat(stamp))
            except (TypeError, ValueError):
                pass

    if not durations:
        return None

    timing = {
        "total_response_s": round(sum(durations), 2),
        "mean_response_s": round(sum(durations) / len(durations), 2),
        "slowest_response_s": round(max(durations), 2),
        "inputs_timed": len(durations),
        "inputs_stored": len(request_files),
    }
    if len(stamps) > 1:
        timing["span_s"] = round((max(stamps) - min(stamps)).total_seconds(), 2)
    return timing


def pricing_provenance(request_data, test_config, run_date):
    """The price in force for a run, derived from the pricing table and the run's date.

    Exported under its own key rather than folded into `scoring`, because `scoring` is a
    verbatim copy of the run's scoring.json and this is not in that file: it is derived
    here, fresh on every export, and never written back into results/.

    Note the claim this makes -- "the price in force on that date", not "the price this
    run was charged". The two diverge where a run was costed against a stale table.

    Prefers the provider/model as written in the result file, since that is what the
    model_aliases map is keyed on, and falls back to the test config.
    """
    provider = model = None
    if isinstance(request_data, dict):
        provider, model = request_data.get("provider"), request_data.get("model")
    if not (provider and model):
        provider, model = test_config.get("provider"), test_config.get("model")
    if not (provider and model and run_date):
        return None

    # Unbounded: the table has gaps longer than 30 days in the past, and a stale price
    # carrying an explicit age is more useful than no provenance at all.
    pricing = resolve_pricing(provider, model, run_date, max_age_days=None)
    if pricing is None:
        return None

    return {
        "bucket_date": pricing.bucket_date,
        "age_days": pricing.age_days,
        "input_price_per_million": pricing.input_price,
        "output_price_per_million": pricing.output_price,
    }


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

    for run in iter_run_dirs():
        # Get test configuration
        test_config = tests_by_id.get(run.test_id)
        if not test_config:
            print(f"Warning: No test config found for {run.test_id}")
            continue

        # Load prompt content
        benchmark_name = test_config.get("name")
        prompt_file = test_config.get("prompt_file")
        prompt_content = load_prompt(benchmark_name, prompt_file)

        # Load scoring data
        scoring_path = run.path / "scoring.json"
        scoring_data = load_json(scoring_path) if scoring_path.exists() else None

        # Load request/response data (find the request_*.json file)
        request_files = [request.path for request in read_run(run).requests]
        request_data = None
        if request_files:
            request_data = load_json(request_files[0])
        # Note that `results` above is one arbitrary input, so its `duration` is that
        # input's, never the run's. The run-level figures come from every file.
        timing = run_timing(request_files)

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
            "test_id": run.test_id,
            "benchmark": benchmark_name,
            "date": run.date,
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
            "pricing": pricing_provenance(request_data, test_config, run.date),
            "timing": timing,
            "normalized_score": normalized_score
        }

        # Remove None values from config to keep it clean
        test_run["config"] = {k: v for k, v in test_run["config"].items() if v is not None}

        test_runs_export.append(test_run)

    # Save the export data to a JSON file
    os.makedirs(EXPORT_PATH, exist_ok=True)
    export_path = EXPORT_PATH / "test_runs_export.json"
    with open(export_path, "w", encoding="utf-8") as f:
        json.dump(test_runs_export, f, indent=2, ensure_ascii=False)

    print(f"Exported {len(test_runs_export)} test runs to {export_path}")

if __name__ == "__main__":
    generate_test_runs_export()
