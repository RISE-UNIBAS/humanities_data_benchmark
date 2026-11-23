"""Benchmark implementation for entry localisation in the Basel address book of 1890.

Models receive one page of the business directory ("Verzeichnis der Einwohner nach ihren
Geschäften und Gewerben") and return one bounding box per directory entry. An entry may run
over several printed lines; its box covers all of them. A cross-reference standing in place of
entries ("(Siehe Konditoren.)") is an entry; headings, notes, legends, footnotes, running heads
and page numbers are not.

Scoring approach
----------------
Predicted boxes are matched 1:1 to ground-truth boxes, greedily by IoU, highest first.
A pair counts at IoU >= IOU_THRESHOLD (0.5). Entries are narrow (a one-line entry is about 1.5 % of the
page height), so a box that drifts by one line already falls below the threshold. A second
pass at STRICT_IOU_THRESHOLD (0.75) shows how tightly the boxes fit.

Per-page metrics
    true_positives / false_positives / false_negatives at IoU 0.5
    precision, recall, f1        at IoU 0.5 (headline score: f1)
    f1_strict                    at IoU 0.75
    mean_iou                     over the pairs matched at 0.5
    count_error                  |predicted - expected| / expected

Benchmark-level metrics are macro-averages over the pages, plus micro precision, recall and
F1 over all boxes (pages hold 38 to 105 entries, so the two can differ).

Ground truth format (ground_truths/<stem>.json):
    {"entries": [{"box": [x0, y0, x1, y1]}, ...]}   pixel coordinates of the image in images/
"""

import math
import os
from typing import Dict, List, Optional, Tuple

from PIL import Image

from scripts.benchmark_base import Benchmark

IOU_THRESHOLD = 0.5
STRICT_IOU_THRESHOLD = 0.75


def _iou(a: list, b: list) -> float:
    """Return Intersection-over-Union of two [x0, y0, x1, y1] boxes."""
    ix0 = max(a[0], b[0])
    iy0 = max(a[1], b[1])
    ix1 = min(a[2], b[2])
    iy1 = min(a[3], b[3])
    inter = max(0.0, ix1 - ix0) * max(0.0, iy1 - iy0)
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def _match_boxes(gt_boxes: list, pred_boxes: list,
                 threshold: float = IOU_THRESHOLD) -> List[Tuple[int, int, float]]:
    """Greedy 1:1 matching; returns (gt_idx, pred_idx, iou) for pairs at or above threshold.

    Predictions that are None (malformed) never match.
    """
    candidates = []
    for i, gt in enumerate(gt_boxes):
        for j, pred in enumerate(pred_boxes):
            if pred is None:
                continue
            score = _iou(gt, pred)
            if score >= threshold:
                candidates.append((score, i, j))
    candidates.sort(key=lambda c: (-c[0], c[1], c[2]))
    matched_gt, matched_pred, matches = set(), set(), []
    for score, i, j in candidates:
        if i not in matched_gt and j not in matched_pred:
            matches.append((i, j, score))
            matched_gt.add(i)
            matched_pred.add(j)
    return matches


def _clean_box(box) -> Optional[list]:
    """Return [x0, y0, x1, y1] with ordered corners, or None unless the box is four finite numbers."""
    if not isinstance(box, (list, tuple)) or len(box) != 4:
        return None
    if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in box):
        return None
    x0, y0, x1, y1 = (float(v) for v in box)
    return [min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)]


def _extract_boxes(data) -> List[Optional[list]]:
    """Boxes from {"entries": [{"box": [...]}, ...]}, or {"detections": [...]} from the local
    backends; a malformed item stays as None.

    Malformed items are kept so they count as false positives instead of disappearing.
    """
    if hasattr(data, "model_dump"):
        data = data.model_dump()
    if not isinstance(data, dict):
        return []
    items = data.get("entries")
    if items is None:
        items = data.get("detections")
    if not isinstance(items, list):
        return []
    return [_clean_box(item.get("box")) if isinstance(item, dict) else None for item in items]


def _prf(tp: int, fp: int, fn: int) -> Tuple[float, float, float]:
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return precision, recall, f1


class AddressBookLayout(Benchmark):
    """Locate every directory entry on a page of the Basel address book of 1890."""

    score_unparseable_as_miss = True

    def get_prompt_kwargs(self, basename: str, filenames: List[str]) -> Dict:
        """Return image dimensions so the prompt can state the coordinate space."""
        with Image.open(filenames[0]) as img:
            width, height = img.size
        return {"width": width, "height": height}

    def score_request_answer(self, image_name: str, response, ground_truth) -> dict:
        parsed = getattr(response, "parsed", None) if response is not None else None
        pred_boxes = _extract_boxes(parsed)
        gt_boxes = [b for b in _extract_boxes(ground_truth) if b is not None]

        matches = _match_boxes(gt_boxes, pred_boxes, IOU_THRESHOLD)
        tp = len(matches)
        fp = len(pred_boxes) - tp
        fn = len(gt_boxes) - tp
        precision, recall, f1 = _prf(tp, fp, fn)

        strict_tp = len(_match_boxes(gt_boxes, pred_boxes, STRICT_IOU_THRESHOLD))
        _, _, f1_strict = _prf(strict_tp, len(pred_boxes) - strict_tp, len(gt_boxes) - strict_tp)

        mean_iou = sum(m[2] for m in matches) / tp if tp else 0.0
        count_error = abs(len(pred_boxes) - len(gt_boxes)) / len(gt_boxes) if gt_boxes else float(len(pred_boxes) > 0)

        # The pairing is the comparison: which prediction was matched to which entry, at what IoU.
        field_scores = {}
        matched_pred = set()
        for gt_i, pred_i, iou in sorted(matches):
            matched_pred.add(pred_i)
            field_scores["entry %d" % gt_i] = {
                "response": pred_boxes[pred_i],
                "ground_truth": gt_boxes[gt_i],
                "score": round(iou, 3),
            }
        matched_gt = {m[0] for m in matches}
        for gt_i, box in enumerate(gt_boxes):
            if gt_i not in matched_gt:
                field_scores["entry %d" % gt_i] = {"response": None, "ground_truth": box, "score": 0.0}
        for pred_i, box in enumerate(pred_boxes):
            if pred_i not in matched_pred:
                field_scores["unmatched prediction %d" % pred_i] = {
                    "response": box, "ground_truth": None, "score": 0.0,
                }

        return {
            "field_scores": field_scores,
            "f1": round(f1, 3),
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1_strict": round(f1_strict, 3),
            "mean_iou": round(mean_iou, 3),
            "count_error": round(count_error, 3),
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "expected_entries": len(gt_boxes),
            "predicted_entries": len(pred_boxes),
            "iou_threshold": IOU_THRESHOLD,
        }

    def score_benchmark(self, all_scores: list) -> dict:
        scores = [s for s in all_scores if isinstance(s, dict) and "f1" in s]
        if not scores:
            return {"f1": 0.0, "precision": 0.0, "recall": 0.0, "f1_strict": 0.0, "mean_iou": 0.0}
        n = len(scores)

        def mean(key):
            return round(sum(s[key] for s in scores) / n, 3)

        tp = sum(s["true_positives"] for s in scores)
        fp = sum(s["false_positives"] for s in scores)
        fn = sum(s["false_negatives"] for s in scores)
        micro_precision, micro_recall, micro_f1 = _prf(tp, fp, fn)
        return {
            "f1": mean("f1"),
            "precision": mean("precision"),
            "recall": mean("recall"),
            "f1_strict": mean("f1_strict"),
            "mean_iou": mean("mean_iou"),
            "count_error": mean("count_error"),
            "f1_micro": round(micro_f1, 3),
            "precision_micro": round(micro_precision, 3),
            "recall_micro": round(micro_recall, 3),
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "num_pages": n,
        }
