"""Benchmark implementation for magazine page advertisement detection.

Evaluates a model's ability to locate advertisements on magazine pages by
comparing predicted bounding boxes to manually verified ground truth boxes.

Scoring approach
----------------
Each predicted box is matched 1:1 to a ground truth box using greedy
assignment by IoU (highest IoU first).  A match is accepted when
IoU ≥ IOU_THRESHOLD (default 0.5, the PASCAL VOC standard).

Per-image metrics
    true_positives  : predicted boxes matched to a GT box at ≥ threshold
    false_positives : predicted boxes that matched nothing (hallucinations)
    false_negatives : GT boxes that no prediction covered (missed ads)
    precision       : TP / (TP + FP)  — how many predictions are correct
    recall          : TP / (TP + FN)  — how many GT ads were found
    f1              : harmonic mean of precision and recall (headline score)
    mean_iou        : average IoU over matched pairs (quality of localisation)

Benchmark-level metrics are the macro-averages of the per-image values.

Ground truth format  (benchmarks/magazine_pages/ground_truths/<stem>.json):
    {"advertisements": [{"box": [x0, y0, x1, y1]}, ...]}   — same shape as LLM output

Response format expected from models / local backends:
    {"detections": [{"box": [x0, y0, x1, y1], ...}, ...]}   # local backends
    {"advertisements": [{"box": [x0, y0, x1, y1]}, ...]}    # LLM dataclass
    All boxes must be in original-image pixel coordinates.
"""

import os
from typing import List, Optional, Tuple, Dict

from PIL import Image

from scripts.benchmark_base import Benchmark

IOU_THRESHOLD = 0.5


# ---------------------------------------------------------------------------
# Pure helper functions (no state, easy to unit-test)
# ---------------------------------------------------------------------------

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


def _match_boxes(
    gt_boxes: list,
    pred_boxes: list,
    threshold: float = IOU_THRESHOLD,
) -> List[Tuple[int, int, float]]:
    """
    Greedy 1:1 matching of predicted boxes to ground truth boxes.

    Builds all (gt_idx, pred_idx, iou) triples where iou ≥ threshold,
    sorts by iou descending, then greedily assigns each gt/pred index at
    most once.

    Returns list of (gt_idx, pred_idx, iou) for accepted matches.
    """
    if not gt_boxes or not pred_boxes:
        return []
    candidates = []
    for i, gt in enumerate(gt_boxes):
        for j, pred in enumerate(pred_boxes):
            score = _iou(gt, pred)
            if score >= threshold:
                candidates.append((score, i, j))
    candidates.sort(reverse=True)
    matched_gt:   set = set()
    matched_pred: set = set()
    matches = []
    for score, i, j in candidates:
        if i not in matched_gt and j not in matched_pred:
            matches.append((i, j, score))
            matched_gt.add(i)
            matched_pred.add(j)
    return matches


def _extract_boxes(response: Optional[dict]) -> list:
    """
    Pull a flat list of [x0, y0, x1, y1] boxes from various response shapes.

    Handles:
      {"detections": [{"box": [...], ...}, ...]}  — local backends
      {"advertisements": [{"box": [...]}, ...]}   — LLM dataclass output
    """
    if not response or not isinstance(response, dict):
        return []
    for key in ("detections", "advertisements"):
        items = response.get(key)
        if isinstance(items, list) and items:
            boxes = [item["box"] for item in items if isinstance(item, dict) and "box" in item]
            if boxes:
                return boxes
    return []


# ---------------------------------------------------------------------------
# Benchmark class
# ---------------------------------------------------------------------------

class MagazinePages(Benchmark):
    """Benchmark for magazine page advertisement detection."""

    def get_prompt_kwargs(self, basename: str, filenames: List[str]) -> Dict:
        """Return image dimensions so the prompt can state the coordinate space."""
        image_path = os.path.join(filenames[0])
        with Image.open(image_path) as img:
            width, height = img.size
        return {"width": width, "height": height}

    def score_request_answer(
        self,
        image_name: str,
        response,
        ground_truth,
    ) -> dict:
        """
        Score one page's detections against ground truth.

        Args:
            image_name:   Filename of the image (informational).
            response:     Parsed model output (see module docstring for format).
            ground_truth: GT dict {"advertisements": [{"box": [...]}, ...]}.

        Returns:
            Dict with f1, precision, recall, mean_iou, tp, fp, fn counts.
        """
        pred_boxes = _extract_boxes(response.parsed)
        gt_boxes   = _extract_boxes(ground_truth)

        # Perfect score when both are empty (model correctly predicted nothing)
        if not gt_boxes and not pred_boxes:
            return {
                "f1":              1.0,
                "precision":       1.0,
                "recall":          1.0,
                "mean_iou":        1.0,
                "true_positives":  0,
                "false_positives": 0,
                "false_negatives": 0,
                "iou_threshold":   IOU_THRESHOLD,
            }

        matches = _match_boxes(gt_boxes, pred_boxes, IOU_THRESHOLD)
        tp = len(matches)
        fp = len(pred_boxes) - tp
        fn = len(gt_boxes)   - tp

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0 else 0.0
        )
        mean_iou = sum(m[2] for m in matches) / len(matches) if matches else 0.0

        return {
            "f1":              round(f1, 3),
            "precision":       round(precision, 3),
            "recall":          round(recall, 3),
            "mean_iou":        round(mean_iou, 3),
            "true_positives":  tp,
            "false_positives": fp,
            "false_negatives": fn,
            "iou_threshold":   IOU_THRESHOLD,
        }

    def score_benchmark(self, all_scores: list) -> dict:
        """
        Macro-average of per-image scores across all pages.

        Args:
            all_scores: List of dicts returned by score_request_answer.

        Returns:
            Dict with averaged f1, precision, recall, mean_iou and totals.
        """
        if not all_scores:
            return {"f1": 0.0, "precision": 0.0, "recall": 0.0, "mean_iou": 0.0}

        n = len(all_scores)
        return {
            "f1":              round(sum(s["f1"]        for s in all_scores) / n, 3),
            "precision":       round(sum(s["precision"] for s in all_scores) / n, 3),
            "recall":          round(sum(s["recall"]    for s in all_scores) / n, 3),
            "mean_iou":        round(sum(s["mean_iou"]  for s in all_scores) / n, 3),
            "true_positives":  sum(s["true_positives"]  for s in all_scores),
            "false_positives": sum(s["false_positives"] for s in all_scores),
            "false_negatives": sum(s["false_negatives"] for s in all_scores),
            "num_pages":       n,
        }