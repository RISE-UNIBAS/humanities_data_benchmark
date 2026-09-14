"""The read-only results layer, over fixture trees rather than the real corpus.

`scripts/results_index.py` exists so that the frontend export and the dataset export can
stop keeping seven private walks of `results/`. The two disagree about what to keep -- the
frontend may skip a run it cannot chart, the dataset export must emit a row for it and say
why -- so the layer's contract is that it drops nothing and every filter is named and
applied by the caller. These tests pin that contract, plus the parsing rules that were
learned from the corpus the hard way.

Run with the rest of the logic-only suite: pytest -m "not integrity".

Rules enforced here:
  1. `iter_run_dirs` yields every run directory, including ones with no scoring, no
     requests, an unknown test id, or nothing at all.
  2. Both levels of the walk are sorted, and `newest_first` reverses both.
  3. An object id is taken from the directory's test id, then from a prefix observed in
     the directory, and never from a greedy split on underscores.
  4. A request file whose object id will not resolve is still yielded.
  5. `read_json` never raises, and tells "missing" apart from a file holding `null`.
  6. `TestCatalog`'s views keep the quirks their callers already depend on.
"""
import json

from scripts.results_index import (JsonRead, RunDir, TestCatalog, first_provider_model,
                                   first_request, iter_request_records, iter_run_dirs,
                                   known_tests, object_id_of, observed_prefix, read_json,
                                   read_run)


def test_iter_run_dirs_yields_every_run_dir_date_major_and_sorted(make_corpus):
    root = make_corpus({
        "2026-01-02": {"T0009": {}, "T0002": {}},
        "2026-01-01": {"T0010": {}, "T0001": {}},
    })
    assert [(r.date, r.test_id) for r in iter_run_dirs(root)] == [
        ("2026-01-01", "T0001"), ("2026-01-01", "T0010"),
        ("2026-01-02", "T0002"), ("2026-01-02", "T0009")]


def test_iter_run_dirs_keeps_runs_with_nothing_worth_charting(make_corpus):
    """The hard constraint: the export must be able to emit a row for each of these.

    A frontend generator is entitled to skip an unknown id or an empty run. If the shared
    walk skipped them too, the dataset export could not tell the difference between a run
    that failed and a run that never happened.
    """
    root = make_corpus({"2026-01-01": {
        "T0001": {"requests": {"a": {"provider": "openai"}}},   # ordinary
        "T0002": {"requests": {"a": {}}},                        # no scoring.json
        "T0003": {"scoring": {"fuzzy": 1.0}},                    # no request files
        "T9999": {"requests": {"a": {}}},                        # id not in any CSV
        "T0004": {},                                             # nothing at all
    }})
    found = sorted(r.test_id for r in iter_run_dirs(root))
    assert found == ["T0001", "T0002", "T0003", "T0004", "T9999"], (
        "iter_run_dirs dropped %s. It is the complete walk; filtering is the caller's."
        % (set(["T0001", "T0002", "T0003", "T0004", "T9999"]) - set(found)))


def test_iter_run_dirs_newest_first_reverses_both_levels(make_corpus):
    root = make_corpus({
        "2026-01-01": {"T0001": {}, "T0002": {}},
        "2026-01-02": {"T0003": {}, "T0004": {}},
    })
    assert [(r.date, r.test_id) for r in iter_run_dirs(root, newest_first=True)] == [
        ("2026-01-02", "T0004"), ("2026-01-02", "T0003"),
        ("2026-01-01", "T0002"), ("2026-01-01", "T0001")]


def test_iter_run_dirs_ignores_stray_files_and_a_missing_root(make_corpus, tmp_path):
    root = make_corpus({"2026-01-01": {"T0001": {}}})
    (root / "README.txt").write_text("not a date", encoding="utf-8")
    (root / "2026-01-01" / "notes.txt").write_text("not a run", encoding="utf-8")

    assert [r.test_id for r in iter_run_dirs(root)] == ["T0001"]
    assert list(iter_run_dirs(tmp_path / "absent")) == []


def test_run_id_is_test_id_at_date(make_corpus):
    root = make_corpus({"2026-01-01": {"T0001": {}}})
    assert next(iter_run_dirs(root)).run_id == "T0001@2026-01-01"


def test_object_id_uses_the_directory_id_then_the_observed_prefix(make_corpus):
    """4,296 files in 188 early run directories name a prefix the directory does not.

    The ids were re-padded (T01 -> T0001) without renaming the files, and two padding
    widths are in use, so the width cannot be derived -- only observed.
    """
    root = make_corpus({"2025-03-01": {"T0001": {"requests": {
        "request_T01_jaccuse.json": {},
        "request_T01_luther.json": {},
    }}}})
    files = read_run(next(iter_run_dirs(root)))
    assert files.prefix == "T01"
    assert sorted(f.object_id for f in files.requests) == ["jaccuse", "luther"]


def test_object_id_is_not_split_greedily_on_underscores():
    assert object_id_of("request_T0001_Se_18_Bilanz1967_page_4.json", "T0001") == \
        "Se_18_Bilanz1967_page_4"
    assert object_id_of("request_T0931_page_10.json", "T0931") == "page_10"
    assert object_id_of("request_T0570_00414956.json", "T0570") == "00414956", \
        "leading zeros are part of the id, not a number to be normalised"


def test_object_id_is_none_rather_than_a_guess():
    assert object_id_of("request_T0002_x.json", "T0001") is None
    assert object_id_of("request_T0001_.json", "T0001") is None
    assert object_id_of("scoring.json", "T0001") is None
    assert observed_prefix(["scoring.json"]) is None


def test_unresolvable_filename_is_still_yielded(make_corpus):
    """Losing the file would lose the observation; the null object id is the diagnostic."""
    root = make_corpus({"2026-01-01": {"T0001": {"requests": {
        "request_T0001_good.json": {},
        "request_T0002_stray.json": {},
    }}}})
    files = read_run(next(iter_run_dirs(root)))
    assert len(files.requests) == 2
    assert sorted((f.name, f.object_id) for f in files.requests) == [
        ("request_T0001_good.json", "good"), ("request_T0002_stray.json", None)]


def test_read_json_reports_status_instead_of_raising(make_corpus, tmp_path):
    good = tmp_path / "good.json"
    good.write_text('{"a": 1}', encoding="utf-8")
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")

    assert read_json(good) == JsonRead({"a": 1}, "ok", None)
    assert read_json(tmp_path / "absent.json").status == "missing"

    invalid = read_json(bad)
    assert invalid.status == "invalid" and invalid.value is None and invalid.error

    unreadable = read_json(tmp_path)
    assert unreadable.status == "unreadable", (
        "a directory is not a missing file; the export has to tell them apart")


def test_read_json_tells_a_stored_null_apart_from_a_missing_file(tmp_path):
    """"Null means unavailable, never an inferred zero" needs both facts to be visible."""
    for text, value in (("null", None), ("0", 0), ("[]", []), ("{}", {})):
        path = tmp_path / ("v%s.json" % abs(hash(text)))
        path.write_text(text, encoding="utf-8")
        read = read_json(path)
        assert read.status == "ok" and read.value == value
    assert read_json(tmp_path / "gone.json") == JsonRead(None, "missing", None)


def test_iter_request_records_yields_malformed_files_too(make_corpus):
    root = make_corpus({"2026-01-01": {"T0001": {"requests": {
        "a": {"provider": "openai", "model": "gpt-4o"},
        "b": "{truncated",
    }}}})
    records = dict((f.object_id, read.status) for f, read in
                   iter_request_records(next(iter_run_dirs(root))))
    assert records == {"a": "ok", "b": "invalid"}


def test_first_request_returns_the_first_file_even_when_it_will_not_parse(make_corpus):
    root = make_corpus({"2026-01-01": {"T0001": {"requests": {
        "a_first": "{truncated", "b_second": {"provider": "openai"},
    }}}})
    request, read = first_request(next(iter_run_dirs(root)))
    assert request.object_id == "a_first" and read.status == "invalid"


def test_first_request_is_none_when_the_run_stored_nothing(make_corpus):
    root = make_corpus({"2026-01-01": {"T0001": {}}})
    assert first_request(next(iter_run_dirs(root))) is None


def test_first_provider_model_needs_both_fields(make_corpus):
    """A record naming only one is not an identification, and the frontend skips it."""
    root = make_corpus({"2026-01-01": {"T0001": {"requests": {
        "a": {"provider": "openai"},
        "b": "{truncated",
        "c": {"provider": "genai", "model": "gemini-3.8-flash"},
    }}}})
    assert first_provider_model(next(iter_run_dirs(root))) == ("genai", "gemini-3.8-flash")


def test_first_provider_model_is_a_pair_of_nones_when_nothing_says(make_corpus):
    root = make_corpus({"2026-01-01": {"T0001": {"requests": {"a": {}}}}})
    assert first_provider_model(next(iter_run_dirs(root))) == (None, None)


def test_known_tests_drops_unknown_ids_and_nothing_else(make_corpus, write_tests_csv):
    root = make_corpus({"2026-01-01": {"T0001": {}, "T0002": {}, "T9999": {}}})
    catalog = TestCatalog.load(write_tests_csv([
        {"id": "T0001", "name": "business_letters"},
        {"id": "T0002", "name": "company_lists"},
    ]))
    assert [(r.test_id, b) for r, b in known_tests(iter_run_dirs(root), catalog)] == [
        ("T0001", "business_letters"), ("T0002", "company_lists")]


def test_known_tests_filters_by_benchmark(make_corpus, write_tests_csv):
    root = make_corpus({"2026-01-01": {"T0001": {}, "T0002": {}}})
    catalog = TestCatalog.load(write_tests_csv([
        {"id": "T0001", "name": "business_letters"},
        {"id": "T0002", "name": "company_lists"},
    ]))
    kept = list(known_tests(iter_run_dirs(root), catalog, "company_lists"))
    assert [r.test_id for r, _ in kept] == ["T0002"]


def test_known_tests_drops_a_row_whose_benchmark_is_blank(write_tests_csv):
    """A row with no name cannot say which benchmark scored the run, so it is not known."""
    catalog = TestCatalog.load(write_tests_csv([{"id": "T0001", "name": ""}]))
    run = RunDir(None, "2026-01-01", "T0001", "T0001@2026-01-01")
    assert list(known_tests([run], catalog)) == []


def test_typed_rows_keeps_the_quirks_its_callers_read(write_tests_csv):
    """The empty-string branch runs first, so blank is None rather than 0.0 or False.

    `get_all_tests` has always behaved this way and the frontend reads the difference
    between "not configured" and "configured false", so the refactor must not tidy it up.
    """
    catalog = TestCatalog.load(write_tests_csv([
        {"id": "T0001", "name": "b", "temperature": "", "legacy_test": ""},
        {"id": "T0002", "name": "b", "temperature": "0", "legacy_test": "TRUE"},
        {"id": "T0003", "name": "b", "temperature": "0.7", "legacy_test": "false"},
    ]))
    rows = dict((r["id"], r) for r in catalog.typed_rows())
    assert rows["T0001"]["temperature"] is None and rows["T0001"]["legacy_test"] is None
    assert rows["T0002"]["temperature"] == 0.0, (
        'a configured zero is a value, not an absence: "0" is a non-empty string, so it '
        'passes the truthiness guard and becomes 0.0, while "" becomes None')
    assert rows["T0002"]["legacy_test"] is True
    assert rows["T0003"]["temperature"] == 0.7 and rows["T0003"]["legacy_test"] is False


def test_raw_by_id_strips_ids_drops_blanks_and_lets_the_last_row_win(write_tests_csv):
    catalog = TestCatalog.load(write_tests_csv([
        {"id": " T0001 ", "name": "first"},
        {"id": "", "name": "blank"},
        {"id": "T0002", "name": "one"},
        {"id": "T0002", "name": "two"},
    ]))
    assert sorted(catalog.raw_by_id()) == ["T0001", "T0002"]
    assert catalog.raw_by_id()["T0002"]["name"] == "two"
    assert "T0001" in catalog and "T9999" not in catalog


def test_rules_are_parsed_and_unusable_rules_are_none(write_tests_csv):
    catalog = TestCatalog.load(write_tests_csv([
        {"id": "T0001", "name": "b", "rules": '{"score_interpretation": true}'},
        {"id": "T0002", "name": "b", "rules": ""},
        {"id": "T0003", "name": "b", "rules": "{not json"},
    ]))
    assert catalog.rules_of("T0001") == {"score_interpretation": True}
    assert catalog.rules_of("T0002") is None
    assert catalog.rules_of("T0003") is None
    assert catalog.rules_of("T9999") is None


def test_a_missing_tests_csv_is_empty_not_an_error(tmp_path):
    catalog = TestCatalog.load(tmp_path / "absent.csv")
    assert catalog.rows == () and catalog.raw_by_id() == {} and catalog.typed_rows() == []


def test_read_run_accepts_a_bare_path(make_corpus):
    """Callers hold a Path today; `iter_run_inputs(run_dir)` passes one straight through."""
    root = make_corpus({"2026-01-01": {"T0001": {"requests": {"a": {}}}}})
    files = read_run(root / "2026-01-01" / "T0001")
    assert files.run.run_id == "T0001@2026-01-01"
    assert [f.object_id for f in files.requests] == ["a"]


def test_scoring_path_is_reported_even_when_absent(make_corpus):
    root = make_corpus({"2026-01-01": {"T0001": {"requests": {"a": {}}}}})
    files = read_run(next(iter_run_dirs(root)))
    assert files.scoring_path.name == "scoring.json" and not files.scoring_path.exists()


def test_payload_is_returned_unchanged(make_corpus):
    """The export copies this verbatim into its payload sidecar, so nothing may coerce it."""
    record = {"parsed": {"a": None, "b": [], "c": 0.1}, "text": "é", "usage": {}}
    root = make_corpus({"2026-01-01": {"T0001": {"requests": {"a": record}}}})
    _file, read = first_request(next(iter_run_dirs(root)))
    assert read.value == record
    assert json.dumps(read.value, sort_keys=True) == json.dumps(record, sort_keys=True)
