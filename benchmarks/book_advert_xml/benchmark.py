"""Benchmark implementation for Book Advert XML files (malformed) from Avisblatt.
"""

from typing import Dict, List
from scripts.benchmark_base import Benchmark


class BookAdvertXml(Benchmark):
    """Benchmark for Book Advert XML files (malformed) from Avisblatt."""

    def score_request_answer(self, image_name: str, response: dict, ground_truth: dict) -> dict:
        """Score a single request against ground truth.

        Args:
            image_name: Name of the image/file being processed
            response: The model's response (parsed JSON)
            ground_truth: The expected ground truth (parsed JSON)

        Returns:
            Dictionary containing scores for this request
        """
        # TODO: Implement scoring logic
        # Example structure:
        scores = {
            "image_name": image_name,
            "score": 0.0,
            # Add more metrics as needed
        }

        return scores

    def score_benchmark(self, all_scores: list) -> dict:
        """Aggregate scores from all requests.

        Args:
            all_scores: List of score dictionaries from score_request_answer

        Returns:
            Dictionary containing aggregated benchmark scores
        """
        # TODO: Implement aggregation logic
        if not all_scores:
            return {"overall_score": 0.0}

        # Calculate average score
        avg_score = sum(s.get("score", 0.0) for s in all_scores) / len(all_scores)

        return {
            "overall_score": avg_score,
            "num_samples": len(all_scores),
            # Add more aggregated metrics as needed
        }
