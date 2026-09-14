"""Pytest configuration file to set up proper import paths."""
import sys
import os
from types import SimpleNamespace

import pytest

# Add the scripts directory to Python path
scripts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts')
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


@pytest.fixture
def make_scorer():
    """Build a benchmark scorer instance without running __init__ (no AI client,
    no API key — CI-safe). Scoring methods only need prepare_scoring_data (base
    class) and, for some benchmarks, self.rules; inject any extra attrs via kwargs.
    """
    def _make(cls, rules=None, **attrs):
        instance = cls.__new__(cls)
        instance.rules = rules
        for key, value in attrs.items():
            setattr(instance, key, value)
        return instance
    return _make


@pytest.fixture
def response():
    """Build a minimal LLMResponse-like stub exposing .parsed and .text."""
    def _response(parsed=None, text=""):
        return SimpleNamespace(parsed=parsed, text=text)
    return _response

@pytest.fixture
def metrics():
    """A score with its comparison detail stripped off.

    Scorers return `field_scores` alongside their metrics -- the values they actually
    compared and the similarity assigned to each -- so a comparison view can show the
    scorer's own judgement instead of re-deriving one that would disagree with it.
    These tests are about the metrics, so drop that rather than restate a large nested
    structure in every expectation.
    """
    def _metrics(score):
        if not isinstance(score, dict):
            return score
        return dict((k, v) for k, v in score.items() if k != "field_scores")
    return _metrics


@pytest.fixture
def make_corpus(tmp_path):
    """Write a `results/`-shaped tree from a compact spec.

    The exporter's hard cases are all shapes on disk -- a legacy filename prefix, a run
    with no scoring, a request file that will not parse -- and spelling each one out in
    mkdir/write_text calls buries the case being tested. The spec is
    `{date: {test_id: {"requests": {...}, "scoring": ...}}}`.

    A request key that already starts with `request_` is used as the filename verbatim,
    which is how a legacy `request_T01_jaccuse.json` under `T0001` gets written; anything
    else is treated as an object id and becomes `request_<test_id>_<object_id>.json`.
    Values are JSON-encoded when they are dicts or lists and written verbatim when they
    are strings, so malformed JSON is expressible. `scoring` follows the same rule and is
    omitted entirely when absent or None.
    """
    def _make(spec, root="results"):
        base = tmp_path / root
        for date, runs in spec.items():
            for test_id, content in (runs or {}).items():
                run_dir = base / date / test_id
                run_dir.mkdir(parents=True, exist_ok=True)
                for key, payload in (content.get("requests") or {}).items():
                    name = key if key.startswith("request_") else "request_%s_%s.json" % (test_id, key)
                    _write(run_dir / name, payload)
                if content.get("scoring") is not None:
                    _write(run_dir / "scoring.json", content["scoring"])
        base.mkdir(parents=True, exist_ok=True)
        return base
    return _make


@pytest.fixture
def write_tests_csv(tmp_path):
    """Write a benchmarks_tests.csv with the real column set, returning its path.

    Rows are given as dicts and missing columns default to the empty string, because the
    distinction the readers care about is empty-vs-absent-vs-set and a test should only
    have to state the columns it is about.
    """
    columns = ["id", "name", "provider", "model", "dataclass", "temperature",
               "role_description", "prompt_file", "rules", "legacy_test"]

    def _write(rows, name="benchmarks_tests.csv"):
        import csv as _csv
        path = tmp_path / name
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = _csv.DictWriter(handle, fieldnames=columns)
            writer.writeheader()
            for row in rows:
                writer.writerow(dict((c, row.get(c, "")) for c in columns))
        return path
    return _write


def _write(path, payload):
    import json as _json
    text = payload if isinstance(payload, str) else _json.dumps(payload)
    path.write_text(text, encoding="utf-8")
