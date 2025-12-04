"""Benchmark implementation for Book Advert XML files (malformed) from Avisblatt.
"""
from ai_client import LLMResponse
from rapidfuzz import fuzz

from scripts.benchmark_base import Benchmark


class BookAdvertXml(Benchmark):
    """Benchmark for Book Advert XML files (malformed) from Avisblatt."""

    def score_request_answer(self, image_name: str, response: LLMResponse, ground_truth: dict) -> dict:
        """Score a single request against ground truth."""
        if not response.parsed or "fixed_xml" not in response.parsed:
            return {"score": 0.0, "message": "No valid response"}

        fixed_xml = (response.parsed.get("fixed_xml", "")
                     .replace("\n", "")
                     .replace("\r", "")
                     .replace(" ", ""))

        gt_xml = (ground_truth.get("fixed_xml", "")
                  .replace("\n", "")
                  .replace("\r", "")
                  .replace(" ", ""))

        score = fuzz.ratio(fixed_xml, gt_xml)

        return {"fuzzy": score}

    def score_benchmark(self, all_scores: list) -> dict:
        """Aggregate scores from all requests."""
        if not all_scores:
            return {"fuzzy": 0.0}

        # Calculate average score
        avg_score = sum(s.get("fuzzy", 0.0) for s in all_scores) / len(all_scores)

        return {
            "fuzzy": avg_score,
            "n": len(all_scores)
        }
