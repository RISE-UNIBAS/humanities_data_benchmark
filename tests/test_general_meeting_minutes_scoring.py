"""Scoring tests for general_meeting_minutes.

score_request_answer averages the fuzzy similarity of every terminal field of the ground
truth, compared with the response at the same path. Only ground-truth paths are scored, so
extra response rows cost nothing. score_benchmark averages the per-page `fuzzy` values.
"""
import copy
import importlib
import json
import os

import pytest

GeneralMeetingMinutes = importlib.import_module(
    "benchmarks.general_meeting_minutes.benchmark").GeneralMeetingMinutes

GROUND_TRUTHS = os.path.join(os.path.dirname(__file__), "..", "benchmarks", "general_meeting_minutes",
                             "ground_truths")


def entry(number="1", name="Monsieur BREHAM Alain", signature_present=False, signature=""):
    return {"number": number, "name": name, "address": "NEUILLY-S/SEINE", "actions_o": "179",
            "actions_p": "520", "no_de_voix": "699", "signature_present": signature_present,
            "signature": signature}


def page(entries):
    return {"document": "Se_18_page_9", "page_number": 9, "entries": entries}


@pytest.fixture
def scorer(make_scorer):
    return make_scorer(GeneralMeetingMinutes)


class TestScoreRequestAnswer:
    def test_perfect_match(self, scorer, response):
        gt = page([entry()])
        assert scorer.score_request_answer("p", response(parsed=copy.deepcopy(gt)), gt)["fuzzy"] == 1.0

    def test_score_is_the_mean_over_ground_truth_fields(self, scorer, response):
        gt = page([entry(name="Basel")])
        pred = page([entry(name="Base")])
        # 10 fields: 9 identical, name scores fuzz.ratio("Base", "Basel") = 8/9.
        result = scorer.score_request_answer("p", response(parsed=pred), gt)
        assert result["fuzzy"] == pytest.approx((9 + 8 / 9) / 10)
        assert result["field_scores"]["entries[0].name"]["score"] == pytest.approx(8 / 9)

    def test_empty_strings_on_both_sides_score_one(self, scorer, response):
        gt = page([entry(signature="")])
        result = scorer.score_request_answer("p", response(parsed=copy.deepcopy(gt)), gt)
        assert result["field_scores"]["entries[0].signature"]["score"] == 1.0

    def test_missing_response_field_scores_zero(self, scorer, response):
        gt = page([entry()])
        pred = copy.deepcopy(gt)
        del pred["entries"][0]["address"]
        result = scorer.score_request_answer("p", response(parsed=pred), gt)
        assert result["field_scores"]["entries[0].address"]["score"] == 0.0

    def test_wrong_boolean_is_compared_as_text(self, scorer, response):
        gt = page([entry(signature_present=True)])
        pred = page([entry(signature_present=False)])
        result = scorer.score_request_answer("p", response(parsed=pred), gt)
        assert result["field_scores"]["entries[0].signature_present"]["score"] == pytest.approx(2 / 9)

    def test_extra_response_rows_are_not_scored(self, scorer, response):
        gt = page([entry()])
        pred = page([entry(), entry(number="2", name="Somebody Else")])
        assert scorer.score_request_answer("p", response(parsed=pred), gt)["fuzzy"] == 1.0

    def test_rows_are_compared_by_position(self, scorer, response):
        gt = page([entry(number="1", name="Alpha"), entry(number="2", name="Omega")])
        pred = page([entry(number="2", name="Omega")])
        result = scorer.score_request_answer("p", response(parsed=pred), gt)
        assert result["field_scores"]["entries[0].name"]["response"] == "Omega"
        assert result["field_scores"]["entries[1].name"]["score"] == 0.0

    def test_unparseable_response(self, scorer, response):
        gt = page([entry(signature="x")])
        result = scorer.score_request_answer("p", response(parsed=None, text="not json"), gt)
        assert result["fuzzy"] == 0.0

    def test_unparseable_answers_are_scored(self):
        assert GeneralMeetingMinutes.score_unparseable_as_miss is True

    @pytest.mark.parametrize("name", sorted(f[:-5] for f in os.listdir(GROUND_TRUTHS) if f.endswith(".json")))
    def test_every_ground_truth_matches_itself(self, scorer, response, name):
        with open(os.path.join(GROUND_TRUTHS, f"{name}.json"), encoding="utf-8") as f:
            gt = json.load(f)
        assert scorer.score_request_answer(name, response(parsed=copy.deepcopy(gt)), gt)["fuzzy"] == 1.0


class TestPromptKwargs:
    def test_page_number_from_file_name(self, scorer):
        kwargs = scorer.get_prompt_kwargs("Se_19_Assemblée Mine d. Costano_2.9_12.1962_page_4", [])
        assert kwargs == {"filename": "Se_19_Assemblée Mine d. Costano_2.9_12.1962_page_4", "page_number": "4"}


class TestScoreBenchmark:
    def test_empty(self, scorer):
        assert scorer.score_benchmark([]) == {"fuzzy": 0.0}

    def test_mean_of_pages(self, scorer):
        assert scorer.score_benchmark([{"fuzzy": 1.0}, {"fuzzy": 0.5}]) == {"fuzzy": 0.75}
