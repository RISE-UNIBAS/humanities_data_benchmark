"""Benchmark implementation for Multilanguage Multiscript Bibliographic Data.

Evaluate models' ability to extract bibliographic entries from multilingual,
multiscript documents (Arabic, transliterated, German).
"""

import logging
from typing import Dict, List, Optional
from scripts.benchmark_base import Benchmark
from scripts.scoring_helper import calculate_fuzzy_score


class MultiBibliographicData(Benchmark):
    """Benchmark for Multilanguage Multiscript Bibliographic Data."""

    # Field importance weights for scoring
    FIELD_WEIGHTS = {
        # High importance - core bibliographic data
        "title.arabic": 2.0,
        "title.transliterated": 2.0,
        "title.german": 2.0,
        "author": 2.0,
        "author_arabic": 2.0,

        # Medium importance - key metadata
        "publication_details.year_gregorian": 1.0,
        "publication_details.year_hijri": 1.0,
        "publication_details.organization": 1.0,
        "publication_details.place": 1.0,
        "description": 1.0,
        "id": 1.0,

        # Lower importance - supplementary details
        "publication_details.pages": 0.5,
        "publication_details.language": 0.5,
    }

    def score_request_answer(self, image_name: str, response: dict, ground_truth: dict) -> dict:
        """Score a single request against ground truth.

        Uses hybrid approach:
        1. Entry-level matching by id (F1 score)
        2. Field-level weighted fuzzy matching for content quality

        Args:
            image_name: Name of the image/file being processed
            response: The model's response (parsed JSON)
            ground_truth: The expected ground truth (parsed JSON)

        Returns:
            Dictionary containing F1 metrics and field-level scores
        """
        data = self.prepare_scoring_data(response)

        # Handle case where response is a list but ground_truth has 'entries' key
        if isinstance(data, list) and "entries" in ground_truth:
            data = {"entries": data}
        elif isinstance(data, list):
            data = {"entries": data}

        # Ensure ground_truth has entries list
        if "entries" not in ground_truth:
            ground_truth = {"entries": ground_truth if isinstance(ground_truth, list) else [ground_truth]}

        # Extract entry lists
        predicted_entries = data.get("entries", [])
        ground_truth_entries = ground_truth.get("entries", [])

        # Build lookup dictionaries by id
        predicted_by_id = {entry.get("id"): entry for entry in predicted_entries if entry.get("id")}
        ground_truth_by_id = {entry.get("id"): entry for entry in ground_truth_entries if entry.get("id")}

        # Calculate entry-level F1 metrics
        true_positives = len(set(predicted_by_id.keys()) & set(ground_truth_by_id.keys()))
        false_positives = len(set(predicted_by_id.keys()) - set(ground_truth_by_id.keys()))
        false_negatives = len(set(ground_truth_by_id.keys()) - set(predicted_by_id.keys()))

        # Calculate field-level scores for matched entries
        matched_ids = set(predicted_by_id.keys()) & set(ground_truth_by_id.keys())
        field_scores = []

        for entry_id in matched_ids:
            pred_entry = predicted_by_id[entry_id]
            gt_entry = ground_truth_by_id[entry_id]
            entry_score = self._score_entry_fields(pred_entry, gt_entry)
            field_scores.append(entry_score)

        # Average field score across matched entries
        avg_field_score = sum(field_scores) / len(field_scores) if field_scores else 0.0

        logging.debug(f"{image_name}: TP={true_positives}, FP={false_positives}, FN={false_negatives}, Field Avg={avg_field_score:.3f}")

        return {
            "image_name": image_name,
            "tp": true_positives,
            "fp": false_positives,
            "fn": false_negatives,
            "field_score": avg_field_score,
            "num_predicted": len(predicted_entries),
            "num_ground_truth": len(ground_truth_entries),
        }

    def _score_entry_fields(self, predicted_entry: dict, ground_truth_entry: dict) -> float:
        """Score individual fields within a matched entry using weighted fuzzy matching.

        Args:
            predicted_entry: Predicted bibliographic entry
            ground_truth_entry: Ground truth bibliographic entry

        Returns:
            Weighted average field score (0.0 to 1.0)
        """
        total_score = 0.0
        total_weight = 0.0

        for field_path, weight in self.FIELD_WEIGHTS.items():
            pred_value = self._get_nested_field(predicted_entry, field_path)
            gt_value = self._get_nested_field(ground_truth_entry, field_path)

            # Skip if ground truth doesn't have this field
            if gt_value is None:
                continue

            score = calculate_fuzzy_score(pred_value, gt_value)
            total_score += score * weight
            total_weight += weight

        return total_score / total_weight if total_weight > 0 else 0.0

    def _get_nested_field(self, entry: dict, field_path: str) -> Optional[any]:
        """Retrieve nested field value from entry.

        Args:
            entry: Entry dictionary
            field_path: Dot-separated path (e.g., "title.arabic")

        Returns:
            Field value or None if not found
        """
        keys = field_path.split(".")
        value = entry

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None

            if value is None:
                return None

        return value

    def score_benchmark(self, all_scores: list) -> dict:
        """Aggregate scores from all requests.

        Calculates:
        - Overall F1 score (entry detection)
        - Average field quality score
        - Combined score (harmonic mean of F1 and field score)

        Args:
            all_scores: List of score dictionaries from score_request_answer

        Returns:
            Dictionary containing aggregated benchmark scores
        """
        if not all_scores:
            return {
                "f1_score": 0.0,
                "field_score": 0.0,
                "combined_score": 0.0,
                "precision": 0.0,
                "recall": 0.0,
                "num_samples": 0
            }

        # Aggregate F1 metrics
        total_tp = sum(s.get("tp", 0) for s in all_scores)
        total_fp = sum(s.get("fp", 0) for s in all_scores)
        total_fn = sum(s.get("fn", 0) for s in all_scores)

        # Calculate precision, recall, F1
        precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
        recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        # Average field quality score
        avg_field_score = sum(s.get("field_score", 0.0) for s in all_scores) / len(all_scores)

        # Combined score (harmonic mean of F1 and field score)
        if f1_score > 0 and avg_field_score > 0:
            combined_score = 2 * (f1_score * avg_field_score) / (f1_score + avg_field_score)
        else:
            combined_score = 0.0

        logging.info(f"F1: {f1_score:.3f}, Field: {avg_field_score:.3f}, Combined: {combined_score:.3f}")

        return {
            "f1_score": round(f1_score, 3),
            "field_score": round(avg_field_score, 3),
            "combined_score": round(combined_score, 3),
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "num_samples": len(all_scores),
            "total_tp": total_tp,
            "total_fp": total_fp,
            "total_fn": total_fn,
        }

    # Optional: Override these methods if needed

    # def remove_none_values(self) -> bool:
    #     """Whether to remove None values from parsed responses."""
    #     return True

    # def convert_result_to_json(self) -> bool:
    #     """Whether to convert response to JSON before scoring."""
    #     return True

    # def get_title(self) -> str:
    #     """Get benchmark title."""
    #     return "Multilanguage Multiscript Bibliographic Data"
