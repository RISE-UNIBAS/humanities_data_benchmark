"""Comparison data for the website, built here because it re-scores runs with the benchmarks'
own scorers: `collected_results/compare_detail/` and `compare_index.json`; also the run counts per
benchmark version, `benchmark_versions.json`, which need the version history's commit times. The
website (benchmark-frontend) reads them with the rest of this repository's files.

Paths and reading go through `scripts/results_index.py`, the reader shared with the dataset
export; these helpers keep the warnings this pipeline prints.

    python -m scripts.compare.generate_all
"""
import logging

from scripts.results_index import (BENCHMARKS_PATH, COLLECTED_RESULTS_PATH, RESULTS_PATH, TESTS_CSV,
                                   TestCatalog, benchmark_meta, benchmark_names, read_json)

EXPORT_PATH = COLLECTED_RESULTS_PATH


def load_json(path):
    """A JSON file's content, or None if it is missing, unreadable or broken."""
    read = read_json(path)
    if read.status == "invalid":
        print(f"Failed to parse {path}")
    return read.value


def get_benchmarks():
    """Return benchmark folder names; folders without a meta.json are not benchmarks."""
    return benchmark_names()


def get_meta(benchmark):
    read = benchmark_meta(benchmark)
    if read.status == "missing":
        logging.error("Could not find meta.json for benchmark %s", benchmark)
        return {}
    if read.status == "invalid":
        print(f"Failed to parse {BENCHMARKS_PATH / benchmark / 'meta.json'}")
    if read.value is None:
        # Unparseable, unreadable, or a file holding a literal null: all fall back to {}.
        logging.error("Could not decode JSON from meta.json for benchmark %s", benchmark)
        return {}
    return read.value


def get_all_tests():
    """benchmarks_tests.csv as dicts: empty values None, temperature a float, legacy_test a bool."""
    if not TESTS_CSV.exists():
        print(f"⚠️ Tests CSV not found: {TESTS_CSV}")
        return []
    return TestCatalog.load().typed_rows()
