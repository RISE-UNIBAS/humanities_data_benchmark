"""Scoring tests for magazine_pages.

Predicted boxes are matched 1:1 to ground-truth boxes, greedily by IoU, highest first; a
pair counts at IoU >= 0.5. Per page: TP = matched pairs, FP = unmatched predictions,
FN = unmatched ground-truth boxes. score_benchmark macro-averages the per-page values.
"""
import importlib
import json
import os

import pytest

module = importlib.import_module("benchmarks.magazine_pages.benchmark")
MagazinePages = module.MagazinePages

GROUND_TRUTHS = os.path.join(os.path.dirname(__file__), "..", "benchmarks", "magazine_pages", "ground_truths")


def ads(*boxes):
    return {"advertisements": [{"box": list(b)} for b in boxes]}


@pytest.fixture
def scorer(make_scorer):
    return make_scorer(MagazinePages)


def counts(result):
    return result["true_positives"], result["false_positives"], result["false_negatives"]


class TestIou:
    @pytest.mark.parametrize("a,b,expected", [
        ([0, 0, 10, 10], [0, 0, 10, 10], 1.0),
        ([0, 0, 10, 10], [0, 0, 10, 5], 0.5),
        ([0, 0, 10, 10], [20, 20, 30, 30], 0.0),
        ([0, 0, 10, 10], [5, 0, 15, 10], 50 / 150),
    ])
    def test_iou(self, a, b, expected):
        assert module._iou(a, b) == pytest.approx(expected)


class TestMatchBoxes:
    def test_threshold_is_inclusive(self):
        assert module._match_boxes([[0, 0, 10, 10]], [[0, 0, 10, 5]]) == [(0, 0, 0.5)]
        assert module._match_boxes([[0, 0, 10, 10]], [[0, 0, 10, 4]]) == []

    def test_each_box_is_matched_once(self):
        # Two predictions overlap the same ground-truth box; only the better one counts.
        matches = module._match_boxes([[0, 0, 10, 10]], [[0, 0, 10, 9], [0, 0, 10, 10]])
        assert matches == [(0, 1, 1.0)]

    def test_highest_iou_is_assigned_first(self):
        gt = [[0, 0, 10, 10], [0, 0, 10, 8]]
        pred = [[0, 0, 10, 8]]
        assert module._match_boxes(gt, pred) == [(1, 0, 1.0)]


class TestExtractBoxes:
    def test_llm_and_backend_shapes(self):
        assert module._extract_boxes(ads([1, 2, 3, 4])) == [[1, 2, 3, 4]]
        assert module._extract_boxes({"detections": [{"box": [1, 2, 3, 4], "score": 0.9}]}) == [[1, 2, 3, 4]]

    @pytest.mark.parametrize("value", [None, [], "text", {"advertisements": []}, {"advertisements": [{"x": 1}]}])
    def test_unusable_shapes_give_no_boxes(self, value):
        assert module._extract_boxes(value) == []


class TestScoreRequestAnswer:
    def test_perfect_match(self, scorer, response):
        gt = ads([0, 0, 10, 10], [20, 20, 30, 30])
        result = scorer.score_request_answer("p", response(parsed=gt), gt)
        assert counts(result) == (2, 0, 0)
        assert (result["f1"], result["mean_iou"]) == (1.0, 1.0)

    def test_miss_and_hallucination(self, scorer, response):
        gt = ads([0, 0, 10, 10], [20, 20, 30, 30])
        pred = ads([0, 0, 10, 10], [50, 50, 60, 60])
        result = scorer.score_request_answer("p", response(parsed=pred), gt)
        assert counts(result) == (1, 1, 1)
        assert result["f1"] == 0.5
        assert result["field_scores"]["box 1"]["response"] is None
        assert result["field_scores"]["unmatched prediction 1"]["ground_truth"] is None

    def test_unparseable_response_is_a_miss(self, scorer, response):
        gt = ads([0, 0, 10, 10])
        result = scorer.score_request_answer("p", response(parsed=None, text="prose"), gt)
        assert counts(result) == (0, 0, 1)
        assert result["f1"] == 0.0

    def test_nothing_expected_and_nothing_found_is_perfect(self, scorer, response):
        result = scorer.score_request_answer("p", response(parsed=ads()), ads())
        assert counts(result) == (0, 0, 0)
        assert result["f1"] == 1.0

    def test_unparseable_answers_are_scored(self):
        assert MagazinePages.score_unparseable_as_miss is True

    @pytest.mark.parametrize("box", [None, 1, "x", [], [1, 2, 3], [[0, 0], [10, 10]], ["0", "0", "10", "10"],
                                     [True, 0, 10, 10]])
    def test_a_box_that_is_not_four_numbers_is_a_false_positive(self, scorer, response, box):
        gt = ads([0, 0, 10, 10])
        pred = {"advertisements": [{"box": [0, 0, 10, 10]}, {"box": box}]}
        assert counts(scorer.score_request_answer("p", response(parsed=pred), gt)) == (1, 1, 0)

    @pytest.mark.parametrize("name", sorted(f[:-5] for f in os.listdir(GROUND_TRUTHS) if f.endswith(".json")))
    def test_every_ground_truth_matches_itself(self, scorer, response, name):
        with open(os.path.join(GROUND_TRUTHS, f"{name}.json"), encoding="utf-8") as f:
            gt = json.load(f)
        result = scorer.score_request_answer(name, response(parsed=gt), gt)
        assert result["false_positives"] == result["false_negatives"] == 0
        assert result["f1"] == 1.0


class TestScoreBenchmark:
    def test_empty(self, scorer):
        assert scorer.score_benchmark([]) == {"f1": 0.0, "precision": 0.0, "recall": 0.0, "mean_iou": 0.0}

    def test_macro_average_of_pages(self, scorer):
        pages = [
            {"f1": 1.0, "precision": 1.0, "recall": 1.0, "mean_iou": 0.9,
             "true_positives": 2, "false_positives": 0, "false_negatives": 0},
            {"f1": 0.0, "precision": 0.0, "recall": 0.0, "mean_iou": 0.0,
             "true_positives": 0, "false_positives": 1, "false_negatives": 3},
        ]
        result = scorer.score_benchmark(pages)
        assert (result["f1"], result["mean_iou"], result["num_pages"]) == (0.5, 0.45, 2)
        assert (result["true_positives"], result["false_positives"], result["false_negatives"]) == (2, 1, 3)
