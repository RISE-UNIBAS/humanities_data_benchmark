"""Paths the frontend export reads and writes.

The corpus paths come from `scripts/results_index.py`, which is the single definition
shared with the dataset export; the rest are this pipeline's own inputs and output and
stay here. Every name this module has always exported is still exported, because the
generators import them from here.
"""
from scripts.results_index import (BENCHMARKS_PATH, COLLECTED_RESULTS_PATH, PROJECT_ROOT,
                                   RESULTS_PATH, TESTS_CSV)

_PROJECT_ROOT = PROJECT_ROOT

EXPORT_PATH = COLLECTED_RESULTS_PATH
PRICING_PATH = _PROJECT_ROOT / "scripts" / "data" / "pricing.json"
MODEL_ALIASES_PATH = _PROJECT_ROOT / "scripts" / "data" / "model_aliases.json"
CONTRIBUTORS_PATH = _PROJECT_ROOT / "scripts" / "data" / "contributors.json"
VOCABULARIES_PATH = _PROJECT_ROOT / "vocabularies"
