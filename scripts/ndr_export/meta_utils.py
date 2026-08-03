import os
import json
import logging
from pathlib import Path

from scripts.ndr_export import BENCHMARKS_PATH


def get_benchmarks():
    """Return benchmark folder names; folders without a meta.json are not benchmarks."""
    return [name for name in os.listdir(BENCHMARKS_PATH)
            if os.path.isdir(os.path.join(BENCHMARKS_PATH, name)) and not name.startswith('.')
            and os.path.isfile(os.path.join(BENCHMARKS_PATH, name, "meta.json"))]

def get_benchmarks_with_meta_key(key):
    benchmarks = get_benchmarks()
    benchmarks_with_key = []
    for benchmark in benchmarks:
        meta = get_meta(benchmark)
        if key in meta:
            benchmarks_with_key.append(benchmark)
    return benchmarks_with_key

def get_meta(benchmark):
    benchmark_meta_path = os.path.join(BENCHMARKS_PATH, benchmark, "meta.json")
    if os.path.isfile(benchmark_meta_path):
        meta_data = load_json(benchmark_meta_path)
        if meta_data is None:
            logging.error("Could not decode JSON from meta.json for benchmark %s", benchmark)
            return {}
        return meta_data
    logging.error("Could not find meta.json for benchmark %s", benchmark)
    return {}

def get_meta_value(benchmark, key):
    meta = get_meta(benchmark)
    try:
        return meta[key]
    except KeyError:
        logging.error("Key %s not found in meta.json for benchmark %s", key, benchmark)
        return None

def load_json(path):
    """Safely load a JSON file, return None if missing or broken."""
    if isinstance(path, str):
        path = Path(path)

    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Failed to parse {path}")
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