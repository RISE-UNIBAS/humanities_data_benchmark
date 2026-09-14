"""The dataset exporter against the real corpus.

The unit tests prove the exporter handles each awkward shape correctly. They cannot prove
it handles *every* file, and for an archive that is the claim that matters: an analyst who
finds 104,000 rows where the tree holds 104,395 files has no way to discover which 395 are
missing or why. So this reconciles the output against the tree it came from, file by file.

It also holds the metric dictionary honest. `extract.Extractor.run` raises on a numeric
value it cannot name, so simply completing a full pass is the assertion that every number
in the corpus has a definition. The day a scorer grows a key, this fails instead of the
release shipping an unexplained column.

Costs about 90 seconds: it reads all 104,395 request files and all 2,362 scoring files
once, in a module-scoped fixture shared by every test below.

Run logic-only with: pytest -m "not integrity".
"""
import collections

import pytest

from scripts.export_dataset.extract import Extractor
from scripts.export_dataset.schema import SCORING_STATUSES, PARSE_STATUSES
from scripts.results_index import RESULTS_PATH, iter_run_dirs, read_run

pytestmark = pytest.mark.integrity


@pytest.fixture(scope="module")
def extracted():
    """One full pass over the corpus. Completing it at all is the first assertion."""
    return Extractor().run()


@pytest.fixture(scope="module")
def tree():
    runs = list(iter_run_dirs())
    requests = sum(len(read_run(run).requests) for run in runs)
    return {"run_dirs": runs, "request_files": requests}


def test_every_run_directory_produced_exactly_one_row(extracted, tree):
    expected = sorted(run.run_id for run in tree["run_dirs"])
    got = sorted(row["run_id"] for row in extracted.runs)
    missing = set(expected) - set(got)
    assert got == expected, (
        "%d run directories produced no row (%s...). Every directory must reconcile to a "
        "row or to a release-blocking diagnostic; silently dropping one is the failure "
        "this export exists to prevent." % (len(missing), sorted(missing)[:5]))


def test_every_request_file_produced_exactly_one_row(extracted, tree):
    assert len(extracted.requests) == tree["request_files"], (
        "%d request rows for %d files on disk"
        % (len(extracted.requests), tree["request_files"]))


def test_run_counts_agree_with_the_request_table(extracted):
    """n_requests is derived per run; it must add up to the table it summarises."""
    assert sum(row["n_requests"] for row in extracted.runs) == len(extracted.requests)


def test_run_ids_are_unique(extracted):
    counts = collections.Counter(row["run_id"] for row in extracted.runs)
    assert not [k for k, n in counts.items() if n > 1]


def test_request_keys_are_unique(extracted):
    counts = collections.Counter((row["run_id"], row["object_id"])
                                 for row in extracted.requests)
    dupes = [k for k, n in counts.items() if n > 1]
    assert not dupes, "(run_id, object_id) is the request key: %s" % dupes[:5]


def test_score_keys_are_unique(extracted):
    counts = collections.Counter(
        (s["run_id"], s["object_id"], s["level"], s["field_path"], s["metric_id"])
        for s in extracted.scores)
    dupes = [k for k, n in counts.items() if n > 1]
    assert not dupes, "duplicate score observation: %s" % dupes[:3]


def test_every_score_row_joins_back(extracted):
    runs = set(row["run_id"] for row in extracted.runs)
    requests = set((row["run_id"], row["object_id"]) for row in extracted.requests)
    orphan_runs, orphan_requests = [], []
    for s in extracted.scores:
        if s["run_id"] not in runs:
            orphan_runs.append(s["run_id"])
        if s["level"] != "run" and (s["run_id"], s["object_id"]) not in requests:
            orphan_requests.append((s["run_id"], s["object_id"]))
    assert not orphan_runs, "score rows for runs that have no row: %s" % orphan_runs[:3]
    assert not orphan_requests, "score rows with no request: %s" % orphan_requests[:3]


def test_field_path_is_non_null_exactly_at_field_level(extracted):
    """The CSV reader depends on this: it is how an empty path is told from a null one."""
    wrong = [s for s in extracted.scores
             if (s["level"] == "field") != (s["field_path"] is not None)]
    assert not wrong, (
        "%d score rows break the field_path invariant. writers.read_csv reconstructs the "
        "empty-string path from `level`, so a violation makes the CSV lossy." % len(wrong))


def test_the_empty_field_path_is_present_and_is_not_a_null(extracted):
    """Four benchmarks store a field_scores entry under the empty string."""
    empty = [s for s in extracted.scores if s["field_path"] == ""]
    assert empty, ("no field observation uses the empty-string path any more. If the "
                   "scorers changed this test should go; if not, it has regressed to null.")
    assert all(s["level"] == "field" for s in empty)


def test_every_payload_record_joins_back_to_a_request(extracted):
    requests = set((row["run_id"], row["object_id"]) for row in extracted.requests)
    orphans = [(r["run_id"], r["object_id"]) for records in extracted.payloads.values()
               for r in records if (r["run_id"], r["object_id"]) not in requests]
    assert not orphans, "payload records with no row: %s" % orphans[:3]


def test_statuses_stay_inside_their_vocabulary(extracted):
    run_statuses = set(row["scoring_status"] for row in extracted.runs)
    assert run_statuses <= set(SCORING_STATUSES), run_statuses
    parse = set(row["parse_status"] for row in extracted.requests)
    assert parse <= set(PARSE_STATUSES), parse


def test_no_token_count_was_invented(extracted):
    """A zero must come from the file. This checks the reverse: that nulls survive.

    If a future change defaulted a missing token count to 0, this fails, because the
    corpus genuinely contains requests with no usage block at all.
    """
    assert any(row["input_tokens"] is None for row in extracted.requests), (
        "every request now has an input_tokens value, which the corpus does not support: "
        "some stored records have no usage block. A missing count has become a zero.")


def test_stored_costs_were_not_backfilled_from_the_derived_ones(extracted):
    """The two columns answer different questions and must not have been merged."""
    disagree = [r for r in extracted.requests
                if r["stored_estimated_cost_usd"] is None
                and r["derived_total_cost_usd"] is not None]
    assert disagree, (
        "no request has a derived cost without a stored one, which would mean the stored "
        "column had been filled in from the derived one. They are separate claims.")


def test_timestamps_were_not_given_an_invented_timezone(extracted):
    """Every stored timestamp is naive, so timestamp_utc is null throughout.

    If this starts failing because the runner began recording an offset, that is good
    news and the test should be narrowed -- not because a default timezone crept in.
    """
    converted = [r for r in extracted.requests if r["timestamp_utc"] is not None]
    assert not converted, (
        "%d timestamps were converted to UTC. The corpus records local time with no "
        "offset, so a conversion means one was assumed." % len(converted))


def test_diagnostics_are_reported_rather_than_silent(extracted):
    """Whatever the exporter could not handle must be named, with a severity."""
    for row in extracted.diagnostics:
        assert set(row) == {"source_path", "issue", "severity", "handling"}
        assert row["severity"] in ("blocking", "warning")


def test_unknown_test_ids_would_survive(extracted):
    """Currently none, and that is not asserted -- an unknown id is a supported state.

    What is asserted is that the column exists and is populated, so a future unknown id
    lands as a row with `config_status = "unknown_test_id"` rather than vanishing.
    """
    statuses = set(row["config_status"] for row in extracted.runs)
    assert statuses <= {"matched", "unknown_test_id"}
    assert "matched" in statuses


def test_no_exported_path_is_absolute(extracted):
    """The release condition: nothing carries the build machine's directory layout.

    This is the assertion that would have caught the bug, and it has to run here rather
    than over a fixture, because `relative_path` deliberately falls back to the absolute
    form for a path outside the repository -- which every tmp_path corpus is.
    """
    paths = ([r["source_path"] for r in extracted.runs]
             + [r["source_path"] for r in extracted.requests]
             + [p["source_path"] for records in extracted.payloads.values()
                for p in records]
             + [p["source_path"] for p in extracted.run_payloads]
             + [d["source_path"] for d in extracted.diagnostics])
    assert paths

    absolute = [p for p in paths
                if p.startswith("/") or p.startswith("\\")
                or (len(p) > 1 and p[1] == ":")]
    assert not absolute, (
        "%d of %d exported paths are absolute, so a published artifact would carry this "
        "machine's username and directory layout. Record paths through "
        "inventory.relative_path. First: %r" % (len(absolute), len(paths), absolute[0]))
