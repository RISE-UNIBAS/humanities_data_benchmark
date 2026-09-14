"""Regression tests for the findings in dev/DATASET_EXPORT_BRANCH_AUDIT.md.

Kept together and named by finding, so a reviewer can go from the audit to the test that
closes it. They are not organised by module: what they have in common is how they were
missed, not where they live.

That common cause is worth stating. Every existing test asserted what a row *contained*.
None asserted what it should refuse to contain, and none checked a documentation claim
against the artifact. F01 is the sharpest case -- a request with one recorded token count
and one missing produced a complete, confident cost, and 345 passing tests said nothing
about it. Most of what follows is an assertion about absence.

Run with the rest of the logic-only suite: pytest -m "not integrity".
"""
import json

import pytest

from scripts.export_dataset import metrics as M
from scripts.export_dataset import paths as P
from scripts.export_dataset.extract import Extractor, parse_timestamp
from scripts.results_index import TestCatalog, read_json


@pytest.fixture
def extract_audit(make_corpus, write_tests_csv, make_benchmarks):
    def _extract(spec, tests=None, metas=None):
        root = make_corpus(spec)
        make_benchmarks(metas if metas is not None else {"company_lists": {}})
        catalog = TestCatalog.load(write_tests_csv(
            tests if tests is not None
            else [{"id": "T0001", "name": "company_lists", "provider": "openai",
                   "model": "gpt-4o", "legacy_test": "false"}]))
        return Extractor(results_path=root, catalog=catalog).run()
    return _extract


@pytest.fixture(autouse=True)
def prices(make_pricing):
    make_pricing({"2026-01-01": {"openai": {"gpt-4o": {"input_price": 2.0,
                                                       "output_price": 5.0}}}})


def _derive(input_tokens, output_tokens):
    tokens = dict(input_tokens=input_tokens, output_tokens=output_tokens,
                  total_tokens=None, cached_tokens=None,
                  cache_creation_tokens=None, cache_read_tokens=None)
    return Extractor._derive_cost("2026-01-01", "openai", "gpt-4o", {}, tokens)


# --- F01: a missing token count is not a zero cost -------------------------------

def test_f01_both_counts_present_gives_a_complete_cost():
    row = _derive(1_000_000, 1_000_000)
    assert (row["derived_input_cost_usd"], row["derived_output_cost_usd"]) == (2.0, 5.0)
    assert row["derived_total_cost_usd"] == 7.0
    assert row["cost_provenance"] == "derived"


def test_f01_input_only_keeps_the_known_half_and_no_total():
    """The real row: input_tokens 523, output_tokens null, total_tokens 66,058.

    `or 0` made the output cost a measured-looking zero and the total non-null and
    `derived`. The recorded total-token count proves the output was the larger half.
    """
    row = _derive(1_000_000, None)
    assert row["derived_input_cost_usd"] == 2.0
    assert row["derived_output_cost_usd"] is None
    assert row["derived_total_cost_usd"] is None
    assert row["cost_provenance"] == "partial_tokens"


def test_f01_output_only_is_symmetric():
    row = _derive(None, 1_000_000)
    assert row["derived_input_cost_usd"] is None
    assert row["derived_output_cost_usd"] == 5.0
    assert row["derived_total_cost_usd"] is None
    assert row["cost_provenance"] == "partial_tokens"


def test_f01_explicit_zeros_are_measurements_not_absences():
    row = _derive(0, 0)
    assert row["derived_total_cost_usd"] == 0.0
    assert row["cost_provenance"] == "derived", (
        "a recorded zero is a measurement; only an absent count is partial")


def test_f01_no_tokens_still_reports_the_price_in_force():
    """Four runs record no tokens at all. What the model cost that day is still a fact."""
    row = _derive(None, None)
    assert row["cost_provenance"] == "no_tokens"
    assert row["derived_total_cost_usd"] is None
    assert row["pricing_input_price_per_million"] == 2.0
    assert row["pricing_output_price_per_million"] == 5.0


def test_f01_a_partial_request_does_not_count_as_costed(extract_audit):
    e = extract_audit({"2026-01-01": {"T0001": {"requests": {
        "whole": {"provider": "openai", "model": "gpt-4o",
                  "usage": {"input_tokens": 10, "output_tokens": 10}},
        "partial": {"provider": "openai", "model": "gpt-4o",
                    "usage": {"input_tokens": 10}},
    }}}})
    run = e.runs[0]
    assert run["n_requests"] == 2
    assert run["n_requests_with_derived_cost"] == 1, (
        "run coverage must not count a request whose total could not be derived")


# --- F02: the build cannot delete its own input ----------------------------------

@pytest.mark.parametrize("kwargs", [
    {"source": "dataset", "out": "dataset"},
    {"source": "x/release", "out": "x"},
    {"source": "x", "out": "x/nested"},
])
def test_f02_overlapping_paths_are_refused(kwargs):
    with pytest.raises(P.UnsafePaths):
        P.check(**kwargs)


@pytest.mark.parametrize("destination", ["results", "results/sub", "benchmarks",
                                         "scripts/data"])
def test_f02_generated_output_may_not_land_on_the_corpus(destination):
    with pytest.raises(P.UnsafePaths, match="the build reads"):
        P.check(source="dataset", out=destination)


def test_f02_a_normal_destination_is_allowed():
    assert P.check(source="results", out="dataset", staging="dataset.staging")


def test_f02_refusal_happens_before_anything_is_deleted(tmp_path):
    """A sentinel proves the input survived, which is the whole point of checking early."""
    from scripts import package_dataset as PD
    source = tmp_path / "release"
    source.mkdir()
    (source / "manifest.json").write_text("{}", encoding="utf-8")
    (source / "sentinel").write_text("intact", encoding="utf-8")

    with pytest.raises(P.UnsafePaths):
        PD.build_release_tree(source, tmp_path / "release")
    assert (source / "sentinel").read_text(encoding="utf-8") == "intact"


# --- F03: inputs are verified before they are packaged ---------------------------

def _mini_dataset(tmp_path, output_sha256=None, extra=None):
    from scripts import package_dataset as PD
    d = tmp_path / "dataset"
    (d / "payloads").mkdir(parents=True)
    (d / "runs.parquet").write_bytes(b"PAR1")
    (d / "coverage.csv").write_text("a\n1\n", encoding="utf-8")
    if extra:
        (d / extra).write_text("unexpected", encoding="utf-8")
    declared = output_sha256 if output_sha256 is not None else {
        "runs.parquet": PD.sha256_of(d / "runs.parquet"),
        "coverage.csv": PD.sha256_of(d / "coverage.csv"),
    }
    (d / "manifest.json").write_text(json.dumps({
        "dataset_version": "2026-09-09.2", "schema_version": "1.1.0",
        "data_cutoff": "2026-09-09", "partial": False,
        "source_worktree_dirty": False, "source_commit": "abc123456",
        "row_counts": {"runs": 1, "requests": 1, "scores_long": 1, "metrics": 1},
        "inventory": {"files_hashed": 2},
        "output_sha256": declared,
    }), encoding="utf-8")
    return d


def test_f03_a_changed_input_is_refused(tmp_path):
    from scripts import package_dataset as PD
    d = _mini_dataset(tmp_path, output_sha256={"runs.parquet": "wrong-hash"})
    manifest = json.loads((d / "manifest.json").read_text())
    assert any("changed since the build" in p for p in PD.verify_inputs(d, manifest))


def test_f03_a_missing_declared_input_is_refused(tmp_path):
    from scripts import package_dataset as PD
    d = _mini_dataset(tmp_path)
    (d / "runs.parquet").unlink()
    manifest = json.loads((d / "manifest.json").read_text())
    assert any("declared but missing" in p for p in PD.verify_inputs(d, manifest))


def test_f03_an_unmanifested_extra_file_is_refused(tmp_path):
    from scripts import package_dataset as PD
    d = _mini_dataset(tmp_path, extra="stowaway.txt")
    manifest = json.loads((d / "manifest.json").read_text())
    assert any("not in the build manifest" in p for p in PD.verify_inputs(d, manifest))


def test_f03_a_matching_build_verifies(tmp_path):
    from scripts import package_dataset as PD
    d = _mini_dataset(tmp_path)
    manifest = json.loads((d / "manifest.json").read_text())
    assert PD.verify_inputs(d, manifest) == []


def test_f03_packaging_refuses_and_leaves_the_previous_distribution(tmp_path):
    from scripts import package_dataset as PD
    d = _mini_dataset(tmp_path, output_sha256={"runs.parquet": "wrong-hash"})
    dist = tmp_path / "dist"
    (dist / "release").mkdir(parents=True)
    (dist / "release" / "sentinel").write_text("previous", encoding="utf-8")

    with pytest.raises(SystemExit, match="does not match its own manifest"):
        PD.main(["--dataset", str(d), "--out", str(dist), "--skip-payloads"])
    assert (dist / "release" / "sentinel").read_text(encoding="utf-8") == "previous"


# --- F04: a release blocker blocks -----------------------------------------------

def test_f04_a_partial_build_is_not_releasable(tmp_path):
    from scripts import package_dataset as PD
    d = _mini_dataset(tmp_path)
    manifest = json.loads((d / "manifest.json").read_text())
    manifest["partial"] = True
    assert any("partial" in b for b in PD.release_preflight(d, manifest))


def test_f04_a_blocking_diagnostic_is_not_releasable(tmp_path):
    from scripts import package_dataset as PD
    d = _mini_dataset(tmp_path)
    (d / "diagnostics.jsonl").write_text(
        json.dumps({"source_path": "x", "issue": "unresolvable_object_id",
                    "severity": "blocking", "handling": "kept"}) + "\n",
        encoding="utf-8")
    manifest = json.loads((d / "manifest.json").read_text())
    assert any("blocking diagnostic" in b for b in PD.release_preflight(d, manifest))


def test_f04_unknown_git_provenance_is_not_releasable(tmp_path):
    from scripts import package_dataset as PD
    d = _mini_dataset(tmp_path)
    manifest = json.loads((d / "manifest.json").read_text())
    manifest["source_worktree_dirty"] = None
    assert any("provenance is unknown" in b for b in PD.release_preflight(d, manifest))


def test_f04_a_clean_build_is_releasable(tmp_path):
    from scripts import package_dataset as PD
    d = _mini_dataset(tmp_path)
    manifest = json.loads((d / "manifest.json").read_text())
    assert PD.release_preflight(d, manifest) == []


def test_f04_the_cli_exits_nonzero_and_gives_no_deposit_instruction(tmp_path, capsys):
    from scripts import package_dataset as PD
    d = _mini_dataset(tmp_path)
    manifest = json.loads((d / "manifest.json").read_text())
    manifest["partial"] = True
    (d / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(SystemExit) as exit_info:
        PD.main(["--dataset", str(d), "--out", str(tmp_path / "dist"), "--skip-payloads"])
    assert exit_info.value.code != 0
    assert "deposit" not in capsys.readouterr().out


# --- F05: the package describes what it ships ------------------------------------

def test_f05_every_declared_resource_exists_in_the_package(tmp_path):
    from scripts import package_dataset as PD
    d = _mini_dataset(tmp_path)
    release = tmp_path / "dist" / "release"
    PD.build_release_tree(d, release)
    assert PD.check_declared_paths(release) == []


def test_f05_the_release_readme_does_not_promise_absent_files(tmp_path):
    from scripts import package_dataset as PD
    d = _mini_dataset(tmp_path)
    release = tmp_path / "dist" / "release"
    PD.build_release_tree(d, release, payload_archive="payloads-2026-09-09.2.tar.gz")
    text = (release / "README.md").read_text(encoding="utf-8")
    assert "Loading the CSV" not in text
    assert "payloads-2026-09-09.2.tar.gz" in text


def test_f05_table_csvs_do_not_ship(tmp_path):
    from scripts import package_dataset as PD
    d = _mini_dataset(tmp_path)
    (d / "requests.csv").write_text("a\n1\n", encoding="utf-8")
    release = tmp_path / "dist" / "release"
    PD.build_release_tree(d, release)
    assert not (release / "requests.csv").exists()
    assert not (release / "requests.csv.gz").exists()
    assert (release / "coverage.csv.gz").is_file(), "coverage has no Parquet form"


# --- F06: unresolved visibility stays unknown ------------------------------------

@pytest.mark.parametrize("legacy,display,expected", [
    ("false", True, False),
    ("true", True, True),
    ("false", False, True),
    ("true", False, True),
    ("false", None, None),
    ("", True, None),
    ("", None, None),
    ("true", None, True),
    ("", False, True),
])
def test_f06_hidden_is_nullable_or(extract_audit, legacy, display, expected):
    """`(legacy=false, display=unknown)` used to give hidden=false, admitting a run whose
    benchmark metadata could not be read into the default analytical view."""
    metas = {"company_lists": "{not json" if display is None
             else ({} if display is True else {"display": False})}
    e = extract_audit({"2026-01-01": {"T0001": {"requests": {"a": {}}}}},
                      tests=[{"id": "T0001", "name": "company_lists",
                              "legacy_test": legacy}],
                      metas=metas)
    assert e.runs[0]["hidden"] is expected


# --- F08: nothing decoded is discarded -------------------------------------------

def test_f08_invalid_utf8_is_an_invalid_file_not_a_crash(tmp_path):
    path = tmp_path / "bad.json"
    path.write_bytes(b'{"a": "\xff"}')
    read = read_json(path)
    assert read.status == "invalid" and read.value is None and read.error


@pytest.mark.parametrize("payload", ["[1, 2]", "42", "null", '"text"'])
def test_f08_a_non_object_record_is_preserved_and_diagnosed(extract_audit, payload):
    e = extract_audit({"2026-01-01": {"T0001": {"requests": {"a": payload}}}})
    assert len(e.requests) == 1
    assert e.requests[0]["parse_status"] == "ok"

    preserved = [r for records in e.payloads.values() for r in records]
    assert len(preserved) == 1, "a decoded value reaches the sidecar whatever its shape"
    assert preserved[0]["source_record"] == json.loads(payload)
    assert "unsupported_record_shape" in [d["issue"] for d in e.diagnostics]


# --- F10: real UTC ----------------------------------------------------------------

@pytest.mark.parametrize("raw,expected", [
    ("2026-01-24T23:53:45+02:00", "2026-01-24T21:53:45+00:00"),
    ("2026-01-24T23:53:45-05:00", "2026-01-25T04:53:45+00:00"),
    ("2026-01-01T00:30:00+05:00", "2025-12-31T19:30:00+00:00"),
    ("2026-01-24T23:53:45+00:00", "2026-01-24T23:53:45+00:00"),
])
def test_f10_aware_timestamps_convert_to_utc(raw, expected):
    assert parse_timestamp(raw)[0] == expected


def test_f10_naive_timestamps_stay_null():
    assert parse_timestamp("2026-01-24T23:53:45.614205") == (None, None)


# --- F12: unknown provenance stays unknown ----------------------------------------

def test_f12_a_failed_git_command_reports_failure():
    from scripts.export_dataset.__main__ import _git
    output, error = _git("not-a-git-command")
    assert output is None and error


def test_f12_a_successful_git_command_reports_output():
    from scripts.export_dataset.__main__ import _git
    output, error = _git("rev-parse", "HEAD")
    assert error is None and output and len(output) == 40


# --- follow-up 1: n_scored means something ----------------------------------------

def test_followup1_scaffold_placeholders_are_not_scores():
    assert not M.is_scored("test_benchmark2",
                           {"score": 66, "scoresdfsdf_2": 77, "score_3": 88})


def test_followup1_business_letters_needs_all_three_categories():
    assert not M.is_scored("business_letters", {"send_date_tp": 1})
    assert not M.is_scored("business_letters",
                           {"send_date_tp": 1, "sender_persons_tp": 0})
    assert M.is_scored("business_letters", {"send_date_tp": 1, "sender_persons_tp": 0,
                                            "receiver_persons_tp": 2})


def test_followup1_a_parameter_alone_is_not_a_score():
    assert not M.is_scored("magazine_pages", {"iou_threshold": 0.5})
    assert M.is_scored("magazine_pages", {"iou_threshold": 0.5, "f1": 0.7})


def test_followup1_n_scored_counts_the_predicate(extract_audit):
    e = extract_audit({"2026-01-01": {"T0001": {"requests": {
        "scored": {"score": {"f1_score": 0.5}},
        "not_scored": {"score": {"total_fields": 3}},
    }}}})
    assert e.runs[0]["n_scored"] == 1
