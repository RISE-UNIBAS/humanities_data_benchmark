"""Scoring tests for benchmarks/medieval_manuscripts (CER + fuzzy)."""
import copy
import importlib
import json
import os

import pytest

MedievalManuscripts = importlib.import_module(
    "benchmarks.medieval_manuscripts.benchmark"
).MedievalManuscripts


@pytest.fixture
def scorer(make_scorer):
    return make_scorer(MedievalManuscripts)


class TestCalculateCer:
    def test_identical_is_zero(self, scorer):
        assert scorer.calculate_cer("hello world", "hello world") == 0.0

    def test_both_empty_is_zero(self, scorer):
        assert scorer.calculate_cer("", "") == 0.0
        assert scorer.calculate_cer(None, "   ") == 0.0

    def test_one_empty_is_max(self, scorer):
        assert scorer.calculate_cer("text", "") == 1.0
        assert scorer.calculate_cer("", "text") == 1.0

    def test_single_substitution(self, scorer):
        # 'kitten' vs 'sitten': 1 edit over 6 reference chars
        assert scorer.calculate_cer("kitten", "sitten") == pytest.approx(1 / 6)

    def test_case_and_whitespace_normalized(self, scorer):
        assert scorer.calculate_cer("Hello   World", "hello world") == 0.0

    def test_capped_at_one(self, scorer):
        assert scorer.calculate_cer("ab", "xyzwvurst") == 1.0


class TestNormalizeEmpty:
    def test_none_and_whitespace_to_empty(self, scorer):
        assert scorer.normalize_empty(None) == ""
        assert scorer.normalize_empty("   ") == ""

    def test_value_preserved(self, scorer):
        assert scorer.normalize_empty("abc") == "abc"

    def test_a_number_is_compared_as_its_text_and_other_values_as_empty(self, scorer):
        assert (scorer.normalize_empty(18), scorer.normalize_empty(1.5)) == ("18", "1.5")
        assert [scorer.normalize_empty(v) for v in (True, [], ["a"], {"a": 1})] == ["", "", "", ""]


class TestScoreBenchmark:
    def test_empty_returns_worst_cer(self, scorer):
        assert scorer.score_benchmark([]) == {"fuzzy": 0.0, "cer": 1.0}

    def test_averages_and_skips_none(self, scorer):
        scores = [{"fuzzy": 1.0, "cer": 0.0}, None, {"fuzzy": 0.0, "cer": 1.0}]
        assert scorer.score_benchmark(scores) == {"fuzzy": 0.5, "cer": 0.5}


class TestScoreRequestAnswer:
    def test_perfect_match(self, scorer, response, metrics):
        gt = {"[3r]": [{"folio": "3r", "text": "hello"}]}
        parsed = {"folios": [{"folio": "3r", "text": "hello"}]}
        assert metrics(scorer.score_request_answer("img", response(parsed=parsed), gt)) == {"fuzzy": 1.0, "cer": 0.0}

    def test_no_response_folio_is_worst(self, scorer, response, metrics):
        gt = {"[3r]": [{"folio": "3r", "text": "hello"}]}
        parsed = {"folios": []}  # nothing to match -> similarity 0, cer 1
        assert metrics(scorer.score_request_answer("img", response(parsed=parsed), gt)) == {"fuzzy": 0.0, "cer": 1.0}

GROUND_TRUTHS = os.path.join(os.path.dirname(__file__), "..", "benchmarks", "medieval_manuscripts", "ground_truths")


class TestUnparseable:
    def test_scored_as_a_miss(self):
        assert MedievalManuscripts.score_unparseable_as_miss is True

    def test_unparseable_response_misses_every_field(self, scorer, response, metrics):
        gt = {"[3r]": [{"folio": "3", "text": "hello", "addition1": "note"}]}
        result = scorer.score_request_answer("img", response(parsed=None, text="no json"), gt)
        assert metrics(result) == {"fuzzy": 0.0, "cer": 1.0}
        assert len(result["field_scores"]) == 3


class TestFields:
    def test_empty_folio_on_both_sides_is_not_scored(self, scorer, response):
        gt = {"[4v]": [{"folio": "", "text": "hello"}]}
        result = scorer.score_request_answer("img", response(parsed={"folios": [{"folio": "", "text": "hello"}]}), gt)
        assert list(result["field_scores"]) == ["[4v] text"]

    def test_folio_counts_as_much_as_the_text(self, scorer, response, metrics):
        gt = {"[18r]": [{"folio": "18", "text": "hello"}]}
        result = scorer.score_request_answer("img", response(parsed={"folios": [{"folio": "", "text": "hello"}]}), gt)
        assert metrics(result) == {"fuzzy": 0.5, "cer": 0.5}

    @pytest.mark.parametrize("entry", [1, "3r hello", ["3r", "hello"], None])
    def test_a_folio_that_is_not_an_object_misses_its_fields(self, scorer, response, metrics, entry):
        gt = {"[3r]": [{"folio": "3r", "text": "hello"}]}
        result = scorer.score_request_answer("img", response(parsed={"folios": [entry]}), gt)
        assert metrics(result) == {"fuzzy": 0.0, "cer": 1.0}

    def test_a_numeric_folio_is_scored_as_text(self, scorer, response, metrics):
        gt = {"[18r]": [{"folio": "18", "text": "hello"}]}
        result = scorer.score_request_answer("img", response(parsed={"folios": [{"folio": 18, "text": "hello"}]}), gt)
        assert metrics(result) == {"fuzzy": 1.0, "cer": 0.0}

    def test_additions_stop_at_the_first_missing_key(self, scorer, response):
        gt = {"[9v]": [{"folio": "", "text": "a", "addition1": "x"}]}
        parsed = {"folios": [{"folio": "", "text": "a", "addition1": "x", "addition2": "extra"}]}
        result = scorer.score_request_answer("img", response(parsed=parsed), gt)
        assert "[9v] addition2" not in result["field_scores"]


class TestGroundTruth:
    @pytest.mark.parametrize("name", sorted(f[:-5] for f in os.listdir(GROUND_TRUTHS) if f.endswith(".json")))
    def test_every_ground_truth_matches_itself(self, scorer, response, metrics, name):
        with open(os.path.join(GROUND_TRUTHS, f"{name}.json"), encoding="utf-8") as f:
            gt = json.load(f)
        parsed = {"folios": [copy.deepcopy(entries[0]) for _, entries in sorted(gt.items())]}
        assert metrics(scorer.score_request_answer(name, response(parsed=parsed), gt)) == {"fuzzy": 1.0, "cer": 0.0}

    @pytest.mark.parametrize("name", sorted(f[:-5] for f in os.listdir(GROUND_TRUTHS) if f.endswith(".json")))
    def test_recto_pages_carry_their_folio_number(self, name):
        with open(os.path.join(GROUND_TRUTHS, f"{name}.json"), encoding="utf-8") as f:
            gt = json.load(f)
        for ref, entries in gt.items():
            if ref.endswith("r]"):
                assert entries[0]["folio"] == ref[1:-2], f"{name} {ref}: folio {entries[0]['folio']!r}"
