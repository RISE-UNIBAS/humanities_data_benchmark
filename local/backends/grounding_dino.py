"""
GroundingDINO local backend.

GroundingDINO is a zero-shot, text-prompted object detector. It accepts
natural-language phrases as detection targets and returns bounding boxes
with confidence scores — the same conceptual interface as SAM3, but built
on standard HuggingFace Transformers and PyTorch, making it fully
cross-platform (Windows, Linux, macOS) with automatic NVIDIA GPU support.

Requirements:
    pip install transformers torch torchvision Pillow

Model weights (~700 MB for tiny, ~800 MB for base) are downloaded from
HuggingFace on first use and cached in ~/.cache/huggingface/.

Available model IDs (set MODEL_ID on a subclass to override):
    IDEA-Research/grounding-dino-tiny   — faster, good for testing
    IDEA-Research/grounding-dino-base   — more accurate

TEXT_PROMPTS follow GroundingDINO's convention: short noun phrases.
The backend joins them with " . " separators as the model expects.

Usage in benchmarks_tests.csv:
    provider = grounding_dino_local
    model    = grounding-dino-tiny     (informational; MODEL_ID controls the actual model)
"""

import json
import time
from datetime import datetime
from typing import List, Optional

import torch
from PIL import Image
from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor

from ai_client import LLMResponse
from local.backends.base import LocalBackend, LocalRequest


class GroundingDinoBackend(LocalBackend):
    """
    Local backend for GroundingDINO (zero-shot text-prompted object detection).

    Override TEXT_PROMPTS in a benchmark-specific subclass to control what
    is detected. Prompts should be short noun phrases — the same kind of
    labels you would pass to SAM3.

    Example::

        class NewspaperAdsBackend(GroundingDinoBackend):
            TEXT_PROMPTS = [
                "advertisement",
                "company logo",
                "price list",
                "bordered box with text",
            ]
    """

    MODEL_ID: str = "IDEA-Research/grounding-dino-tiny"

    # Text labels to detect. Joined as "label1 . label2 . label3 ." at runtime.
    TEXT_PROMPTS: List[str] = ["advertisement"]

    # Minimum confidence for a box to be kept.
    # box_threshold filters on overall detection confidence;
    # text_threshold filters on label-text alignment confidence.
    BOX_THRESHOLD: float = 0.35
    TEXT_THRESHOLD: float = 0.25

    # Resize images so the long edge does not exceed this value before
    # running inference. GroundingDINO internally caps at 1333 px anyway;
    # setting this lower speeds up CPU runs.
    MAX_LONG_EDGE: int = 1333

    def __init__(self):
        self.processor = AutoProcessor.from_pretrained(self.MODEL_ID)
        self.model = AutoModelForZeroShotObjectDetection.from_pretrained(self.MODEL_ID)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = self.model.to(self.device)
        self.model.eval()

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _text_query(self) -> str:
        """Build the period-separated prompt string GroundingDINO expects."""
        return " . ".join(self.TEXT_PROMPTS) + " ."

    def _resize(self, image: Image.Image) -> Image.Image:
        w, h = image.size
        if max(w, h) > self.MAX_LONG_EDGE:
            scale = self.MAX_LONG_EDGE / max(w, h)
            image = image.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        return image

    def _detect_image(self, image_path: str) -> List[dict]:
        """Run detection on a single image and return a list of detections."""
        image = Image.open(image_path).convert("RGB")
        image = self._resize(image)
        text = self._text_query()

        inputs = self.processor(images=image, text=text, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)

        # post_process returns one result dict per image; filter by threshold manually
        # (box_threshold / text_threshold kwargs were removed in newer transformers versions)
        results = self.processor.post_process_grounded_object_detection(
            outputs,
            inputs["input_ids"],
            target_sizes=[image.size[::-1]],  # (height, width)
        )[0]

        detections = []
        for box, score, label in zip(results["boxes"], results["scores"], results["labels"]):
            score_val = float(score)
            if score_val >= self.BOX_THRESHOLD:
                detections.append({
                    "label": label,
                    "box": [round(float(v), 2) for v in box.tolist()],  # xyxy, absolute pixels
                    "score": round(score_val, 4),
                })

        return detections

    # ------------------------------------------------------------------ #
    # parse_response override                                              #
    # ------------------------------------------------------------------ #

    def parse_response(self, text: str, dataclass: Optional[type] = None) -> Optional[dict]:
        """Detection output is already JSON; direct parse suffices."""
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
            model=self.MODEL_ID,
            provider="grounding_dino_local",
            finish_reason="stop",
            usage=usage,
            raw_response=raw_output,
            duration=duration,
            timestamp=datetime.now(),
            parsed=parsed,
        )