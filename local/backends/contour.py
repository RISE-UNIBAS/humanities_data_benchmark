"""
OpenCV contour-based bordered-region detector.

Detects rectangular regions defined by printed/ruled borders in document
images — exactly the kind of bordered advertisement boxes found in
historical newspapers and trade magazines. No ML model required.

Works by finding edges (Canny), dilating to close minor gaps in ruled
lines, locating contours, filtering for roughly rectangular shapes in a
sensible size range, and applying NMS to remove duplicates.

Requirements:
    pip install opencv-python-headless   # or opencv-python for GUI tools

Because this is purely rule-based, it is fast, deterministic, and produces
no false positives on plain text columns (which have no enclosing border).
Its weakness: ads without a printed border (e.g. white-space-separated
blocks) will be missed.

Usage in benchmarks_tests.csv:
    provider = contour_local
    model    = opencv-contour   (informational only)
"""

import json
import time
from datetime import datetime
from typing import List, Optional

import cv2
import numpy as np
from PIL import Image

from ai_client import LLMResponse
from local.backends.base import LocalBackend, LocalRequest


class ContourDetectionBackend(LocalBackend):
    """
    Local backend for contour-based bordered-region detection.

    All thresholds are class variables — override in a subclass to tune
    for a specific document type without changing shared defaults.
    """

    # Work at high resolution so thin ruled borders are preserved.
    # Lower this (e.g. 1333) to trade accuracy for speed on CPU.
    MAX_LONG_EDGE: int = 2000

    # A detection must cover at least this fraction of total image area.
    MIN_AREA_RATIO: float = 0.005   # 0.5 % — removes tiny noise contours

    # A detection must cover at most this fraction of total image area.
    # Keeps out the page-border contour that encloses everything.
    MAX_AREA_RATIO: float = 0.75

    # Minimum ratio of contour area to its bounding-box area.
    # 1.0 = perfect rectangle; lower values allow slightly irregular shapes.
    MIN_RECTANGULARITY: float = 0.65

    # Polygon approximation tolerance as a fraction of contour arc length.
    APPROX_EPSILON_RATIO: float = 0.02

    # Canny edge-detection thresholds.
    CANNY_LOW: int = 50
    CANNY_HIGH: int = 150

    # Dilation iterations to close small gaps in ruled borders.
    DILATE_ITERATIONS: int = 2

    # IoU threshold for non-maximum suppression.
    NMS_IOU_THRESHOLD: float = 0.5

    # Boxes are converted back to original image space before returning.
    RETURNS_ORIGINAL_COORDS: bool = True

    def __init__(self):
        pass  # cv2 import at module level is sufficient

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _resize(self, image: Image.Image) -> Image.Image:
        w, h = image.size
        if max(w, h) > self.MAX_LONG_EDGE:
            scale = self.MAX_LONG_EDGE / max(w, h)
            image = image.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        return image

    def _detect_image(self, image_path: str) -> List[dict]:
        img_pil = Image.open(image_path).convert("RGB")
        orig_w = img_pil.size[0]
        img_pil = self._resize(img_pil)
        w, h = img_pil.size
        scale = w / orig_w if orig_w else 1.0
        image_area = w * h

        # PIL → OpenCV grayscale
        gray = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2GRAY)

        # Edge detection with slight blur to reduce scan noise
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        edges = cv2.Canny(blurred, self.CANNY_LOW, self.CANNY_HIGH)

        # Dilate to bridge minor gaps in printed borders
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        edges = cv2.dilate(edges, kernel, iterations=self.DILATE_ITERATIONS)

        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        candidates = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            area_ratio = area / image_area
            if not (self.MIN_AREA_RATIO <= area_ratio <= self.MAX_AREA_RATIO):
                continue

            # Approximate contour to polygon; keep only near-rectangles
            epsilon = self.APPROX_EPSILON_RATIO * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            if not (4 <= len(approx) <= 8):
                continue

            x, y, bw, bh = cv2.boundingRect(cnt)
            box_area = bw * bh
            rectangularity = area / box_area if box_area > 0 else 0.0
            if rectangularity < self.MIN_RECTANGULARITY:
                continue

            candidates.append({
                "label": "bordered region",
                "box": [float(x), float(y), float(x + bw), float(y + bh)],
                "score": round(float(rectangularity), 4),
            })

        # Sort largest-first, then suppress overlapping duplicates
        candidates.sort(
            key=lambda d: (d["box"][2] - d["box"][0]) * (d["box"][3] - d["box"][1]),
            reverse=True,
        )
        kept = self._nms(candidates, self.NMS_IOU_THRESHOLD)

        # Convert boxes from inference space back to original image coordinates
        if scale != 1.0:
            for det in kept:
                det["box"] = [round(v / scale, 2) for v in det["box"]]
        return kept

    @staticmethod
    def _nms(detections: List[dict], iou_threshold: float) -> List[dict]:
        kept = []
        for det in detections:
            x0, y0, x1, y1 = det["box"]
            suppress = False
            for kept_det in kept:
                kx0, ky0, kx1, ky1 = kept_det["box"]
                inter_area = (
                    max(0.0, min(x1, kx1) - max(x0, kx0))
                    * max(0.0, min(y1, ky1) - max(y0, ky0))
                )
                union_area = (x1-x0)*(y1-y0) + (kx1-kx0)*(ky1-ky0) - inter_area
                if union_area > 0 and inter_area / union_area > iou_threshold:
                    suppress = True
                    break
            if not suppress:
                kept.append(det)
        return kept

    # ------------------------------------------------------------------ #
    # parse_response override                                              #
    # ------------------------------------------------------------------ #

    def parse_response(self, text: str, dataclass: Optional[type] = None) -> Optional[dict]:
        try:
            return json.loads(text)
        except (json.JSONDecodeError, ValueError):
            return super().parse_response(text, dataclass)

    # ------------------------------------------------------------------ #
    # run                                                                  #
    # ------------------------------------------------------------------ #

    def run(self, request: LocalRequest) -> LLMResponse:
        t0 = time.time()

        all_detections: List[dict] = []
        for image_path in request.images:
            all_detections.extend(self._detect_image(image_path))

        raw_output = {"detections": all_detections}
        text = json.dumps(raw_output, ensure_ascii=False)
        parsed = self.parse_response(text, request.dataclass)
        duration = time.time() - t0
        usage = self._build_usage(request.prompt, text, request.images)

        return LLMResponse(
            text=text,
            model="opencv-contour",
            provider="contour_local",
            finish_reason="stop",
            usage=usage,
            raw_response=raw_output,
            duration=duration,
            timestamp=datetime.now(),
            parsed=parsed,
        )