"""Comparison data for the website, built here because it re-scores runs with the benchmarks'
own scorers: `collected_results/compare_detail/` and `compare_index.json`. The website
(benchmark-frontend) reads them with the rest of this repository's files.

    python -m scripts.compare.generate_all
"""
import csv
import json
import logging
import os
from pathlib import Path

_PROJECT_ROOT = Path(__file__).parent.parent.parent

RESULTS_PATH = _PROJECT_ROOT / "results"
EXPORT_PATH = _PROJECT_ROOT / "collected_results"
BENCHMARKS_PATH = _PROJECT_ROOT / "benchmarks"
TESTS_CSV = BENCHMARKS_PATH / "benchmarks_tests.csv"


def load_json(path):
    """Safely load a JSON file, return None if missing or broken."""
    path = Path(path)
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Failed to parse {path}")
        return None


def get_benchmarks():
    """Return benchmark folder names; folders without a meta.json are not benchmarks."""
    return [name for name in os.listdir(BENCHMARKS_PATH)
            if os.path.isdir(os.path.join(BENCHMARKS_PATH, name)) and not name.startswith('.')
            and os.path.isfile(os.path.join(BENCHMARKS_PATH, name, "meta.json"))]


def get_meta(benchmark):
    meta = load_json(BENCHMARKS_PATH / benchmark / "meta.json")
    if meta is None:
        logging.error("Could not read meta.json for benchmark %s", benchmark)
        return {}
    return meta


def get_all_tests():
    """benchmarks_tests.csv as dicts, empty values as None."""
    with TESTS_CSV.open("r", encoding="utf-8") as f:
        return [{k: (v if v != "" else None) for k, v in row.items()} for row in csv.DictReader(f)]
