"""Scoring tests for duty_rosters.

score_request_answer compares every terminal field of the Schedule JSON at the same path
(persons[i].days[j].shifts[k].<field>), counting a match at fuzzy similarity >= 0.92.
Empty strings count as missing; a field missing on both sides counts as nothing.
score_benchmark pools TP/FP/FN for f1_micro and averages the per-row f1_score for f1_macro.
"""
import copy
import importlib
import json
import os

import pytest

DutyRosters = importlib.import_module("benchmarks.duty_rosters.benchmark").DutyRosters

GROUND_TRUTHS = os.path.join(os.path.dirname(__file__), "..", "benchmarks", "duty_rosters", "ground_truths")


def shift(icon="F-Dienst 1", length="full", planned=True, alternate=None):
    return {"icon": icon, "length": length, "planned_on_current_unit": planned, "alternate_unit": alternate}


def schedule(days):
    """A one-person Schedule; `days` maps an ISO date to its list of shifts."""
    return {"year": 2025, "month": "April", "persons": [{
        "id": "103", "profession": "WBL", "employment_percent": 80, "is_jumper": False,
        "days": [{"date": date, "shifts": shifts} for date, shifts in days.items()],
    }]}


# Scored fields of schedule() with one full shift: year, month, 4 person fields, date,
# and the shift's icon, length and planned_on_current_unit (alternate_unit is null).
ONE_SHIFT_FIELDS = 10


def counts(result):
    return result["true_positives"], result["false_positives"], result["false_negatives"]


@pytest.fixture
def scorer(make_scorer):
    return make_scorer(DutyRosters)


class TestScoreRequestAnswer:
    def test_perfect_match(self, scorer, response):
        gt = schedule({"2025-04-01": [shift()]})
        result = scorer.score_request_answer("row", response(parsed=copy.deepcopy(gt)), gt)
        assert counts(result) == (ONE_SHIFT_FIELDS, 0, 0)
        assert result["f1_score"] == 1.0

    def test_wrong_icon_is_fp_and_fn(self, scorer, response):
        gt = schedule({"2025-04-01": [shift(icon="F-Dienst 1")]})
        pred = schedule({"2025-04-01": [shift(icon="Ferien")]})
        assert counts(scorer.score_request_answer("row", response(parsed=pred), gt)) == (ONE_SHIFT_FIELDS - 1, 1, 1)

    def test_null_on_both_sides_counts_nothing(self, scorer, response):
        gt = schedule({"2025-04-01": [shift(icon=None)]})
        result = scorer.score_request_answer("row", response(parsed=copy.deepcopy(gt)), gt)
        assert counts(result) == (ONE_SHIFT_FIELDS - 1, 0, 0)

    def test_empty_string_counts_as_missing(self, scorer, response):
        gt = schedule({"2025-04-01": [shift(alternate="LE")]})
        pred = schedule({"2025-04-01": [shift(alternate="")]})
        assert counts(scorer.score_request_answer("row", response(parsed=pred), gt)) == (ONE_SHIFT_FIELDS, 0, 1)

    def test_extra_alternate_unit_is_fp(self, scorer, response):
        gt = schedule({"2025-04-01": [shift()]})
        pred = schedule({"2025-04-01": [shift(alternate="TS")]})
        assert counts(scorer.score_request_answer("row", response(parsed=pred), gt)) == (ONE_SHIFT_FIELDS, 1, 0)

    def test_split_cell_missing_half_is_fn(self, scorer, response):
        gt = schedule({"2025-04-29": [shift(icon="Freier Tag", length="half_left"),
                                      shift(icon="Persönliche Absenz", length="half_right")]})
        pred = schedule({"2025-04-29": [shift(icon="Freier Tag", length="half_left")]})
        # The second shift's icon, length and planned flag are only in the ground truth.
        assert counts(scorer.score_request_answer("row", response(parsed=pred), gt)) == (ONE_SHIFT_FIELDS, 0, 3)

    def test_days_are_compared_by_position(self, scorer, response):
        gt = schedule({"2025-04-01": [shift(icon="Ferien")], "2025-04-02": [shift(icon="F-Dienst 1")]})
        pred = schedule({"2025-04-02": [shift(icon="F-Dienst 1")]})
        # The response's only day sits at days[0], so it is compared with 1 April: the
        # date and icon mismatch, and all of days[1] is missing.
        tp, fp, fn = counts(scorer.score_request_answer("row", response(parsed=pred), gt))
        assert (fp, fn) == (2, 2 + 4)
        assert tp == ONE_SHIFT_FIELDS - 2

    def test_unparseable_response_scores_every_field_as_missing(self, scorer, response):
        gt = schedule({"2025-04-01": [shift()]})
        result = scorer.score_request_answer("row", response(parsed=None, text="not json"), gt)
        assert result["true_positives"] == 0
        assert result["false_negatives"] == ONE_SHIFT_FIELDS
        assert result["f1_score"] == 0.0

    def test_f1_is_rounded_to_two_decimals(self, scorer, response):
        gt = schedule({"2025-04-01": [shift(icon="Ferien")], "2025-04-02": [shift(icon="Ferien")]})
        pred = schedule({"2025-04-01": [shift(icon="Ferien")], "2025-04-02": [shift(icon="Krank")]})
        f1 = scorer.score_request_answer("row", response(parsed=pred), gt)["f1_score"]
        assert f1 == round(f1, 2)

    @pytest.mark.parametrize("name", sorted(f[:-5] for f in os.listdir(GROUND_TRUTHS) if f.endswith(".json")))
    def test_every_ground_truth_matches_itself(self, scorer, response, name):
        with open(os.path.join(GROUND_TRUTHS, f"{name}.json"), encoding="utf-8") as f:
            gt = json.load(f)
        result = scorer.score_request_answer(name, response(parsed=copy.deepcopy(gt)), gt)
        assert result["false_positives"] == result["false_negatives"] == 0
        assert result["f1_score"] == 1.0


class TestScoreBenchmark:
    def test_empty(self, scorer):
        assert scorer.score_benchmark([]) == {"f1_micro": 0.0, "f1_macro": 0.0}

    def test_micro_pools_counts_and_macro_averages_rows(self, scorer):
        scores = [
            {"f1_score": 1.0, "true_positives": 1, "false_positives": 0, "false_negatives": 0},
            {"f1_score": 0.0, "true_positives": 0, "false_positives": 3, "false_negatives": 3},
        ]
        result = scorer.score_benchmark(scores)
        assert (result["total_tp"], result["total_fp"], result["total_fn"]) == (1, 3, 3)
        assert result["f1_macro"] == pytest.approx(0.5)
        assert result["f1_micro"] == pytest.approx(0.25)
        assert result["total_instances"] == 2

    def test_entries_without_f1_are_skipped(self, scorer):
        scores = [None, {"error": "x"},
                  {"f1_score": 1.0, "true_positives": 2, "false_positives": 0, "false_negatives": 0}]
        result = scorer.score_benchmark(scores)
        assert result["total_instances"] == 1
        assert result["f1_macro"] == 1.0
