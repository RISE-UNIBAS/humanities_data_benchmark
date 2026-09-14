"""`scripts/results_index.py` against the real corpus and against what it replaces.

Two jobs, and the first one is temporary in spirit but permanent in practice.

**Equivalence.** The shared layer takes over from `offline_scoring`'s walk and CSV reader,
`ndr_export.test_utils.get_all_tests` and `ndr_export.meta_utils.get_benchmarks`. These
tests were written before any caller moved, so they were green against the old code and
must stay green as each caller migrates. That is what makes the migration provably
behaviour-preserving rather than merely diffed afterwards: a byte-diff of
`collected_results/` can only be run once the whole pipeline has moved, and it cannot say
which step broke.

**Corpus invariants.** The parsing rules the layer implements are only correct because of
facts about `results/` -- that it is two levels deep, that it holds nothing but request
and scoring files, that every request filename resolves to an object id under either the
directory's test id or a prefix observed beside it. Those facts are load-bearing for the
dataset export's keys, so they are asserted rather than assumed. The day the runner starts
writing something else, these fail instead of the export silently dropping rows.

Run logic-only with: pytest -m "not integrity".

Deliberately not asserted: that every test id under `results/` appears in the CSV. It is
true today (1,638 of 1,638), but an unknown id is a state the dataset export is required
to survive and emit a row for -- asserting it would turn a supported condition into a red
build.
"""
import pytest

from scripts import offline_scoring
from scripts.ndr_export.meta_utils import get_benchmarks
from scripts.ndr_export.test_utils import get_all_tests
from scripts.results_index import (RESULTS_PATH, TEST_RUNS_PATH, TestCatalog,
                                   benchmark_names, iter_run_dirs, known_tests,
                                   object_id_of, observed_prefix, read_run)

pytestmark = pytest.mark.integrity


@pytest.fixture(scope="module")
def catalog():
    return TestCatalog.load()


@pytest.fixture(scope="module")
def run_dirs():
    """The whole walk once; every test below would otherwise re-list 2,371 directories."""
    return list(iter_run_dirs())


def test_iter_runs_matches_the_filtered_shared_walk(catalog):
    old = list(offline_scoring.iter_runs())
    new = [(run.path, run.test_id, name)
           for run, name in known_tests(iter_run_dirs(), catalog)]
    assert old == new, (
        "offline_scoring.iter_runs and known_tests(iter_run_dirs()) disagree on %d runs. "
        "known_tests is meant to be exactly that filter, extracted."
        % len(set(map(str, old)) ^ set(map(str, new))))


def test_iter_runs_matches_newest_first(catalog):
    old = list(offline_scoring.iter_runs(newest_first=True))
    new = [(run.path, run.test_id, name)
           for run, name in known_tests(iter_run_dirs(newest_first=True), catalog)]
    assert old == new, "newest_first must reverse both levels, not just the dates"


def test_iter_runs_matches_for_one_benchmark(catalog):
    old = list(offline_scoring.iter_runs("business_letters"))
    new = [(run.path, run.test_id, name)
           for run, name in known_tests(iter_run_dirs(), catalog, "business_letters")]
    assert old == new and old, "the benchmark filter must select the same runs"


def test_get_all_tests_matches_the_catalog(catalog):
    assert get_all_tests() == catalog.typed_rows()


def test_read_tests_matches_the_catalog(catalog):
    assert offline_scoring.read_tests() == catalog.raw_by_id()


def test_benchmark_of_test_matches_the_catalog(catalog):
    assert offline_scoring.benchmark_of_test() == catalog.benchmark_map()


def test_rules_of_test_matches_the_catalog(catalog):
    """personnel_cards picks its scored fields out of these, so a drift changes scores."""
    disagreed = [test_id for test_id in catalog.raw_by_id()
                 if offline_scoring.rules_of_test(test_id) != catalog.rules_of(test_id)]
    assert not disagreed, "rules differ for %s" % disagreed[:5]


def test_get_benchmarks_matches_benchmark_names():
    assert get_benchmarks() == benchmark_names()


def test_the_walk_reaches_every_run_directory(run_dirs):
    """Counted independently, so the walk cannot certify itself."""
    expected = sorted(str(run) for date in RESULTS_PATH.iterdir() if date.is_dir()
                      for run in date.iterdir() if run.is_dir())
    assert sorted(str(r.path) for r in run_dirs) == expected
    assert len(expected) > 2000, "results/ looks unexpectedly small (%d)" % len(expected)


def test_the_walk_reaches_every_request_file(run_dirs):
    expected = len(list(RESULTS_PATH.glob("*/*/request_*.json")))
    seen = sum(len(read_run(run).requests) for run in run_dirs)
    assert seen == expected, (
        "read_run found %d request files, the tree holds %d" % (seen, expected))


def test_results_is_two_levels_of_two_known_file_kinds(run_dirs):
    """The dataset export's inventory step treats anything else as a release blocker."""
    unexpected = []
    for run in run_dirs:
        for entry in run.path.iterdir():
            if entry.is_dir():
                unexpected.append("%s is a directory inside a run" % entry)
            elif entry.name != "scoring.json" and not entry.name.startswith("request_"):
                unexpected.append(str(entry))
    assert not unexpected, (
        "results/ holds %d files that are neither request_*.json nor scoring.json:%s"
        % (len(unexpected), "".join("\n  " + line for line in unexpected[:10])))


def test_every_request_filename_resolves_to_an_object_id(run_dirs):
    """`(run_id, object_id)` is the dataset export's request key; an unresolved name has none.

    Both prefixes are needed: 4,296 files in 188 early run directories name a test id the
    directory does not, because the ids were re-padded without renaming the files.
    """
    unresolved = [str(request.path) for run in run_dirs
                  for request in read_run(run).requests if request.object_id is None]
    assert not unresolved, (
        "%d request filenames did not resolve under either the directory's test id or a "
        "prefix observed beside them -- see object_id_of:%s"
        % (len(unresolved), "".join("\n  " + line for line in unresolved[:10])))


def test_object_ids_are_unique_within_a_run(run_dirs):
    collisions = []
    for run in run_dirs:
        seen = {}
        for request in read_run(run).requests:
            if request.object_id in seen:
                collisions.append("%s: %s and %s share %r"
                                  % (run.run_id, seen[request.object_id], request.name,
                                     request.object_id))
            seen[request.object_id] = request.name
    assert not collisions, (
        "(run_id, object_id) is not a key:%s"
        % "".join("\n  " + line for line in collisions[:10]))


def test_the_legacy_prefix_runs_are_still_reachable(run_dirs):
    """A regression here would silently drop the oldest runs from any export."""
    legacy = [run for run in run_dirs
              if (lambda files: files.prefix and files.prefix != run.test_id)(read_run(run))]
    assert legacy, (
        "no run directory uses a filename prefix other than its own id any more. If the "
        "files were renamed this test should go; if not, observed_prefix has regressed.")
    for run in legacy[:20]:
        assert all(r.object_id for r in read_run(run).requests), run.run_id


def test_tests_csv_has_no_short_or_long_rows(catalog):
    """`typed_rows` inherits an AttributeError on a short row; this keeps it unreachable."""
    malformed = [row.get("id") for row in catalog.rows
                 if None in row or None in row.values()]
    assert not malformed, (
        "csv.DictReader produced a None key or value for %s, which means a row has the "
        "wrong number of fields; typed_rows() would raise on it" % malformed[:5])


def test_unknown_ids_survive_the_walk_and_only_the_filter_drops_them(catalog):
    """Both halves of the layer's contract, against real data rather than a fixture.

    `test_runs/` has the same shape as `results/` and holds ad-hoc runs whose ids were
    never in the CSV -- exactly the case the dataset export must emit a row for and the
    frontend must skip.
    """
    if not TEST_RUNS_PATH.is_dir():
        pytest.skip("no test_runs/ tree in this checkout")

    walked = list(iter_run_dirs(TEST_RUNS_PATH))
    assert walked, "test_runs/ exists but the walk found nothing in it"

    unknown = [run for run in walked if catalog.benchmark_of(run.test_id) is None]
    assert unknown, (
        "test_runs/ no longer holds an id absent from the CSV, so this test is no longer "
        "exercising the unknown-id case; point it at another tree or build a fixture")

    kept = [run.test_id for run, _ in known_tests(walked, catalog)]
    assert not set(kept) & {run.test_id for run in unknown}, (
        "known_tests let an unknown id through; it is the filter, not the walk")


def test_object_id_helpers_agree_with_the_files_on_disk(run_dirs):
    """read_run must apply object_id_of/observed_prefix, not a private copy of the rule."""
    for run in run_dirs[:200]:
        files = read_run(run)
        names = [request.name for request in files.requests]
        assert files.prefix == observed_prefix(names)
        for request in files.requests:
            assert request.object_id == object_id_of(request.name, run.test_id,
                                                     files.prefix)
