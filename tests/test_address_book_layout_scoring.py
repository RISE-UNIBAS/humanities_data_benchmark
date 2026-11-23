"""Scoring tests for address_book_layout.

Predicted entry boxes are matched 1:1 to ground-truth boxes, greedily by IoU, highest first;
a pair counts at IoU >= 0.5 (f1) and, separately, at IoU >= 0.75 (f1_strict). Malformed
predictions count as false positives.
"""
import importlib
import json
import os

import pytest

module = importlib.import_module("benchmarks.address_book_layout.benchmark")
AddressBookLayout = module.AddressBookLayout

GROUND_TRUTHS = os.path.join(os.path.dirname(__file__), "..", "benchmarks",
                             "address_book_layout", "ground_truths")


def entries(*boxes):
    return {"entries": [{"box": list(b)} for b in boxes]}


@pytest.fixture
def scorer(make_scorer):
    return make_scorer(AddressBookLayout)


class TestMatchBoxes:
    def test_threshold_is_inclusive(self):
        assert module._match_boxes([[0, 0, 10, 10]], [[0, 0, 10, 5]]) == [(0, 0, 0.5)]
        assert module._match_boxes([[0, 0, 10, 10]], [[0, 0, 10, 4]]) == []

    def test_each_box_is_matched_once(self):
        matches = module._match_boxes([[0, 0, 10, 10]], [[0, 0, 10, 9], [0, 0, 10, 10]])
        assert matches == [(0, 1, 1.0)]

    def test_malformed_prediction_never_matches(self):
        assert module._match_boxes([[0, 0, 10, 10]], [None]) == []


class TestExtractBoxes:
    def test_corners_are_ordered(self):
        assert module._extract_boxes(entries([10, 10, 0, 0])) == [[0.0, 0.0, 10.0, 10.0]]

    def test_malformed_items_are_kept_as_none(self):
        data = {"entries": [{"box": [1, 2, 3]}, {"box": ["a", 0, 1, 1]}, "x", {"box": [0, 0, 1, 1]}]}
        assert module._extract_boxes(data) == [None, None, None, [0.0, 0.0, 1.0, 1.0]]

    def test_unparseable_response_has_no_boxes(self):
        assert module._extract_boxes(None) == []
        assert module._extract_boxes("not json") == []

    @pytest.mark.parametrize("box", [["0", "0", "10", "10"], [0, 0, float("nan"), 10],
                                     [0, 0, float("inf"), 10], [True, 0, 10, 10]])
    def test_only_finite_numbers_are_coordinates(self, box):
        assert module._extract_boxes(entries(box)) == [None]

    def test_local_backend_detections_are_read(self):
        data = {"detections": [{"box": [0, 0, 10, 10], "score": 0.9}]}
        assert module._extract_boxes(data) == [[0.0, 0.0, 10.0, 10.0]]


class TestScoreRequestAnswer:
    def test_partial_page(self, scorer, response):
        gt = entries([0, 0, 100, 10], [0, 20, 100, 30], [0, 40, 100, 50])
        pred = entries([0, 0, 100, 10], [0, 22, 100, 32], [0, 80, 100, 90])
        result = scorer.score_request_answer("p", response(parsed=pred), gt)
        assert (result["true_positives"], result["false_positives"], result["false_negatives"]) == (2, 1, 1)
        assert result["f1"] == pytest.approx(0.667, abs=1e-3)
        # The shifted box has IoU 8/12 = 0.667: a hit at 0.5, a miss at 0.75.
        assert result["f1_strict"] == pytest.approx(0.333, abs=1e-3)
        assert result["count_error"] == 0.0
        json.dumps(result)

    def test_malformed_prediction_is_false_positive(self, scorer, response):
        gt = entries([0, 0, 10, 10])
        pred = {"entries": [{"box": [0, 0, 10, 10]}, {"box": "oops"}]}
        result = scorer.score_request_answer("p", response(parsed=pred), gt)
        assert (result["true_positives"], result["false_positives"]) == (1, 1)
        assert result["field_scores"]["unmatched prediction 1"]["response"] is None

    def test_quoted_or_nan_coordinates_score_nothing(self, scorer, response):
        gt = entries([0, 0, 10, 10], [0, 20, 10, 30])
        pred = {"entries": [{"box": ["0", "0", "10", "10"]}, {"box": [0, 20, float("nan"), 30]}]}
        result = scorer.score_request_answer("p", response(parsed=pred), gt)
        assert (result["true_positives"], result["false_positives"], result["f1"]) == (0, 2, 0.0)
        json.dumps(result, allow_nan=False)

    def test_detections_score_like_entries(self, scorer, response):
        gt = entries([0, 0, 10, 10], [0, 20, 10, 30])
        pred = {"detections": [{"box": b["box"], "score": 1.0} for b in gt["entries"]]}
        assert scorer.score_request_answer("p", response(parsed=pred), gt)["f1"] == 1.0

    def test_unparseable_is_a_miss(self, scorer, response):
        result = scorer.score_request_answer("p", response(parsed=None), entries([0, 0, 10, 10]))
        assert result["f1"] == 0.0 and result["false_negatives"] == 1


class TestScoreBenchmark:
    def test_macro_and_micro(self, scorer, response):
        page_a = scorer.score_request_answer("a", response(parsed=entries([0, 0, 10, 10])), entries([0, 0, 10, 10]))
        page_b = scorer.score_request_answer(
            "b", response(parsed=entries()), entries([0, 0, 10, 10], [0, 20, 10, 30], [0, 40, 10, 50]))
        result = scorer.score_benchmark([page_a, page_b])
        assert result["f1"] == 0.5
        assert result["recall_micro"] == 0.25
        assert result["num_pages"] == 2


def test_every_ground_truth_scores_perfectly_against_itself(scorer, response):
    files = sorted(f for f in os.listdir(GROUND_TRUTHS) if f.endswith(".json"))
    assert files
    for name in files:
        with open(os.path.join(GROUND_TRUTHS, name), encoding="utf-8") as fh:
            truth = json.load(fh)
        result = scorer.score_request_answer(name, response(parsed=truth), truth)
        assert result["f1"] == 1.0 and result["f1_strict"] == 1.0, name


def test_every_numeric_metric_is_registered_for_export(scorer, response):
    from scripts.export_dataset import metrics as M
    gt = entries([0, 0, 10, 10], [0, 20, 10, 30])
    page = scorer.score_request_answer("p", response(parsed=entries([0, 0, 10, 10], [50, 50, 60, 60])), gt)
    run = scorer.score_benchmark([page])
    for level, scores in (("request", page), ("run", run)):
        for key, value in scores.items():
            if key not in M.NON_METRIC_KEYS and M.numeric(value) is not None:
                assert M.is_known("address_book_layout", level, key), (level, key)
    assert M.is_known("address_book_layout", "field", "score")
