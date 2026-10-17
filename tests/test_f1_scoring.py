"""Scoring tests for the field-level F1 benchmarks.

company_lists, library_cards and personnel_cards share an identical
score_benchmark (micro/macro aggregation) but differ in score_request_answer:
  - company_lists: wraps a bare-list response into {"entries": ...}; filters metadata.*
  - library_cards: filters examination.* and a couple of removed keys.
  - personnel_cards: filters by self.rules and always skips row_number.
"""
import importlib
import json
import os

import pytest

CompanyLists = importlib.import_module("benchmarks.company_lists.benchmark").CompanyLists
LibraryCards = importlib.import_module("benchmarks.library_cards.benchmark").LibraryCards
PersonnelCards = importlib.import_module("benchmarks.personnel_cards.benchmark").PersonnelCards

COMPANY_LISTS_GT = os.path.join(os.path.dirname(__file__), "..", "benchmarks", "company_lists", "ground_truths")


# --------------------------------------------------------------------------- #
# Shared score_benchmark (identical across all three classes)
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("cls", [CompanyLists, LibraryCards, PersonnelCards])
class TestScoreBenchmark:
    def test_empty_scores(self, make_scorer, cls):
        assert make_scorer(cls).score_benchmark([]) == {"f1_micro": 0.0, "f1_macro": 0.0}

    def test_micro_vs_macro_diverge(self, make_scorer, cls):
        scores = [
            {"f1_score": 1.0, "true_positives": 1, "false_positives": 0, "false_negatives": 0},
            {"f1_score": 0.0, "true_positives": 0, "false_positives": 3, "false_negatives": 3},
        ]
        result = make_scorer(cls).score_benchmark(scores)
        assert result["total_tp"] == 1
        assert result["total_fp"] == 3
        assert result["total_fn"] == 3
        assert result["f1_macro"] == pytest.approx(0.5)      # mean of [1.0, 0.0]
        assert result["f1_micro"] == pytest.approx(0.25)     # pooled: 2*.25*.25/.5
        assert result["f1_micro"] != result["f1_macro"]

    def test_zero_division_safe(self, make_scorer, cls):
        scores = [{"f1_score": 0.0, "true_positives": 0, "false_positives": 0, "false_negatives": 0}]
        result = make_scorer(cls).score_benchmark(scores)
        assert result["f1_micro"] == 0.0
        assert result["f1_macro"] == 0.0


# --------------------------------------------------------------------------- #
# company_lists score_request_answer
# --------------------------------------------------------------------------- #
class TestCompanyLists:
    @pytest.fixture
    def scorer(self, make_scorer):
        return make_scorer(CompanyLists)

    def test_perfect_match(self, scorer, response):
        gt = {"entries": [{"name": "Acme", "city": "Basel"}]}
        result = scorer.score_request_answer("img", response(parsed=gt), gt)
        assert (result["true_positives"], result["false_positives"], result["false_negatives"]) == (2, 0, 0)
        assert result["f1_score"] == 1.0

    def test_bare_list_response_wrapped(self, scorer, response):
        gt = {"entries": [{"name": "Acme", "city": "Basel"}]}
        result = scorer.score_request_answer("img", response(parsed=[{"name": "Acme", "city": "Basel"}]), gt)
        assert result["f1_score"] == 1.0

    def test_mismatch_is_fp_and_fn(self, scorer, response):
        gt = {"entries": [{"name": "Acme"}]}
        pred = {"entries": [{"name": "Totally Different"}]}
        result = scorer.score_request_answer("img", response(parsed=pred), gt)
        assert (result["true_positives"], result["false_positives"], result["false_negatives"]) == (0, 1, 1)

    def test_extra_field_is_fp(self, scorer, response):
        gt = {"entries": [{"name": "Acme"}]}
        pred = {"entries": [{"name": "Acme", "city": "Basel"}]}
        result = scorer.score_request_answer("img", response(parsed=pred), gt)
        assert (result["true_positives"], result["false_positives"], result["false_negatives"]) == (1, 1, 0)

    def test_missing_field_is_fn(self, scorer, response):
        gt = {"entries": [{"name": "Acme", "city": "Basel"}]}
        pred = {"entries": [{"name": "Acme"}]}
        result = scorer.score_request_answer("img", response(parsed=pred), gt)
        assert (result["true_positives"], result["false_positives"], result["false_negatives"]) == (1, 0, 1)

    def test_metadata_ignored(self, scorer, response):
        gt = {"metadata": {"source": "x"}, "entries": [{"name": "Acme"}]}
        pred = {"metadata": {"source": "WRONG"}, "entries": [{"name": "Acme"}]}
        result = scorer.score_request_answer("img", response(parsed=pred), gt)
        assert (result["true_positives"], result["false_positives"], result["false_negatives"]) == (1, 0, 0)

    def test_unparseable_response_is_a_miss(self, scorer, response):
        assert CompanyLists.score_unparseable_as_miss is True
        gt = {"page_id": "p", "entries": [{"entry_id": "p-1", "company_name": "Acme", "location": "Basel"}]}
        result = scorer.score_request_answer("img", response(parsed=None, text="prose"), gt)
        assert (result["true_positives"], result["false_positives"], result["false_negatives"]) == (0, 0, 2)

    def test_identifiers_ignored(self, scorer, response):
        gt = {"page_id": "156089_1321081_14", "entries": [{"entry_id": "156089_1321081_14-1",
                                                           "company_name": "Acme", "location": "Basel"}]}
        pred = {"page_id": "page_24", "entries": [{"entry_id": "page_24-1",
                                                   "company_name": "Acme", "location": "Basel"}]}
        result = scorer.score_request_answer("img", response(parsed=pred), gt)
        assert (result["true_positives"], result["false_positives"], result["false_negatives"]) == (2, 0, 0)
        assert "page_id" not in result["field_scores"]

    @pytest.mark.parametrize("name", sorted(
        f[:-5] for f in os.listdir(COMPANY_LISTS_GT) if f.endswith(".json")))
    def test_every_ground_truth_matches_itself(self, scorer, response, name):
        with open(os.path.join(COMPANY_LISTS_GT, f"{name}.json"), encoding="utf-8") as f:
            gt = json.load(f)
        result = scorer.score_request_answer(name, response(parsed=gt), gt)
        assert (result["false_positives"], result["false_negatives"]) == (0, 0)
        assert result["f1_score"] == 1.0


# --------------------------------------------------------------------------- #
# library_cards score_request_answer
# --------------------------------------------------------------------------- #
class TestLibraryCards:
    @pytest.fixture
    def scorer(self, make_scorer):
        return make_scorer(LibraryCards)

    def test_perfect_match(self, scorer, response):
        fields = {"title": "Book", "author": "Smith"}
        result = scorer.score_request_answer("img", response(parsed=fields), fields)
        assert (result["true_positives"], result["false_positives"], result["false_negatives"]) == (2, 0, 0)
        assert result["f1_score"] == 1.0

    def test_unparseable_response_is_a_miss(self, scorer, response):
        assert LibraryCards.score_unparseable_as_miss is True
        result = scorer.score_request_answer("img", response(parsed=None, text="prose"), {"title": "Book", "year": "1950"})
        assert (result["true_positives"], result["false_positives"], result["false_negatives"]) == (0, 0, 2)

    def test_examination_fields_ignored(self, scorer, response):
        gt = {"title": "Book", "examination": {"note": "x"}}
        pred = {"title": "Book", "examination": {"note": "WRONG"}}
        result = scorer.score_request_answer("img", response(parsed=pred), gt)
        # examination.* filtered out -> only title scored
        assert (result["true_positives"], result["false_positives"], result["false_negatives"]) == (1, 0, 0)

    def test_mismatch_is_fp_and_fn(self, scorer, response):
        gt = {"title": "Original Title"}
        pred = {"title": "Nothing Alike Here"}
        result = scorer.score_request_answer("img", response(parsed=pred), gt)
        assert (result["true_positives"], result["false_positives"], result["false_negatives"]) == (0, 1, 1)


# --------------------------------------------------------------------------- #
# personnel_cards score_request_answer (rules-gated; row_number skipped)
# --------------------------------------------------------------------------- #
def _row(transcript="Angestellter", crossed=False):
    return {"rows": [{"row_number": 1, "position": {
        "diplomatic_transcript": transcript, "interpretation": None, "is_crossed_out": crossed}}]}


class TestPersonnelCards:
    def test_perfect_match_default_rules(self, make_scorer, response):
        scorer = make_scorer(PersonnelCards, rules=None)
        gt = _row()
        result = scorer.score_request_answer("img", response(parsed=gt), gt)
        # transcript + is_crossed_out match (interpretation is None on both -> not counted)
        assert (result["true_positives"], result["false_positives"], result["false_negatives"]) == (2, 0, 0)
        assert result["f1_score"] == 1.0

    def test_row_number_never_scored(self, make_scorer, response):
        scorer = make_scorer(PersonnelCards, rules=None)
        gt = _row()
        pred = _row()
        pred["rows"][0]["row_number"] = 999  # differs, but must be ignored
        result = scorer.score_request_answer("img", response(parsed=pred), gt)
        assert (result["true_positives"], result["false_positives"], result["false_negatives"]) == (2, 0, 0)

    def test_rule_disables_is_crossed_out(self, make_scorer, response):
        gt = _row(crossed=False)
        pred = _row(crossed=True)  # is_crossed_out mismatches

        with_default = make_scorer(PersonnelCards, rules=None).score_request_answer("img", response(parsed=pred), gt)
        with_rule_off = make_scorer(
            PersonnelCards, rules={"score_is_crossed_out": False}
        ).score_request_answer("img", response(parsed=pred), gt)

        # default scores the mismatch (fp+fn); disabling the rule drops it entirely
        assert with_default["false_positives"] >= 1 and with_default["false_negatives"] >= 1
        assert (with_rule_off["false_positives"], with_rule_off["false_negatives"]) == (0, 0)
        assert with_rule_off["f1_score"] == 1.0

def test_personnel_cards_scores_unparseable_answers_as_misses(make_scorer, response):
    assert PersonnelCards.score_unparseable_as_miss is True
    result = make_scorer(PersonnelCards).score_request_answer(
        "img", response(parsed=None, text="prose"), {"rows": [{"row_number": 1, "dienstort": {"diplomatic_transcript": "Bern"}}]})
    assert result["true_positives"] == 0 and result["false_negatives"] > 0
