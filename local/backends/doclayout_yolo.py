"""
DocLayout-YOLO local backend.

Uses a YOLO model fine-tuned on document layout benchmarks (DocStructBench)
to detect structural regions: title, text, figure, table, and more.
For advertisement detection, the "figure" class is the most relevant —
it catches image-based ads. Text-only ads in bordered boxes may appear
as "plain text" or "abandoned".

Requirements:
    pip install doclayout-yolo

Model weights (~50 MB) are downloaded from HuggingFace on first use.

Available classes (DocStructBench):
    title, plain text, abandoned, figure, figure_caption,
    table, table_caption, table_footnote, isolate_formula, formula_caption

Usage in benchmarks_tests.csv:
    provider = doclayout_yolo_local
    model    = doclayout-yolo-docstructbench   (informational only)
"""

import json
import time
from datetime import datetime
from typing import List, Optional

from doclayout_yolo import YOLOv10
from huggingface_hub import hf_hub_download

from ai_client import LLMResponse
from local.backends.base import LocalBackend, LocalRequest


class DocLayoutYoloBackend(LocalBackend):
    """
    Local backend for DocLayout-YOLO (document layout detection).

    Override INCLUDE_CLASSES to restrict output to specific region types.

    Example::

        class MagazineAdsBackend(DocLayoutYoloBackend):
            INCLUDE_CLASSES = ["figure", "abandoned"]
    """

    MODEL_REPO = "juliozhao/DocLayout-YOLO-DocStructBench"
    MODEL_FILE = "doclayout_yolo_docstructbench_imgsz1024.pt"

    # YOLO undoes its internal letterboxing — boxes come back in original image space.
    RETURNS_ORIGINAL_COORDS: bool = True

    # Set to a list of class names to keep only those; None = keep all.
    INCLUDE_CLASSES: Optional[List[str]] = None

    CONFIDENCE_THRESHOLD: float = 0.2
    IMGSZ: int = 1024

    def __init__(self):
        model_path = hf_hub_download(repo_id=self.MODEL_REPO, filename=self.MODEL_FILE)
        self.model = YOLOv10(model_path)

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _detect_image(self, image_path: str) -> List[dict]:
        results = self.model.predict(
            image_path,
            imgsz=self.IMGSZ,
            conf=self.CONFIDENCE_THRESHOLD,
            verbose=False,
        )[0]

        detections = []
        for box in results.boxes:
            label = results.names[int(box.cls)]
            if self.INCLUDE_CLASSES is not None and label not in self.INCLUDE_CLASSES:
                continue
            detections.append({
                "label": label,
                "box": [round(float(v), 2) for v in box.xyxy[0].tolist()],
                "score": round(float(box.conf), 4),
            })

        detections.sort(key=lambda d: d["score"], reverse=True)
        return detections

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
            model=self.MODEL_FILE,
            provider="doclayout_yolo_local",
            finish_reason="stop",
            usage=usage,
            raw_response=raw_output,
            duration=duration,
            timestamp=datetime.now(),
            parsed=parsed,
        )
