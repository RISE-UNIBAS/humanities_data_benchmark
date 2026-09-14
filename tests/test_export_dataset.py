"""The dataset exporter, over fixture corpora rather than the real result tree.

The product these tests defend is an archive: something an analyst loads years from now
without the repository beside them. That puts the emphasis somewhere unusual. Most of what
follows is not about getting numbers right -- it is about a missing number staying missing.
A token count that was never recorded must not arrive as `0`, a run with no `scoring.json`
must still be a row, and a request file that will not parse must keep its key and say so.
A table built by skipping cannot express "this is not known", and the difference between
"not known" and "zero" is the difference between an honest dataset and a misleading one.

The shapes exercised here were all observed in the corpus: an empty `usage` block, a
`field_scores` key that is the empty string, a request filename whose prefix is not its
directory's test id, an object id with leading zeros, a scorer that reports counts and no
similarity. None of them is hypothetical.

Run with the rest of the logic-only suite: pytest -m "not integrity".
"""
import gzip
import json

import pytest

from scripts.export_dataset import metrics as M
from scripts.export_dataset import writers
from scripts.export_dataset.extract import Extractor, parse_timestamp
from scripts.export_dataset.schema import REQUESTS, RUNS, SCORES_LONG, SORT_KEYS, UNIQUE_KEYS
from scripts.results_index import TestCatalog


@pytest.fixture
def extract(make_corpus, write_tests_csv, make_benchmarks):
    """Run the extractor over a fixture corpus and hand back the finished rows."""
    def _extract(spec, tests=None, metas=None, run=True):
        root = make_corpus(spec)
        make_benchmarks(metas if metas is not None else {"company_lists": {}})
        catalog = TestCatalog.load(write_tests_csv(
            tests if tests is not None
            else [{"id": "T0001", "name": "company_lists", "provider": "openai",
                   "model": "gpt-4o", "legacy_test": "false"}]))
        extractor = Extractor(results_path=root, catalog=catalog)
        if run:
            extractor.run()
        return extractor
    return _extract


def _by_object(extractor):
    return dict((r["object_id"], r) for r in extractor.requests)


# --------------------------------------------------------------------------------
# Nothing is dropped
# --------------------------------------------------------------------------------

def test_every_run_directory_becomes_exactly_one_row(extract):
    """Including the ones a charting pipeline would rightly skip."""
    e = extract({"2026-01-01": {
        "T0001": {"requests": {"a": {"provider": "openai"}}, "scoring": {"f1_micro": 0.5}},
        "T0002": {"requests": {"a": {}}},                  # no scoring.json
        "T0003": {"scoring": {"f1_micro": 0.5}},           # no request files
        "T0004": {},                                        # nothing at all
        "T9999": {"requests": {"a": {}}},                   # id absent from the CSV
    }})
    assert sorted(r["test_id"] for r in e.runs) == \
        ["T0001", "T0002", "T0003", "T0004", "T9999"]
    assert len(e.runs) == 5


def test_an_unknown_test_id_keeps_its_identity(extract):
    """It is never mapped onto a base test: the exact spelling is the evidence."""
    e = extract({"2026-01-01": {"T0892_v2": {"requests": {"a": {}}}}})
    row = e.runs[0]
    assert row["test_id"] == "T0892_v2"
    assert row["config_status"] == "unknown_test_id"
    assert row["benchmark"] is None and row["configured_model"] is None


def test_a_malformed_request_keeps_its_row_and_raises_a_diagnostic(extract):
    e = extract({"2026-01-01": {"T0001": {"requests": {
        "good": {"provider": "openai", "model": "gpt-4o"},
        "broken": "{truncated",
    }}}})
    rows = _by_object(e)
    assert set(rows) == {"good", "broken"}
    assert rows["broken"]["parse_status"] == "invalid"
    assert rows["broken"]["response_provider"] is None
    assert rows["broken"]["source_path"].endswith("request_T0001_broken.json")
    assert [d["issue"] for d in e.diagnostics] == ["unparseable_request_json"]
    assert any(p.name.endswith("broken.json") for p in e.invalid_sources)


def test_a_malformed_scoring_file_keeps_its_run(extract):
    e = extract({"2026-01-01": {"T0001": {"requests": {"a": {}}, "scoring": "{oops"}}})
    assert e.runs[0]["scoring_status"] == "invalid"
    assert e.runs[0]["has_scoring"] is True
    assert [d["issue"] for d in e.diagnostics] == ["unparseable_scoring_json"]


def test_an_unresolvable_filename_is_a_blocking_diagnostic_not_a_deletion(extract):
    # A lone odd file would supply its own fallback prefix and resolve. It takes a
    # second, differently-prefixed file to leave one genuinely unresolvable.
    e = extract({"2026-01-01": {"T0001": {"requests": {
        "request_T0001_good.json": {"provider": "openai"},
        "request_T9999_stray.json": {"provider": "openai"},
    }}}})
    assert len(e.requests) == 2, "the file is kept even though its id will not resolve"
    assert sorted(r["object_id"] or "<null>" for r in e.requests) == ["<null>", "good"]
    issue = [d for d in e.diagnostics if d["issue"] == "unresolvable_object_id"]
    assert issue and issue[0]["severity"] == "blocking"


# --------------------------------------------------------------------------------
# Keys
# --------------------------------------------------------------------------------

def test_run_id_is_test_id_at_date(extract):
    e = extract({"2026-01-01": {"T0001": {"requests": {"a": {}}}}})
    assert e.runs[0]["run_id"] == "T0001@2026-01-01"
    assert e.requests[0]["run_id"] == "T0001@2026-01-01"


def test_object_ids_keep_their_leading_zeros_and_their_accents(extract):
    e = extract({"2026-01-01": {"T0001": {"requests": {
        "00414956": {}, "Se_18_Assemblées_3_Bilanz1968_2_page_9": {},
    }}}})
    assert set(_by_object(e)) == {"00414956", "Se_18_Assemblées_3_Bilanz1968_2_page_9"}


def test_the_legacy_filename_prefix_still_resolves(extract):
    """188 run directories name a test id their folder does not."""
    e = extract({"2025-03-01": {"T0001": {"requests": {
        "request_T01_jaccuse.json": {"provider": "openai"},
    }}}})
    assert list(_by_object(e)) == ["jaccuse"]


def test_line_is_populated_only_for_a_whole_line_n_object_id(extract):
    """It is presentation metadata. Never a join key, so a near-miss must stay null."""
    e = extract({"2026-01-01": {"T0001": {"requests": {
        "line_10": {}, "line_10a": {}, "0002_p002": {}, "letter01": {},
    }}}})
    rows = _by_object(e)
    assert rows["line_10"]["line"] == 10
    assert rows["line_10a"]["line"] is None
    assert rows["0002_p002"]["line"] is None
    assert rows["letter01"]["line"] is None


# --------------------------------------------------------------------------------
# Missing is not zero
# --------------------------------------------------------------------------------

def test_absent_usage_gives_null_tokens_not_zero(extract):
    e = extract({"2026-01-01": {"T0001": {"requests": {
        "none": {"provider": "openai", "model": "gpt-4o"},
        "empty": {"provider": "openai", "model": "gpt-4o", "usage": {}},
        "zero": {"provider": "openai", "model": "gpt-4o",
                 "usage": {"input_tokens": 0, "output_tokens": 0}},
    }}}})
    rows = _by_object(e)
    assert rows["none"]["input_tokens"] is None
    assert rows["empty"]["input_tokens"] is None, "an empty usage block records nothing"
    assert rows["zero"]["input_tokens"] == 0, "a recorded zero is a measurement"


def test_a_run_counts_what_it_found_not_what_it_could_read(extract):
    e = extract({"2026-01-01": {"T0001": {"requests": {
        "a": {"provider": "openai"}, "b": "{truncated", "c": {"error": "429"},
    }}}})
    row = e.runs[0]
    assert row["n_requests"] == 3, "every discovered file"
    assert row["n_valid_requests"] == 2, "only the ones that parsed"
    assert row["n_explicit_errors"] == 1


def test_an_error_record_without_a_duration_still_produces_a_full_row(extract):
    e = extract({"2026-01-01": {"T0001": {"requests": {
        "a": {"provider": "openai", "model": "gpt-4o", "error": True,
              "error_message": "rate limited"},
    }}}})
    row = e.requests[0]
    assert row["is_error"] is True and row["duration_s"] is None
    assert row["error_message"] == "rate limited"


def test_is_error_is_null_when_it_cannot_be_assessed(extract):
    """An unparseable file says nothing about whether the request failed."""
    e = extract({"2026-01-01": {"T0001": {"requests": {"a": "{truncated"}}}})
    assert e.requests[0]["is_error"] is None


# --------------------------------------------------------------------------------
# Status vocabularies
# --------------------------------------------------------------------------------

@pytest.mark.parametrize("scoring,expected", [
    (None, "missing"),
    ("{oops", "invalid"),
    ({"score": "niy"}, "not_implemented"),
    ({"cost_summary": {"total_cost_usd": 1.0}}, "no_numeric_metrics"),
    ({"f1_micro": 0.5}, "numeric_metrics_present"),
])
def test_run_scoring_status(extract, scoring, expected):
    spec = {"2026-01-01": {"T0001": {"requests": {"a": {}}}}}
    if scoring is not None:
        spec["2026-01-01"]["T0001"]["scoring"] = scoring
    assert extract(spec).runs[0]["scoring_status"] == expected


def test_niy_is_never_coerced_to_a_zero_score(extract):
    """A benchmark with no scorer is not a benchmark that scored nothing."""
    e = extract({"2026-01-01": {"T0001": {"requests": {"a": {}},
                                          "scoring": {"score": "niy"}}}})
    assert e.runs[0]["scoring_status"] == "not_implemented"
    assert [s for s in e.scores if s["level"] == "run"] == []


# --------------------------------------------------------------------------------
# Metrics
# --------------------------------------------------------------------------------

def test_only_real_numbers_become_score_rows(extract):
    e = extract({"2026-01-01": {"T0001": {"requests": {"a": {
        "score": {"f1_score": 0.5, "true_positives": 3, "message": "ignored",
                  "precision": "0.9", "recall": True},
    }}}}})
    got = dict((s["metric_id"], s["value"]) for s in e.scores if s["level"] == "request")
    assert got == {"company_lists.request.f1_score": 0.5,
                   "company_lists.request.true_positives": 3.0}, (
        "a numeric-looking string and a boolean are not measurements, and `message` "
        "carries no number at all")


def test_field_scores_keep_their_path_including_the_empty_one(extract):
    """6,080 stored records use the empty string as a field_scores key."""
    e = extract({"2026-01-01": {"T0001": {"requests": {"a": {
        "score": {"field_scores": {
            "persons[0].days[16].shifts[0].alternate_unit": {"score": 0.8},
            "": {"score": 0.25},
        }},
    }}}}})
    got = dict((s["field_path"], s["value"]) for s in e.scores if s["level"] == "field")
    assert got == {"persons[0].days[16].shifts[0].alternate_unit": 0.8, "": 0.25}


def test_a_field_score_of_none_produces_no_row(extract):
    """business_letters records counts and sets per-field similarity to null."""
    e = extract({"2026-01-01": {"T0001": {"requests": {"a": {
        "score": {"field_scores": {"send_date": {"response": "x", "score": None}}},
    }}}}})
    assert [s for s in e.scores if s["level"] == "field"] == []


def test_an_undefined_metric_stops_the_build(extract):
    """A new scorer key should force a definition, not flow in as an unexplained float."""
    with pytest.raises(ValueError, match="no entry in metrics.py"):
        extract({"2026-01-01": {"T0001": {"requests": {"a": {
            "score": {"brand_new_metric": 0.5},
        }}}}})


def test_the_dictionary_separates_parameters_from_measurements():
    assert M.BY_ID["magazine_pages.request.iou_threshold"]["metric_role"] == "parameter"
    assert M.BY_ID["magazine_pages.request.mean_iou"]["metric_role"] == "performance"
    assert M.BY_ID["company_lists.request.true_positives"]["metric_role"] == "count"


def test_fuzzy_is_scoped_by_benchmark_because_its_scale_differs():
    assert M.BY_ID["book_advert_xml.run.fuzzy"]["unit"] == "ratio_0_100"
    assert M.BY_ID["bibliographic_data.run.fuzzy"]["unit"] == "ratio_0_1"


# --------------------------------------------------------------------------------
# Cost
# --------------------------------------------------------------------------------

PRICES = {"2026-01-01": {"openai": {"gpt-4o": {"input_price": 2.5, "output_price": 10.0}}}}


def test_derived_cost_is_tokens_times_the_price_in_force(extract, make_pricing):
    make_pricing(PRICES)
    e = extract({"2026-01-01": {"T0001": {"requests": {"a": {
        "provider": "openai", "model": "gpt-4o",
        "usage": {"input_tokens": 1_000_000, "output_tokens": 500_000},
    }}}}})
    row = e.requests[0]
    assert row["derived_input_cost_usd"] == 2.5
    assert row["derived_output_cost_usd"] == 5.0
    assert row["derived_total_cost_usd"] == 7.5
    assert row["cost_provenance"] == "derived"
    assert row["pricing_bucket_date"] == "2026-01-01" and row["pricing_age_days"] == 0


def test_the_stored_cost_is_never_overwritten_by_the_derived_one(extract, make_pricing):
    """They disagree for a run costed against a stale table. Both are kept."""
    make_pricing(PRICES)
    e = extract({"2026-01-01": {"T0001": {"requests": {"a": {
        "provider": "openai", "model": "gpt-4o",
        "usage": {"input_tokens": 1_000_000, "output_tokens": 0,
                  "estimated_cost_usd": 99.0},
    }}}}})
    row = e.requests[0]
    assert row["stored_estimated_cost_usd"] == 99.0
    assert row["derived_total_cost_usd"] == 2.5


def test_the_response_identity_is_preferred_over_the_configured_one(extract, make_pricing):
    """The alias map is keyed on what the result file says actually served the request."""
    make_pricing(PRICES)
    e = extract({"2026-01-01": {"T0001": {"requests": {"a": {
        "provider": "openai", "model": "gpt-4o",
        "usage": {"input_tokens": 1_000_000, "output_tokens": 0},
    }}}}}, tests=[{"id": "T0001", "name": "company_lists", "provider": "anthropic",
                   "model": "claude-fable-5-1"}])
    row = e.requests[0]
    assert row["pricing_identity_source"] == "response"
    assert row["response_model"] == "gpt-4o" and row["configured_model"] == "claude-fable-5-1"
    assert row["derived_total_cost_usd"] == 2.5


def test_an_alias_resolves_to_its_pricing_key(extract, make_pricing):
    make_pricing(PRICES, aliases={"openai": {"gpt-4o": "gpt-4o-2026-01-01"}})
    e = extract({"2026-01-01": {"T0001": {"requests": {"a": {
        "provider": "openai", "model": "gpt-4o-2026-01-01",
        "usage": {"input_tokens": 1_000_000, "output_tokens": 0},
    }}}}})
    assert e.requests[0]["derived_total_cost_usd"] == 2.5


@pytest.mark.parametrize("record,expected", [
    ({"provider": "openai", "model": "gpt-4o"}, "no_tokens"),
    ({"provider": "openai", "model": "nothing-priced",
      "usage": {"input_tokens": 10}}, "no_price_in_table"),
    ({"usage": {"input_tokens": 10}}, "no_model_identity"),
])
def test_cost_provenance_says_why_there_is_no_derived_cost(extract, make_pricing,
                                                           record, expected):
    make_pricing(PRICES)
    e = extract({"2026-01-01": {"T0001": {"requests": {"a": record}}}},
                tests=[{"id": "T0001", "name": "company_lists"}])
    row = e.requests[0]
    assert row["cost_provenance"] == expected
    assert row["derived_total_cost_usd"] is None


def test_a_null_price_is_not_read_as_free(extract, make_pricing):
    """An unpriced entry is a real state in the table and must not cost zero."""
    make_pricing({"2026-01-01": {"openai": {"gpt-4o": {"input_price": None,
                                                       "output_price": None}}}})
    e = extract({"2026-01-01": {"T0001": {"requests": {"a": {
        "provider": "openai", "model": "gpt-4o", "usage": {"input_tokens": 1_000_000},
    }}}}})
    assert e.requests[0]["cost_provenance"] == "no_price_in_table"


def test_run_cost_coverage_is_an_observed_subtotal(extract, make_pricing):
    make_pricing(PRICES)
    e = extract({"2026-01-01": {"T0001": {"requests": {
        "a": {"provider": "openai", "model": "gpt-4o",
              "usage": {"input_tokens": 0, "output_tokens": 0, "estimated_cost_usd": 1.0}},
        "b": {"provider": "openai", "model": "gpt-4o"},
    }}}})
    row = e.runs[0]
    assert row["n_requests_with_stored_cost"] == 1
    assert row["observed_stored_cost_usd"] == 1.0
    assert row["stored_cost_coverage_fraction"] == 0.5
    assert row["stored_cost_complete_for_saved_requests"] is False


# --------------------------------------------------------------------------------
# Timestamps
# --------------------------------------------------------------------------------

def test_a_naive_timestamp_is_never_assumed_to_be_utc():
    """Every timestamp in the corpus is naive, so this column is null throughout."""
    assert parse_timestamp("2026-01-24T23:53:45.614205") == (None, None)


def test_an_offset_bearing_timestamp_converts():
    value, issue = parse_timestamp("2026-01-24T23:53:45+02:00")
    assert value is not None and issue is None


def test_an_unparseable_timestamp_is_a_diagnostic(extract):
    e = extract({"2026-01-01": {"T0001": {"requests": {
        "a": {"provider": "openai", "timestamp": "last Tuesday"},
    }}}})
    assert e.requests[0]["timestamp_raw"] == "last Tuesday"
    assert e.requests[0]["timestamp_utc"] is None
    assert [d["issue"] for d in e.diagnostics] == ["unparseable_timestamp"]


# --------------------------------------------------------------------------------
# Visibility
# --------------------------------------------------------------------------------

def test_hidden_is_legacy_or_display_false(extract):
    e = extract({"2026-01-01": {"T0001": {"requests": {"a": {}}},
                                "T0002": {"requests": {"a": {}}},
                                "T0003": {"requests": {"a": {}}}}},
                tests=[{"id": "T0001", "name": "company_lists", "legacy_test": "false"},
                       {"id": "T0002", "name": "company_lists", "legacy_test": "true"},
                       {"id": "T0003", "name": "test_benchmark2", "legacy_test": "false"}],
                metas={"company_lists": {}, "test_benchmark2": {"display": False}})
    rows = dict((r["test_id"], r) for r in e.runs)
    assert rows["T0001"]["hidden"] is False
    assert rows["T0002"]["hidden"] is True, "legacy"
    assert rows["T0003"]["hidden"] is True, "display: false"


def test_a_missing_display_key_means_visible(extract):
    """No benchmark sets display: true, so absence is the normal case."""
    e = extract({"2026-01-01": {"T0001": {"requests": {"a": {}}}}},
                metas={"company_lists": {"title": "Company lists"}})
    assert e.runs[0]["benchmark_display"] is True and e.runs[0]["hidden"] is False


# --------------------------------------------------------------------------------
# Payloads and serialisation
# --------------------------------------------------------------------------------

def test_the_payload_is_the_untouched_original(extract, tmp_path):
    """The main tables coerce; the sidecar must not."""
    record = {"provider": "openai", "parsed": {"a": None, "b": [], "c": 0.1},
              "text": "é", "usage": {}, "unknown_future_key": {"nested": True}}
    e = extract({"2026-01-01": {"T0001": {"requests": {"a": record}}}})
    payload = e.payloads["company_lists"][0]
    assert payload["source_record"] == record

    path = tmp_path / "p.jsonl.gz"
    sidecar = writers.JsonlGz(path)
    sidecar.write(payload)
    sidecar.close()
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        assert json.loads(handle.readline())["source_record"] == record


def test_csv_and_parquet_read_back_equal(extract, tmp_path):
    e = extract({"2026-01-01": {"T0001": {"requests": {
        "00414956": {"provider": "openai", "model": "gpt-4o",
                     "usage": {"input_tokens": 0},
                     "error_message": 'a "quoted", comma, and\nnewline'},
    }}, "T0002": {"requests": {"a": {}}}}},
        tests=[{"id": "T0001", "name": "company_lists"},
               {"id": "T0002", "name": "company_lists"}])
    for name, rows, schema in (("runs", e.runs, RUNS), ("requests", e.requests, REQUESTS)):
        writers.write_table(tmp_path, name, rows, schema,
                            SORT_KEYS[name], UNIQUE_KEYS[name])
    back = writers.read_csv(tmp_path / "requests.csv", REQUESTS, "requests")
    row = [r for r in back if r["object_id"] == "00414956"][0]
    assert row["object_id"] == "00414956", "leading zeros are not a number"
    assert row["input_tokens"] == 0
    assert row["error_message"] == 'a "quoted", comma, and\nnewline'
    assert row["cached_tokens"] is None


def test_the_empty_field_path_survives_the_csv_round_trip(extract, tmp_path):
    e = extract({"2026-01-01": {"T0001": {"requests": {"a": {
        "score": {"field_scores": {"": {"score": 0.25}, "real": {"score": 0.5}}},
    }}}}})
    writers.write_table(tmp_path, "scores_long", e.scores, SCORES_LONG,
                        SORT_KEYS["scores_long"], UNIQUE_KEYS["scores_long"])
    back = writers.read_csv(tmp_path / "scores_long.csv", SCORES_LONG, "scores_long")
    paths = dict((r["field_path"], r["level"]) for r in back)
    assert paths[""] == "field", "the empty key is data, not a null"


def test_a_duplicate_key_is_refused(tmp_path):
    rows = [{"run_id": "T0001@2026-01-01", "object_id": "a"},
            {"run_id": "T0001@2026-01-01", "object_id": "a"}]
    with pytest.raises(AssertionError, match="appears twice"):
        writers.write_table(tmp_path, "requests", rows, REQUESTS,
                            SORT_KEYS["requests"], UNIQUE_KEYS["requests"])


def test_gzip_output_is_byte_stable(tmp_path):
    """gzip stamps the current time into its header unless told not to."""
    digests = []
    for name in ("a", "b"):
        path = tmp_path / ("%s.jsonl.gz" % name)
        sidecar = writers.JsonlGz(path)
        sidecar.write({"run_id": "T0001@2026-01-01", "value": 1})
        sidecar.close()
        digests.append(path.read_bytes())
    assert digests[0] == digests[1]


def test_a_failed_build_leaves_the_previous_one_intact(tmp_path):
    final = tmp_path / "dataset"
    final.mkdir()
    (final / "runs.csv").write_text("good", encoding="utf-8")
    with pytest.raises(RuntimeError, match="nothing staged"):
        writers.publish(tmp_path / "never_created", final)
    assert (final / "runs.csv").read_text(encoding="utf-8") == "good"


# --------------------------------------------------------------------------------
# Nothing about the build machine reaches the release
# --------------------------------------------------------------------------------

def test_relative_path_strips_the_repository_root():
    """An absolute path would publish the build machine's username and layout.

    This shipped once. `source_path` was `Path.as_posix()` on an absolute path in `runs`,
    `requests` and every payload record -- 106,766 rows of
    `C:/Users/<name>/.../results/...` headed for a citable artifact -- and nothing was
    checking, because every other test asserted what a row contained rather than what it
    should not. The corpus-wide assertion lives in
    tests/integrity/test_dataset_export_integrity.py, since a tmp_path fixture sits
    outside the repository and cannot exercise the real case.
    """
    from scripts.export_dataset.inventory import relative_path
    from scripts.results_index import PROJECT_ROOT

    inside = PROJECT_ROOT / "results" / "2026-01-01" / "T0001" / "request_T0001_a.json"
    assert relative_path(inside) == "results/2026-01-01/T0001/request_T0001_a.json"
    assert relative_path(PROJECT_ROOT) == "."


def test_relative_path_falls_back_for_a_path_outside_the_repository(tmp_path):
    """Documented, not silent: a build whose --source lies elsewhere keeps absolute paths.

    Acceptable because such a build is a development one, and the release condition is
    asserted over the real corpus instead. Stated here so the fallback is a decision
    rather than a surprise.
    """
    from scripts.export_dataset.inventory import relative_path
    outside = tmp_path / "elsewhere" / "runs"
    assert relative_path(outside) == outside.as_posix()
