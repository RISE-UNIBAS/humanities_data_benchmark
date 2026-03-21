"""
Base class for local (non-API) model backends.

Each backend is responsible for:
- Loading its model (in __init__)
- Running inference (run)
- Returning a fully populated LLMResponse so that scoring, saving, and
  cost/token accounting downstream work without modification

Token counts are approximated — see _build_usage().
"""

import json
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from ai_client import LLMResponse, Usage


@dataclass
class LocalRequest:
    """All inputs needed by a local backend to produce a response."""
    prompt: str
    images: List[str] = field(default_factory=list)
    files: List[str] = field(default_factory=list)
    dataclass: Optional[type] = None   # Pydantic model for structured output (may be None)
    temperature: float = 0.5


class LocalBackend(ABC):
    """
    Abstract base class for local model backends.

    Subclasses must implement run(). They may optionally override
    parse_response() for model-specific JSON extraction logic.

    RETURNS_ORIGINAL_COORDS:
        True  — the backend's detection boxes are in the *original* input image
                coordinate space (e.g. YOLO, which undoes its own letterboxing).
        False — boxes are in the *inference* image space after any internal
                resize (e.g. the contour backend, which resizes via PIL first).
    """

    RETURNS_ORIGINAL_COORDS: bool = False

    # ------------------------------------------------------------------ #
    # Structured output parsing                                            #
    # ------------------------------------------------------------------ #

    def parse_response(self, text: str, dataclass: Optional[type] = None) -> Optional[dict]:
        """
        Extract a structured dict/list from the model's raw text output.

        Default strategy (in order):
          1. Direct json.loads on the full text.
          2. Extract the first ```json ... ``` fenced block.
          3. Extract the first bare { ... } or [ ... ] span.

        Override in a subclass when the model's output format is known and
        the default heuristics are insufficient or unnecessarily expensive.

        Args:
            text:      Raw text returned by the model.
            dataclass: The expected Pydantic model (ignored by default, but
                       available for subclasses that want to guide parsing).

        Returns:
            Parsed dict/list, or None if no valid JSON could be extracted.
        """
        text = text.strip()

        # 1. Direct parse
        try:
            return json.loads(text)
        except (json.JSONDecodeError, ValueError):
            pass

        # 2. Fenced ```json block
        match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except (json.JSONDecodeError, ValueError):
                pass

        # 3. First JSON object or array
        match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except (json.JSONDecodeError, ValueError):
                pass

        return None

    # ------------------------------------------------------------------ #
    # Token estimation                                                     #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _estimate_tokens_text(text: str) -> int:
        """Approximate token count from a text string (~4 chars/token for Latin text)."""
        return max(1, len(text) // 4)

    @staticmethod
    def _estimate_tokens_image(image_path: str) -> int:
        """
        Approximate token count from image dimensions.

        Heuristic: (width * height) / 750 — roughly calibrated for the kind
        of document images (A4/letter scans at 150–300 dpi) used in this project.
        Falls back to 256 if PIL is unavailable or the image cannot be opened.
        """
        try:
            from PIL import Image
            with Image.open(image_path) as img:
                w, h = img.size
            return max(1, (w * h) // 750)
        except Exception:
            return 256

    def _build_usage(self, input_text: str, output_text: str, image_paths: List[str]) -> Usage:
        """Build a Usage object from estimated token counts. Cost is $0 for local models."""
        input_tokens = self._estimate_tokens_text(input_text)
        for img in image_paths:
            input_tokens += self._estimate_tokens_image(img)
        output_tokens = self._estimate_tokens_text(output_text)
        return Usage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            cached_tokens=None,
            cache_creation_tokens=0,
            cache_read_tokens=0,
            input_cost_usd=0.0,
            output_cost_usd=0.0,
            estimated_cost_usd=0.0,
        )

    # ------------------------------------------------------------------ #
    # Inference                                                            #
    # ------------------------------------------------------------------ #

    @abstractmethod
    def run(self, request: LocalRequest) -> LLMResponse:
        """
        Execute inference and return a fully populated LLMResponse.

        Implementors must populate at minimum:
          text, model, provider, finish_reason, usage, raw_response,
          duration, timestamp, parsed
        """
        pass