"""Run a benchmark's own scorer over already-stored results, without a model call.

The response and the ground truth are both on disk, so a scorer can simply be run
again. Three callers need that and were growing their own copies of the setup:

  * `scripts/rescore.py` -- proving a change to a scorer leaves its numbers untouched
  * `tests/integrity/test_field_scores_integrity.py` -- the `field_scores` contract
  * `scripts/ndr_export/generate_compare_detail.py` -- comparison detail for runs whose
    scorer did not record any at the time

Benchmarks are instantiated with `__new__`, skipping `__init__`: `__init__` builds an API
client and wants credentials, while the scoring methods reach for nothing but `self.name`,
`self.benchmark_dir` and `self.rules`.

`rules` is not optional decoration. `personnel_cards` reads `score_diplomatic_transcript`,
`score_interpretation` and `score_is_crossed_out` from it to choose which fields to score,
so scoring with `rules=None` where the run had rules would score a different field set
than the run did. The run's own row in `benchmarks/benchmarks_tests.csv` is therefore the
source, parsed exactly as `Benchmark.__init__` parses it.

What this does *not* reconstruct is the state of the data at run time. Ground truths are
revised -- 568 stored request scores no longer reproduce -- so a re-score reflects today's
ground truth, not the one the run was scored against. Callers that publish re-scored
values must say so; see `generate_compare_detail.py`.
"""
import importlib
import json
import logging
import re
import sys
from pathlib import Path

# Re-exported rather than redefined: rescore.py imports RESULTS_PATH from this module,
# and generate_compare_detail.py and the integrity tests import other names from it. Every
# entry point puts the project root on sys.path before importing this module -- rescore.py
# does it explicitly, tests/conftest.py does it for the suite -- so the dotted form
# resolves in all of them.
from scripts.results_index import (BENCHMARKS_PATH, PROJECT_ROOT,  # noqa: F401
                                   RESULTS_PATH, TESTS_CSV, TestCatalog)

for _path in (PROJECT_ROOT, PROJECT_ROOT / "scripts"):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

# Example/smoke benchmarks used to exercise the harness, not real datasets.
SCAFFOLD_BENCHMARKS = {"test_benchmark", "test_benchmark2"}

logger = logging.getLogger(__name__)
"""A named logger, not the root one: calling logging.info() at module level installs a
root handler and silently voids the runners' own basicConfig()."""


class StoredAnswer:
    """Stands in for LLMResponse where a scorer only reads the stored payload.

    `Benchmark.prepare_scoring_data` returns `answer.parsed`, and the scorers that take
    the response object read `.parsed` or `.text`. No scoring path needs the live client,
    the usage block or the raw envelope.
    """

    def __init__(self, record):
        self.parsed = record.get("parsed")
        self.text = record.get("text")
        self.usage = record.get("usage")
        self.finish_reason = record.get("finish_reason")


def read_tests():
    """The test CSV as {test_id: row}."""
    return TestCatalog.load().raw_by_id()


def benchmark_of_test(tests=None):
    """{test_id: benchmark}. A run directory does not record its own benchmark."""
    if tests is None:
        return TestCatalog.load().benchmark_map()
    return dict((test_id, (row.get("name") or "").strip())
                for test_id, row in tests.items() if (row.get("name") or "").strip())


def rules_of_test(test_id, tests=None):
    """The run's `rules`, parsed as `Benchmark.__init__` parses it (None when unusable).

    Parsed here rather than through `TestCatalog.rules_of` so the warning survives: the
    shared layer is silent, and a run scored with the wrong field set is worth a line in
    the log. The two are held to the same answer by test_results_index_integrity.
    """
    rows = tests if tests is not None else TestCatalog.load().raw_by_id()
    raw = (rows.get(test_id) or {}).get("rules")
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        logger.warning("Unusable rules for %s: %r", test_id, raw)
        return None


def load_scorer(benchmark, rules=None):
    """A scorer instance for `benchmark`, able to score but with no API client.

    Only a class declared in the benchmark's own module is considered, so a `Benchmark`
    base class imported into it is not mistaken for the scorer -- and so this does not
    depend on which of `benchmark_base` / `scripts.benchmark_base` the module imported,
    which are two distinct classes and make `issubclass` fail for every benchmark.
    """
    module = importlib.import_module("benchmarks.%s.benchmark" % benchmark)
    for attr in vars(module).values():
        if (isinstance(attr, type)
                and getattr(attr, "__module__", None) == module.__name__
                and callable(getattr(attr, "score_request_answer", None))):
            scorer = attr.__new__(attr)
            scorer.name = benchmark
            scorer.benchmark_dir = str(BENCHMARKS_PATH / benchmark)
            scorer.rules = rules
            return scorer
    raise LookupError("no scorer class declared in benchmarks.%s.benchmark" % benchmark)


def ground_truth_for(benchmark, basename):
    path = BENCHMARKS_PATH / benchmark / "ground_truths" / (basename + ".json")
    if not path.is_file():
        return None
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None


REQUEST_FILE = re.compile(r"^request_(?P<stem>.+)\.json$")


def object_id_of(file_name, test_id, fallback_prefix=None):
    """The input's identity, which exists only in the request filename.

    The prefix is usually the directory's test id, but not always: the earliest runs
    stored `request_T01_jaccuse.json` under `T0001`. So the directory id is tried first
    and a prefix observed in the directory is the fallback. Returns None rather than
    guessing when neither applies -- a greedy split on underscores would silently
    mangle ids like `Se_18_Bilanz1967_page_4`.
    """
    match = REQUEST_FILE.match(file_name)
    if not match:
        return None
    stem = match.group("stem")
    for prefix in (test_id, fallback_prefix):
        if prefix and stem.startswith(prefix + "_"):
            object_id = stem[len(prefix) + 1:]
            return object_id or None
    return None


def observed_prefix(file_names):
    """The prefix actually used in a run directory, from its first request file."""
    for name in sorted(file_names):
        match = REQUEST_FILE.match(name)
        if match:
            return match.group("stem").split("_")[0]
    return None


def iter_run_inputs(run_dir, test_id=None):
    """Yields (object_id, record, StoredAnswer, ground_truth) for one run directory.

    Inputs whose ground truth is missing or whose request file will not parse are
    skipped: there is nothing to compare them against. `record` is the whole stored
    answer, so a caller can read the score the run itself recorded.
    """
    run_dir = Path(run_dir)
    test_id = test_id or run_dir.name
    benchmark = benchmark_of_test().get(test_id)
    if not benchmark:
        return

    file_names = [p.name for p in run_dir.glob("request_*.json")]
    fallback = observed_prefix(file_names)

    for name in sorted(file_names):
        object_id = object_id_of(name, test_id, fallback)
        if object_id is None:
            continue
        truth = ground_truth_for(benchmark, object_id)
        if truth is None:
            continue
        try:
            with (run_dir / name).open(encoding="utf-8") as handle:
                record = json.load(handle)
        except (OSError, json.JSONDecodeError):
            continue
        yield object_id, record, StoredAnswer(record), truth


def iter_runs(benchmark=None, newest_first=False):
    """Yields (run_dir, test_id, benchmark) for every stored run with a known benchmark."""
    if not RESULTS_PATH.is_dir():
        return
    mapping = benchmark_of_test()
    dates = sorted((p for p in RESULTS_PATH.iterdir() if p.is_dir()), reverse=newest_first)
    for date_dir in dates:
        for run_dir in sorted((p for p in date_dir.iterdir() if p.is_dir()),
                              reverse=newest_first):
            name = mapping.get(run_dir.name)
            if name and (benchmark is None or name == benchmark):
                yield run_dir, run_dir.name, name


def numeric_metrics(score):
    """The scalar part of a score, so nested detail does not count as a metric."""
    if not isinstance(score, dict):
        return score
    return dict((key, value) for key, value in score.items()
                if not isinstance(value, (dict, list)) and key != "__error")
