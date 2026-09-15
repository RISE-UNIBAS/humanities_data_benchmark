"""The re-scored field table: today's reading of stored responses, kept apart.

The corpus records `field_scores` for four benchmarks. The frontend's comparison step
re-runs each scorer over the stored responses to fill the gap, covering twelve, and the
dataset now carries that as its own table.

What these tests mostly defend is the separation. Re-scored observations are not what the
runs recorded -- they are produced by a scorer version that keeps changing, against ground
truths that have been revised, and some of them already disagree with the score their run
stored. They join to the same keys, so nothing stops an analyst combining them
deliberately; what must not happen is combining them by accident, which is why they are a
table and not more rows in `scores_long`.

Run with the rest of the logic-only suite: pytest -m "not integrity".
"""
import json

import pytest

from scripts.export_dataset import rescored
from scripts.export_dataset.schema import RESCORED_FIELDS, SCORES_LONG, TABLES


@pytest.fixture
def detail_tree(tmp_path):
    """A `compare_detail/<date>/<test_id>.json` tree from a compact spec."""
    root = tmp_path / "compare_detail"

    def _make(files):
        for (date, test_id), body in files.items():
            folder = root / date
            folder.mkdir(parents=True, exist_ok=True)
            path = folder / ("%s.json" % test_id)
            path.write_text(body if isinstance(body, str) else json.dumps(body),
                            encoding="utf-8")
        root.mkdir(parents=True, exist_ok=True)
        return root
    return _make


def _detail(**overrides):
    body = {
        "benchmark": "library_cards",
        "date": "2026-01-01",
        "test_id": "T0001",
        "source": "rescored",
        "rescored": "2026-09-14",
        "scorer_revision": "a" * 40,
        "ground_truth_revision": "b" * 40,
        "inputs": {
            "00414956": {
                "reproduces_stored_score": True,
                "field_scores": {
                    "author.last_name": {"ground_truth": "X", "response": "Y",
                                         "score": 0.34},
                    "": {"ground_truth": None, "response": None, "score": 1.0},
                },
            },
        },
    }
    body.update(overrides)
    return body


def test_every_field_becomes_a_row(detail_tree):
    rows, payloads, diagnostics = rescored.extract(
        detail_tree({("2026-01-01", "T0001"): _detail()}))
    assert len(rows) == 2 and len(payloads) == 1 and diagnostics == []
    assert sorted(r["field_path"] for r in rows) == ["", "author.last_name"]


def test_the_empty_field_path_is_data_here_too(detail_tree):
    rows, _payloads, _d = rescored.extract(
        detail_tree({("2026-01-01", "T0001"): _detail()}))
    empty = [r for r in rows if r["field_path"] == ""]
    assert len(empty) == 1 and empty[0]["score"] == 1.0


def test_provenance_is_on_every_row(detail_tree):
    """These numbers were produced by a specific scorer commit on a specific day, and
    both keep changing. A score without that is not interpretable later."""
    rows, _payloads, _d = rescored.extract(
        detail_tree({("2026-01-01", "T0001"): _detail()}))
    for row in rows:
        assert row["rescored_date"] == "2026-09-14"
        assert row["scorer_revision"] == "a" * 40
        assert row["ground_truth_revision"] == "b" * 40
        assert row["reproduces_stored_score"] is True


def test_a_disagreement_with_the_stored_score_is_recorded(detail_tree):
    body = _detail()
    body["inputs"]["00414956"]["reproduces_stored_score"] = False
    rows, _payloads, _d = rescored.extract(
        detail_tree({("2026-01-01", "T0001"): body}))
    assert all(r["reproduces_stored_score"] is False for r in rows)


def test_no_stored_score_to_compare_is_null_not_false(detail_tree):
    body = _detail()
    body["inputs"]["00414956"]["reproduces_stored_score"] = None
    rows, _payloads, _d = rescored.extract(
        detail_tree({("2026-01-01", "T0001"): body}))
    assert all(r["reproduces_stored_score"] is None for r in rows), (
        "false means re-scoring disagreed; null means there was nothing to disagree with")


def test_a_dirty_scorer_is_recorded(detail_tree):
    body = _detail(uncommitted_changes=["scorer"])
    rows, _payloads, _d = rescored.extract(
        detail_tree({("2026-01-01", "T0001"): body}))
    assert all(r["scorer_dirty"] is True for r in rows), (
        "the two revisions do not describe the code that ran if the tree was dirty")


def test_a_non_numeric_score_becomes_null(detail_tree):
    """The counting scorers assign no per-field similarity and write null."""
    body = _detail()
    body["inputs"]["00414956"]["field_scores"]["author.last_name"]["score"] = None
    body["inputs"]["00414956"]["field_scores"][""]["score"] = True
    rows, _payloads, _d = rescored.extract(
        detail_tree({("2026-01-01", "T0001"): body}))
    assert all(r["score"] is None for r in rows), "a boolean is not a similarity"


def test_an_unreadable_detail_file_is_a_diagnostic_not_a_crash(detail_tree):
    rows, _payloads, diagnostics = rescored.extract(
        detail_tree({("2026-01-01", "T0001"): "{truncated"}))
    assert rows == []
    assert [d["issue"] for d in diagnostics] == ["unreadable_compare_detail"]


def test_a_detail_file_without_identity_is_a_diagnostic(detail_tree):
    body = _detail()
    del body["test_id"]
    rows, _payloads, diagnostics = rescored.extract(
        detail_tree({("2026-01-01", "T0001"): body}))
    assert rows == []
    assert [d["issue"] for d in diagnostics] == ["compare_detail_without_identity"]


def test_a_benchmark_disagreement_is_reported_and_the_configuration_wins(detail_tree):
    rows, _payloads, diagnostics = rescored.extract(
        detail_tree({("2026-01-01", "T0001"): _detail()}),
        benchmark_of={"T0001": "company_lists"})
    assert [d["issue"] for d in diagnostics] == ["compare_detail_benchmark_mismatch"]
    assert all(r["benchmark"] == "company_lists" for r in rows)


def test_a_missing_detail_directory_yields_nothing(tmp_path):
    """The dataset must not require the frontend pipeline to have run."""
    rows, payloads, diagnostics = rescored.extract(tmp_path / "absent")
    assert (rows, payloads, diagnostics) == ([], [], [])


def test_the_table_is_separate_from_scores_long():
    """A separate table, so an aggregate over scores_long cannot pick these up."""
    assert "rescored_fields" in TABLES
    assert set(RESCORED_FIELDS.names) != set(SCORES_LONG.names)
    assert "metric_id" not in RESCORED_FIELDS.names, (
        "these are not dictionary-defined metrics; they are one scorer's per-field "
        "similarity as of a given commit")
    assert "reproduces_stored_score" in RESCORED_FIELDS.names


# --- staleness: has the detail fallen behind the corpus? ----------------------------

def _run(test_id, date, benchmark="library_cards"):
    return {"run_id": "%s@%s" % (test_id, date), "date": date, "benchmark": benchmark}


def _row(run_id, rescored_date="2026-09-14"):
    return {"run_id": run_id, "rescored_date": rescored_date}


def _issues(diagnostics):
    return dict((d["issue"], d) for d in diagnostics)


def test_a_run_newer_than_the_last_regeneration_blocks():
    """The drift this exists to catch: results landed, the detail was not regenerated,
    and every count in the README still adds up."""
    diagnostics = rescored.coverage_diagnostics(
        [_row("T0001@2026-01-01")],
        [_run("T0001", "2026-01-01"), _run("T0002", "2026-09-20")],
        stored_field_run_ids=set())
    stale = _issues(diagnostics)["rescored_detail_stale"]
    assert stale["severity"] == "blocking", "release preflight refuses on blocking"
    assert "2026-09-20" in stale["handling"] and "generate_compare_detail" in stale["handling"]


def test_a_run_the_generator_already_saw_is_only_a_warning():
    """A failed run has no answer to score, and some scorers report no per-field
    similarity. Uncovered and older than the regeneration is not staleness."""
    diagnostics = rescored.coverage_diagnostics(
        [_row("T0001@2026-01-01")],
        [_run("T0001", "2026-01-01"), _run("T0002", "2026-08-01", "book_advert_xml")],
        stored_field_run_ids=set())
    issues = _issues(diagnostics)
    assert "rescored_detail_stale" not in issues
    assert issues["rescored_detail_incomplete"]["severity"] == "warning"
    assert "book_advert_xml 1" in issues["rescored_detail_incomplete"]["handling"]


def test_detail_recorded_at_run_time_counts_as_coverage():
    """The two sources are complementary, so a run covered by either is covered."""
    assert rescored.coverage_diagnostics(
        [_row("T0001@2026-01-01")],
        [_run("T0001", "2026-01-01"), _run("T0002", "2026-09-20")],
        stored_field_run_ids={"T0002@2026-09-20"}) == []


def test_an_absent_detail_tree_is_reported_without_blocking():
    """A build without the frontend pipeline is legitimate; a silent one is not."""
    diagnostics = rescored.coverage_diagnostics(
        [], [_run("T0001", "2026-01-01")], stored_field_run_ids=set())
    assert [d["issue"] for d in diagnostics] == ["rescored_detail_absent"]
    assert diagnostics[0]["severity"] == "warning"


def test_undated_detail_cannot_be_judged_and_says_so():
    diagnostics = rescored.coverage_diagnostics(
        [_row("T0001@2026-01-01", rescored_date=None)],
        [_run("T0001", "2026-01-01"), _run("T0002", "2026-09-20")],
        stored_field_run_ids=set())
    issues = _issues(diagnostics)
    assert "rescored_detail_undated" in issues
    assert "rescored_detail_stale" not in issues, (
        "without a generation date there is nothing to compare the run date against")
