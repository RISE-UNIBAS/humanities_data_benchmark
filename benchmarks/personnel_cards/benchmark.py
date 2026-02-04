"""Benchmark implementation for Personnel Cards.

This benchmark scores personnel card extraction using F1 micro scoring
with field-level fuzzy matching. The rules configuration allows selective
scoring of diplomatic_transcript, interpretation, and is_crossed_out fields.
"""

import json
import logging
from typing import Dict, List

from scripts.benchmark_base import Benchmark
from scripts.scoring_helper import get_all_keys, get_nested_value, calculate_fuzzy_score
from ai_client import LLMResponse


class PersonnelCards(Benchmark):
    """Benchmark for Personnel Cards.

    Default scoring rules (when rules is None or empty):
    - score_diplomatic_transcript: True
    - score_interpretation: True
    - score_is_crossed_out: True
    """

    def score_benchmark(self, all_scores: list) -> dict:
        """Calculate macro and micro F1 scores across all test instances.

        Micro F1: Aggregate TP/FP/FN across all instances, then calculate F1
        Macro F1: Calculate F1 for each instance, then average the F1 scores

        Args:
            all_scores: List of score dictionaries from score_request_answer

        Returns:
            Dictionary containing aggregated benchmark scores
        """
        if not all_scores:
            return {"f1_micro": 0.0, "f1_macro": 0.0}

        # For micro F1: sum all TP, FP, FN across instances
        total_tp = 0
        total_fp = 0
        total_fn = 0

        # For macro F1: collect individual F1 scores
        f1_scores = []

        for score_data in all_scores:
            if isinstance(score_data, dict) and 'f1_score' in score_data:
                # Add to totals for micro F1
                total_tp += score_data.get('true_positives', 0)
                total_fp += score_data.get('false_positives', 0)
                total_fn += score_data.get('false_negatives', 0)

                # Collect individual F1 for macro F1
                f1_scores.append(score_data['f1_score'])

        # Calculate micro F1
        micro_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
        micro_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
        f1_micro = 2 * micro_precision * micro_recall / (micro_precision + micro_recall) if (micro_precision + micro_recall) > 0 else 0.0

        # Calculate macro F1 (average of individual F1 scores)
        f1_macro = sum(f1_scores) / len(f1_scores) if f1_scores else 0.0

        score = {
            "f1_micro": f1_micro,
            "f1_macro": f1_macro,
            "micro_precision": micro_precision,
            "micro_recall": micro_recall,
            "total_instances": len(f1_scores),
            "total_tp": total_tp,
            "total_fp": total_fp,
            "total_fn": total_fn
        }

        logging.info(f"f1_micro: {f1_micro}, f1_macro: {f1_macro}")

        return score

    def score_request_answer(self, image_name: str, response: dict, ground_truth: dict) -> dict:
        """Score the response against ground truth using F1 score based on field-level comparison.

        Each field is treated as a separate entity for TP/FP/FN calculation.
        Fields are filtered based on rules configuration.

        Args:
            image_name: Name of the image/file being processed
            response: The model's response (parsed JSON)
            ground_truth: The expected ground truth (parsed JSON)

        Returns:
            Dictionary containing scores for this request
        """
        data = self.prepare_scoring_data(response)

        logging.info(image_name)
        logging.debug(f"response: {data}")
        logging.debug(f"ground_truth: {ground_truth}")

        # Get all terminal fields from both response and ground truth
        response_keys = get_all_keys(data)
        gt_keys = get_all_keys(ground_truth)

        # Calculate TP, FP, FN for each field
        tp = 0  # True positives - fields that match between response and ground truth
        fp = 0  # False positives - fields in response but not matching in ground truth
        fn = 0  # False negatives - fields in ground truth but not matching in response

        # Track field-level scores for debugging
        field_scores = {}

        # Get all unique keys from both datasets
        all_keys = set(response_keys + gt_keys)

        # Filter keys based on rules and structure
        filtered_keys = self._filter_keys_by_rules(all_keys)

        for key in filtered_keys:
            response_value = get_nested_value(data, key)
            gt_value = get_nested_value(ground_truth, key)

            # Convert empty strings to None for consistent comparison
            if response_value == "":
                response_value = None
            if gt_value == "":
                gt_value = None

            # Calculate fuzzy match score for this field
            field_score = calculate_fuzzy_score(response_value, gt_value)
            field_scores[key] = {
                'response': response_value,
                'ground_truth': gt_value,
                'score': field_score
            }

            # Threshold for considering a match (can be adjusted)
            match_threshold = 0.92

            if response_value is not None and gt_value is not None:
                if field_score >= match_threshold:
                    tp += 1
                else:
                    # Both have values but don't match well enough
                    fp += 1
                    fn += 1
            elif response_value is not None and gt_value is None:
                fp += 1  # Response has value but ground truth doesn't
            elif response_value is None and gt_value is not None:
                fn += 1  # Ground truth has value but response doesn't
            # If both are None, it's neither TP, FP, nor FN

        # Calculate precision, recall, and F1
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        score = {
            'f1_score': round(f1, 2),
            'precision': precision,
            'recall': recall,
            'true_positives': tp,
            'false_positives': fp,
            'false_negatives': fn,
            'field_scores': field_scores,
            'total_fields': len(all_keys)
        }

        logging.info(score['f1_score'])
        for line in score['field_scores'].values():
            logging.debug(line)

        return score

    def _filter_keys_by_rules(self, all_keys: set) -> list:
        """Filter keys based on rules configuration and structural requirements.

        Default rules (when rules is None or empty):
        - score_diplomatic_transcript: True
        - score_interpretation: True
        - score_is_crossed_out: True

        Args:
            all_keys: Set of all field paths from both response and ground truth

        Returns:
            List of filtered field paths to be scored
        """
        # Define default rules explicitly
        DEFAULT_RULES = {
            'score_diplomatic_transcript': True,
            'score_interpretation': True,
            'score_is_crossed_out': True
        }

        # Get rules configuration, applying defaults for missing keys
        rules = self.rules if self.rules else {}
        score_diplomatic_transcript = rules.get('score_diplomatic_transcript', DEFAULT_RULES['score_diplomatic_transcript'])
        score_interpretation = rules.get('score_interpretation', DEFAULT_RULES['score_interpretation'])
        score_is_crossed_out = rules.get('score_is_crossed_out', DEFAULT_RULES['score_is_crossed_out'])

        # Filter out structural fields and parent keys
        filtered_keys_temp = []
        for key in all_keys:
            # Skip row_number (structural, not content)
            if key.endswith('.row_number') or key == 'row_number':
                continue

            # Skip fields based on rules
            if key.endswith('.diplomatic_transcript') and not score_diplomatic_transcript:
                continue
            if key.endswith('.interpretation') and not score_interpretation:
                continue
            if key.endswith('.is_crossed_out') and not score_is_crossed_out:
                continue

            filtered_keys_temp.append(key)

        # Filter out parent keys when child keys exist
        filtered_keys = []
        for key in filtered_keys_temp:
            # Check if this key has any children in the key set
            has_children = any(other_key.startswith(key + '.') for other_key in filtered_keys_temp if other_key != key)
            if not has_children:
                filtered_keys.append(key)

        return filtered_keys
