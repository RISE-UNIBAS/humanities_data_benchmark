"""Scoring tests for blacklist_cards.

score_request_answer averages the fuzzy similarity of every terminal field of the ground truth,
compared with the response at the same path; `null`, "null", `[]` and missing values count as "", so a
field empty on both sides scores 1.0. An unparseable response scores 0 on every field.
"""
import copy
import importlib
import json
import os

import pytest

BlacklistCards = importlib.import_module("benchmarks.blacklist_cards.benchmark").BlacklistCards

GROUND_TRUTHS = os.path.join(os.path.dirname(__file__), "..", "benchmarks", "blacklist_cards", "ground_truths")


def card(date="", info=("Britische schwarze Liste",)):
    return {"company": {"transcription": "Acme AG"}, "location": {"transcription": "Basel"},
            "b_id": {"transcription": "B.51.322.GB.1"}, "date": date,
            "information": [{"transcription": t} for t in info]}


@pytest.fixture
def scorer(make_scorer):
    return make_scorer(BlacklistCards)


def test_perfect_match(scorer, response):
    gt = card()
    assert scorer.score_request_answer("c", response(parsed=copy.deepcopy(gt)), gt)["fuzzy"] == 1.0


def test_empty_on_both_sides_scores_one(scorer, response):
    gt = card(date="")
    result = scorer.score_request_answer("c", response(parsed=card(date=None)), gt)
    assert result["field_scores"]["date"]["score"] == 1.0


@pytest.mark.parametrize("answer", [None, [], ""])
def test_empty_information_in_any_form_matches(scorer, response, answer):
    gt = card()
    gt["information"] = None
    pred = card()
    pred["information"] = answer
    assert scorer.score_request_answer("c", response(parsed=pred), gt)["fuzzy"] == 1.0


def test_missing_information_block_scores_zero(scorer, response):
    gt = card(info=("one", "two"))
    result = scorer.score_request_answer("c", response(parsed=card(info=("one",))), gt)
    assert result["field_scores"]["information[1].transcription"]["score"] == 0.0


def test_unparseable_response_scores_zero_on_every_field(scorer, response):
    assert BlacklistCards.score_unparseable_as_miss is True
    result = scorer.score_request_answer("c", response(parsed=None, text="prose"), card(date=""))
    assert result["fuzzy"] == 0.0


@pytest.mark.parametrize("name", sorted(f[:-5] for f in os.listdir(GROUND_TRUTHS) if f.endswith(".json")))
def test_every_ground_truth_matches_itself(scorer, response, name):
    with open(os.path.join(GROUND_TRUTHS, f"{name}.json"), encoding="utf-8") as f:
        gt = json.load(f)
    assert scorer.score_request_answer(name, response(parsed=copy.deepcopy(gt)), gt)["fuzzy"] == 1.0
