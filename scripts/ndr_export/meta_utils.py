import logging
from pathlib import Path

from scripts.ndr_export import BENCHMARKS_PATH
from scripts.results_index import benchmark_meta, benchmark_names, read_json


def get_benchmarks():
    """Return benchmark folder names; folders without a meta.json are not benchmarks."""
    return benchmark_names()

def get_benchmarks_with_meta_key(key):
    benchmarks = get_benchmarks()
    benchmarks_with_key = []
    for benchmark in benchmarks:
        meta = get_meta(benchmark)
        if key in meta:
            benchmarks_with_key.append(benchmark)
    return benchmarks_with_key

def get_meta(benchmark):
    read = benchmark_meta(benchmark)
    if read.status == "missing":
        logging.error("Could not find meta.json for benchmark %s", benchmark)
        return {}
    if read.status == "invalid":
        print(f"Failed to parse {BENCHMARKS_PATH / benchmark / 'meta.json'}")
    if read.value is None:
        # Unparseable, unreadable, or a file holding a literal null: all three left
        # meta_data None before, and all three log and fall back to {}.
        logging.error("Could not decode JSON from meta.json for benchmark %s", benchmark)
        return {}
    return read.value

def get_meta_value(benchmark, key):
    meta = get_meta(benchmark)
    try:
        return meta[key]
    except KeyError:
        logging.error("Key %s not found in meta.json for benchmark %s", key, benchmark)
        return None

def load_json(path):
    """Safely load a JSON file, return None if missing or broken.

    One widening over the version this replaces: an unreadable file used to propagate the
    OSError and now returns None, silently, because the shared reader classifies it as
    "unreadable" rather than "invalid". Inert on this corpus -- a full export opens every
    file -- but it is a real change, not a no-op.
    """
    path = Path(path)
    read = read_json(path)
    if read.status == "invalid":
        print(f"Failed to parse {path}")
    return read.value

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
    # Check if score is already in 0-100 range (e.g., from fuzz.ratio)
    # vs 0-1 range (e.g., from calculate_fuzzy_score)
    if score_value > 1.0:
        # Score is already in 0-100 range, no need to multiply
        if order == "desc":
            normalized = score_value
        else:  # order == "asc"
            normalized = max(0, 100 - score_value)
    else:
        # Score is in 0-1 range, multiply by 100
        if order == "desc":
            normalized = score_value * 100
        else:  # order == "asc"
            normalized = max(0, 100 - (score_value * 100))

    return min(100, max(0, normalized))