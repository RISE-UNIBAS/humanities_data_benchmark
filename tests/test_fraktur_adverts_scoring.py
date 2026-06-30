"""Scoring tests for benchmarks/fraktur_adverts (CER + fuzzy).

Covers the pure/aggregation logic: calculate_cer (note: unlike medieval_manuscripts,
an empty reference is always max error), score_benchmark averaging, and the
number-prefix parser. The section/number grouping in compare_ads is integration-heavy
and intentionally not unit-tested here.
"""
import importlib

import pytest

_fraktur = importlib.import_module("benchmarks.fraktur_adverts.benchmark")
FrakturAdverts = _fraktur.FrakturAdverts
DEFAULT_SECTION = _fraktur.DEFAULT_SECTION


@pytest.fixture
def scorer(make_scorer):
    return make_scorer(FrakturAdverts)


class TestCalculateCer:
    def test_identical_is_zero(self, scorer):
        assert scorer.calculate_cer("hello world", "hello world") == 0.0

    def test_empty_reference_is_max(self, scorer):
        assert scorer.calculate_cer("", "anything") == 1.0
        assert scorer.calculate_cer("", "") == 1.0  # empty ref -> 1.0 even if both empty

    def test_empty_hypothesis_is_max(self, scorer):
        assert scorer.calculate_cer("text", "") == 1.0

    def test_single_substitution(self, scorer):
        assert scorer.calculate_cer("kitten", "sitten") == pytest.approx(1 / 6)

    def test_case_and_whitespace_normalized(self, scorer):
        assert scorer.calculate_cer("Hello   World", "hello world") == 0.0

    def test_capped_at_one(self, scorer):
        assert scorer.calculate_cer("ab", "xyzwvurst") == 1.0


class TestScoreBenchmark:
    def test_empty_returns_worst_cer(self, scorer):
        assert scorer.score_benchmark([]) == {"fuzzy": 0.0, "cer": 1.0}

    def test_averages(self, scorer):
        assert scorer.score_benchmark([{"fuzzy": 1.0, "cer": 0.0}, {"fuzzy": 0.0, "cer": 1.0}]) == {
            "fuzzy": 0.5, "cer": 0.5}


class TestExtractNumberPrefix:
    def test_leading_number(self, scorer):
        assert scorer.extract_number_prefix("16. Bey Hrn. Rudolf") == 16

    def test_leading_whitespace_tolerated(self, scorer):
        assert scorer.extract_number_prefix("  3. etwas") == 3

    def test_no_prefix(self, scorer):
        assert scorer.extract_number_prefix("Bey Hrn. ohne Nummer") is None


class TestScoreRequestAnswerGolden:
    """End-to-end goldens with hand-verified expected scores."""

    def test_standard_match_and_miss(self, scorer, response):
        section = "Es werden zum Verkauff offerirt"
        gt = {section: [
            {"tags_section": section, "text": "1. Ein schoenes Buch"},
            {"tags_section": section, "text": "2. Ein altes Haus"},
        ]}
        parsed = {"advertisements": [
            {"tags_section": section, "text": "1. Ein schoenes Buch"},  # ad #2 omitted
        ]}
        # ad 1: exact match -> similarity 1.0, cer 0.0
        # ad 2: no response  -> similarity 0.0, cer 1.0
        # averages: fuzzy (1.0+0.0)/2 = 0.5, cer (0.0+1.0)/2 = 0.5
        assert scorer.score_request_answer("image_1", response(parsed=parsed), gt) == {"fuzzy": 0.5, "cer": 0.5}

    def test_image_4_default_section_forced(self, scorer, response):
        gt = {DEFAULT_SECTION: [{"tags_section": DEFAULT_SECTION, "text": "1. Foo"}]}
        # response ad has no tags_section -> image_4 handling forces DEFAULT_SECTION, then matches
        parsed = {"advertisements": [{"text": "1. Foo"}]}
        assert scorer.score_request_answer("image_4", response(parsed=parsed), gt) == {"fuzzy": 1.0, "cer": 0.0}