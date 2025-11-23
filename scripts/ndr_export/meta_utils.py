import os
import json
import logging
from pathlib import Path

from scripts.ndr_export import BENCHMARKS_PATH


def get_benchmarks():
    return [name for name in os.listdir(BENCHMARKS_PATH)
            if os.path.isdir(os.path.join(BENCHMARKS_PATH, name)) and not name.startswith('.')]

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