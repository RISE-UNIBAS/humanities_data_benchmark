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
import sys
from pathlib import Path

# Re-exported rather than redefined: rescore.py imports RESULTS_PATH from this module,
# and generate_compare_detail.py and the integrity tests import other names from it. Every
# entry point puts the project root on sys.path before importing this module -- rescore.py
# does it explicitly, tests/conftest.py does it for the suite -- so the dotted form
# resolves in all of them.
from scripts.results_index import (BENCHMARKS_PATH, PROJECT_ROOT,  # noqa: F401
                                   RESULTS_PATH, TESTS_CSV, RunDir, TestCatalog,
                                   iter_request_records, iter_run_dirs, known_tests)

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


def iter_run_inputs(run_dir, test_id=None, catalog=None):
    """Yields (object_id, record, StoredAnswer, ground_truth) for one run directory.

    Inputs whose ground truth is missing or whose request file will not parse are
    skipped: there is nothing to compare them against. That is a filter over the shared
    layer's complete iteration, not a property of the walk -- the dataset export reads
    the same directories and must keep every one of them. `record` is the whole stored
    answer, so a caller can read the score the run itself recorded.

    Pass `catalog` when looping over many runs; otherwise each call re-reads the test CSV.
    """
    catalog = catalog if catalog is not None else TestCatalog.load()
    run_dir = Path(run_dir)
    test_id = test_id or run_dir.name
    benchmark = catalog.benchmark_of(test_id)
    if not benchmark:
        return

    # A RunDir rather than the bare path, so a caller-supplied test_id still drives the
    # filename prefix the way it did when this function derived it itself.
    run = RunDir(run_dir, run_dir.parent.name, test_id,
                 "%s@%s" % (test_id, run_dir.parent.name))

    for request, read in iter_request_records(run):
        if request.object_id is None or read.status != "ok":
            continue
        truth = ground_truth_for(benchmark, request.object_id)
        if truth is None:
            continue
        yield request.object_id, read.value, StoredAnswer(read.value), truth


def iter_runs(benchmark=None, newest_first=False):
    """Yields (run_dir, test_id, benchmark) for every stored run with a known benchmark.

    The "with a known benchmark" part is `known_tests`, the shared layer's named filter.
    Runs whose test id is not in the CSV are dropped here because a scorer cannot be
    chosen for them, not because the walk cannot see them.
    """
    catalog = TestCatalog.load()
    for run, name in known_tests(iter_run_dirs(newest_first=newest_first), catalog,
                                 benchmark):
        yield run.path, run.test_id, name


def numeric_metrics(score):
    """The scalar part of a score, so nested detail does not count as a metric."""
    if not isinstance(score, dict):
        return score
    return dict((key, value) for key, value in score.items()
                if not isinstance(value, (dict, list)) and key != "__error")
