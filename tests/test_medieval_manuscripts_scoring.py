"""Scoring tests for benchmarks/medieval_manuscripts (CER + fuzzy)."""
import importlib

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


class TestScoreBenchmark:
    def test_empty_returns_worst_cer(self, scorer):
        assert scorer.score_benchmark([]) == {"fuzzy": 0.0, "cer": 1.0}

    def test_averages_and_skips_none(self, scorer):
        scores = [{"fuzzy": 1.0, "cer": 0.0}, None, {"fuzzy": 0.0, "cer": 1.0}]
        assert scorer.score_benchmark(scores) == {"fuzzy": 0.5, "cer": 0.5}


class TestScoreRequestAnswer:
    def test_perfect_match(self, scorer, response):
        gt = {"[3r]": [{"folio": "3r", "text": "hello"}]}
        parsed = {"folios": [{"folio": "3r", "text": "hello"}]}
        assert scorer.score_request_answer("img", response(parsed=parsed), gt) == {"fuzzy": 1.0, "cer": 0.0}

    def test_no_response_folio_is_worst(self, scorer, response):
        gt = {"[3r]": [{"folio": "3r", "text": "hello"}]}
        parsed = {"folios": []}  # nothing to match -> similarity 0, cer 1
        assert scorer.score_request_answer("img", response(parsed=parsed), gt) == {"fuzzy": 0.0, "cer": 1.0}