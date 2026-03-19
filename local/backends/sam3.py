"""
SAM 3 local backend.

SAM 3 is a Segment Anything Model (MLX port for Apple Silicon) that performs
text-prompted object detection on images, returning bounding boxes and
confidence scores — not natural language text.

Requirements:
    pip install sam3          # https://github.com/Deekshith-Dade/mlx_sam3
    Hardware: Apple Silicon (macOS), model weights ~3.5 GB (auto-downloaded)

Usage in benchmarks_tests.csv:
    provider = sam3_local
    model    = sam3          (informational only, not passed to the library)
    dataclass = <your detection dataclass>

Benchmark subclasses should override TEXT_PROMPTS with domain-specific labels.
The benchmark's prompt.txt is available in request.prompt but is not used for
detection — SAM 3 is prompted with text labels, not instructions.
"""

import json
import time
from datetime import datetime
from typing import List, Optional

from ai_client import LLMResponse
from local.backends.base import LocalBackend, LocalRequest


class Sam3Backend(LocalBackend):
    """
    Local backend for SAM 3 (Segment Anything Model 3, MLX port).

    Detection text prompts are taken from TEXT_PROMPTS. Override this class
    variable in a benchmark-specific subclass to change what is detected.

    Example::

        class MyBenchmarkBackend(Sam3Backend):
            TEXT_PROMPTS = ["advertisement", "company logo", "price list"]
    """

    # Text labels passed to SAM 3 for detection. Override in subclasses.
    TEXT_PROMPTS: List[str] = ["object"]

    # Detection confidence threshold (0.0–1.0). Lower = more detections.
    CONFIDENCE_THRESHOLD: float = 0.18

    # Images are downscaled so the long edge does not exceed this value.
    MAX_LONG_EDGE: int = 1024

    def __init__(self):
        from sam3 import build_sam3_image_model
        from sam3.model.sam3_image_processor import Sam3Processor

        model = build_sam3_image_model()
        self.processor = Sam3Processor(model, confidence_threshold=self.CONFIDENCE_THRESHOLD)

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _resize(self, image):
        w, h = image.size
        long_edge = max(w, h)
        if long_edge > self.MAX_LONG_EDGE:
            from PIL import Image
            scale = self.MAX_LONG_EDGE / long_edge
            image = image.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        return image

    def _detect_image(self, image_path: str) -> List[dict]:
        """Run all TEXT_PROMPTS against a single image and collect detections."""
        from PIL import Image

        image = Image.open(image_path).convert("RGB")
        image = self._resize(image)
        state = self.processor.set_image(image)

        detections = []
        for label in self.TEXT_PROMPTS:
            self.processor.reset_all_prompts(state)
            state = self.processor.set_text_prompt(label, state)
            boxes = state.get("boxes", [])
            scores = state.get("scores", [])
            for box, score in zip(boxes, scores):
                detections.append({
                    "label": label,
                    "box": [round(float(v), 2) for v in box],
                    "score": round(float(score), 4),
                })

        return detections

    # ------------------------------------------------------------------ #
    # parse_response override                                              #
    # ------------------------------------------------------------------ #

    def parse_response(self, text: str, dataclass: Optional[type] = None) -> Optional[dict]:
        """
        Detection output is already serialised JSON, so a direct parse suffices.
        Falls back to the base class heuristics on failure.
        """
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
            detections = self._detect_image(image_path)
            all_detections.extend(detections)

        raw_output = {"detections": all_detections}
        text = json.dumps(raw_output, ensure_ascii=False)
        parsed = self.parse_response(text, request.dataclass)
        duration = time.time() - t0
        usage = self._build_usage(request.prompt, text, request.images)

        return LLMResponse(
            text=text,
            model="sam3",
            provider="sam3_local",
            finish_reason="stop",
            usage=usage,
            raw_response=raw_output,
            duration=duration,
            timestamp=datetime.now(),
            parsed=parsed,
        )