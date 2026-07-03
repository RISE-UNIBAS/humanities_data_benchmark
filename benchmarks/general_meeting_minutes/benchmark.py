"""Benchmark implementation for General Meeting Minutes.

Extract names, locations, signatures from table-like metting minutes of Mines de Costano S.A., 1930s - 1960s
"""
from typing import Dict, List
from scripts.benchmark_base import Benchmark
from scripts.scoring_helper import get_all_keys, get_nested_value, calculate_fuzzy_score


class GeneralMeetingMinutes(Benchmark):
    """Benchmark for General Meeting Minutes."""

    def get_prompt_kwargs(self, basename: str,
                          filenames: List[str]) -> Dict:
        """If the prompt file contains file information."""
        page_number = basename.split("page_")[-1].split(".")[0]  # Extract page number from filename

        return {
            "filename": basename,
            "page_number": page_number
        }

    def score_request_answer(self, image_name: str, response: dict, ground_truth: dict) -> dict:
        """Score a single request against ground truth.

        Args:
            image_name: Name of the image/file being processed
            response: The model's response (parsed JSON)
            ground_truth: The expected ground truth (parsed JSON)

        Returns:
            Dictionary containing scores for this request
        """
        print("Scoring response for:", image_name)
        data = self.prepare_scoring_data(response)

        my_keys = get_all_keys(ground_truth)

        avg_score = 0
        total_keys = 0
        for k in my_keys:
            test_value = get_nested_value(data, k)
            gold_value = get_nested_value(ground_truth, k)

            score = calculate_fuzzy_score(test_value, gold_value)
            avg_score += score
            total_keys += 1

        if total_keys > 0:
            avg_score /= total_keys
        else:
            avg_score = 0

        return {"fuzzy": avg_score}

    def score_benchmark(self, all_scores: list) -> dict:
        """Aggregate scores from all requests.

        Args:
            all_scores: List of score dictionaries from score_request_answer

        Returns:
            Dictionary containing aggregated benchmark scores
        """
        total_score = 0
        for score in all_scores:
            print(score)
            total_score += score['fuzzy']

        return {"fuzzy": total_score / len(all_scores)}
