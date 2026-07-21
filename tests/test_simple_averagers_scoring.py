"""Scoring tests for the simple averaging benchmarks.

bibliographic_data, blacklist_cards and book_advert_xml delegate field scoring
to scoring_helper and average per-request fuzzy scores. The shared risk is a
ZeroDivisionError on an empty score list (an all-failed run); all three must
return a zero score instead.
"""
import importlib

import pytest

BibliographicData = importlib.import_module("benchmarks.bibliographic_data.benchmark").BibliographicData
BlacklistCards = importlib.import_module("benchmarks.blacklist_cards.benchmark").BlacklistCards
BookAdvertXml = importlib.import_module("benchmarks.book_advert_xml.benchmark").BookAdvertXml


@pytest.mark.parametrize("cls", [BibliographicData, BlacklistCards, BookAdvertXml])
def test_score_benchmark_empty_does_not_crash(make_scorer, cls):
    # Must not raise ZeroDivisionError; returns a zero fuzzy score.
    assert make_scorer(cls).score_benchmark([])["fuzzy"] == 0.0


@pytest.mark.parametrize("cls", [BibliographicData, BlacklistCards])
def test_score_benchmark_averages_fuzzy(make_scorer, cls):
    result = make_scorer(cls).score_benchmark([{"fuzzy": 1.0}, {"fuzzy": 0.0}])
    assert result["fuzzy"] == pytest.approx(0.5)


class TestBibliographicAndBlacklistRequestAnswer:
    @pytest.mark.parametrize("cls", [BibliographicData, BlacklistCards])
    def test_perfect_match(self, make_scorer, response, cls):
        gt = {"entries": [{"name": "Acme"}]}
        assert make_scorer(cls).score_request_answer("img", response(parsed=gt), gt)["fuzzy"] == pytest.approx(1.0)

    @pytest.mark.parametrize("cls", [BibliographicData, BlacklistCards])
    def test_metadata_skipped(self, make_scorer, response, cls):
        # metadata mismatch must not lower the score (metadata keys are skipped)
        gt = {"metadata": {"src": "x"}, "entries": [{"name": "Acme"}]}
        pred = {"metadata": {"src": "WRONG"}, "entries": [{"name": "Acme"}]}
        assert make_scorer(cls).score_request_answer("img", response(parsed=pred), gt)["fuzzy"] == pytest.approx(1.0)

    @pytest.mark.parametrize("cls", [BibliographicData, BlacklistCards])
    def test_bare_list_response_wrapped(self, make_scorer, response, cls):
        gt = {"entries": [{"name": "Acme"}]}
        assert make_scorer(cls).score_request_answer("img", response(parsed=[{"name": "Acme"}]), gt)["fuzzy"] == pytest.approx(1.0)


class TestBookAdvertXml:
    @pytest.fixture
    def scorer(self, make_scorer):
        return make_scorer(BookAdvertXml)

    def test_missing_fixed_xml(self, scorer, response):
        assert scorer.score_request_answer("img", response(parsed={}), {"fixed_xml": "<a/>"}) == {
            "score": 0.0, "message": "No valid response"}

    def test_perfect_match_ignores_whitespace(self, scorer, response):
        pred = {"fixed_xml": "<a>\n  <b/> </a>"}
        gt = {"fixed_xml": "<a><b/></a>"}
        assert scorer.score_request_answer("img", response(parsed=pred), gt)["fuzzy"] == pytest.approx(100.0)

    def test_score_benchmark_reports_n(self, scorer):
        result = scorer.score_benchmark([{"fuzzy": 100.0}, {"fuzzy": 0.0}])
        assert result["fuzzy"] == pytest.approx(50.0)
        assert result["n"] == 2