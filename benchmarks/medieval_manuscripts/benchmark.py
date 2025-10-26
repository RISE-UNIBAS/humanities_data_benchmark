import logging
import os
from typing import Dict, List, Any

import Levenshtein
from scripts.benchmark_base import Benchmark
from scripts.scoring_helper import calculate_fuzzy_score


class MedievalManuscripts(Benchmark):
    """
    Benchmark for medieval manuscript transcription and extraction.

    This benchmark evaluates a model's ability to accurately extract and transcribe
    text from medieval manuscripts, including main text, folio numbers, and marginal
    additions. It measures both fuzzy matching scores and character error rates (CER)
    between the model's predictions and ground truth data.
    """

    @staticmethod
    def normalize_empty(value):
        """
        Normalize empty values - treat None, empty string, and whitespace-only strings as equivalent.

        Args:
            value: The value to normalize (can be str, None, or other types).

        Returns:
            str: Empty string if value is None, empty, or whitespace-only; otherwise the original value.
        """
        if value is None:
            return ""
        if isinstance(value, str) and not value.strip():
            return ""
        return value

    def calculate_cer(self, reference_text: str, hypothesis_text: str) -> float:
        """
        Calculate Character Error Rate (CER) between a reference text and a hypothesis text.

        CER is calculated as the Levenshtein distance (edit distance) divided by the number
        of characters in the reference text. Lower scores indicate better performance.

        Args:
            reference_text (str): The ground truth text.
            hypothesis_text (str): The predicted text.

        Returns:
            float: Character Error Rate, a value between 0.0 (perfect match) and 1.0.
        """
        # Normalize empty values
        reference_text = self.normalize_empty(reference_text)
        hypothesis_text = self.normalize_empty(hypothesis_text)

        # If both are empty, perfect match
        if not reference_text and not hypothesis_text:
            return 0.0

        # If only one is empty, maximum error
        if not reference_text or not hypothesis_text:
            return 1.0

        # Normalize strings - lowercase and remove extra whitespace
        ref_normalized = ' '.join(reference_text.lower().split())
        hyp_normalized = ' '.join(hypothesis_text.lower().split())

        # If strings are identical after normalization
        if ref_normalized == hyp_normalized:
            return 0.0

        # Calculate Levenshtein distance (minimum number of single-character edits)
        edit_distance = Levenshtein.distance(ref_normalized, hyp_normalized)

        # Divide by the length of the reference text
        return min(1.0, edit_distance / max(1, len(ref_normalized)))

    def score_benchmark(self, all_scores: list) -> dict:
        """
        Calculate the overall benchmark score by averaging fuzzy scores and CER across documents.

        This method computes average scores across all processed images,
        providing metrics that represent the benchmark's overall performance
        on medieval manuscript transcription.

        Args:
            all_scores (list): List of dictionaries containing individual scores for each document,
                              where each dictionary has 'fuzzy' and 'cer' keys.

        Returns:
            dict: Dictionary with keys 'fuzzy' (higher is better) and 'cer' (lower is better)
                 containing the averaged scores rounded to 3 decimal places.
        """
        total_fuzzy = 0
        total_cer = 0

        for score in all_scores:
            total_fuzzy += score['fuzzy']
            total_cer += score['cer']

        # Ensure we don't divide by zero
        if len(all_scores) > 0:
            avg_fuzzy = total_fuzzy / len(all_scores)
            avg_cer = total_cer / len(all_scores)
        else:
            avg_fuzzy = 0.0
            avg_cer = 1.0

        return {
            "fuzzy": round(avg_fuzzy, 3),
            "cer": round(avg_cer, 3)
        }

    def score_request_answer(self,
                             image_name: str,
                             response: dict,
                             ground_truth: dict) -> dict:
        """
        Score a model response by comparing extracted texts to ground truth.

        This method processes the model's response, compares the extracted folio entries
        with the ground truth data, and calculates both fuzzy similarity scores and
        character error rates (CER) for each text field (folio, text, additions).

        Args:
            image_name (str): Name of the image being processed (e.g., "image_1").
            response (dict): The model's full JSON response containing extracted folios.
            ground_truth (dict): The ground truth data for comparison.

        Returns:
            dict: Dictionary with:
                - 'fuzzy': Average fuzzy similarity score (higher is better, max 1.0)
                - 'cer': Average character error rate (lower is better, min 0.0)
        """
        data = self.prepare_scoring_data(response)
        results = self.compare_folios(response=data, ground_truth=ground_truth)

        # Calculate scores
        total_fuzzy = 0
        total_cer = 0
        count = 0

        for result in results:
            total_fuzzy += result["similarity"]
            total_cer += result["cer"]
            count += 1

        # Ensure we don't divide by zero
        if count > 0:
            avg_fuzzy = total_fuzzy / count
            avg_cer = total_cer / count
        else:
            avg_fuzzy = 0.0
            avg_cer = 1.0

        return {
            "fuzzy": round(avg_fuzzy, 3),
            "cer": round(avg_cer, 3)
        }

    def compare_folios(self,
                      response: dict,
                      ground_truth: dict) -> List[Dict[str, Any]]:
        """
        Compare folio entries between response and ground truth.

        This method matches folio entries from the model's response to the ground truth data
        by position/order in the list, then calculates text similarity scores for folio number,
        main text, and additions using fuzzy matching and CER.

        Args:
            response (dict): The model's parsed response containing extracted folios.
            ground_truth (dict): The ground truth data containing expected folios.

        Returns:
            list: List of dictionaries containing comparison results for each field, including:
                - folio_ref: Folio reference from ground truth (e.g., "[3r]")
                - field: Field name ("folio", "text", "addition1", etc.)
                - match_found: Boolean indicating if a matching entry was found
                - similarity: Fuzzy similarity score (0.0-1.0)
                - cer: Character error rate (0.0-1.0)
                - response_text: Text from model's response (or None if no match)
                - ground_truth_text: Text from ground truth
        """
        results = []

        # Get folios list from response
        response_folios_list = response.get("folios", [])
        if not isinstance(response_folios_list, list):
            response_folios_list = []

        # Convert ground truth dict to sorted list by folio reference
        gt_sorted_items = sorted(ground_truth.items())

        # Iterate through ground truth folios and match by position
        for idx, (folio_ref, gt_entries) in enumerate(gt_sorted_items):
            if not gt_entries or len(gt_entries) == 0:
                continue

            gt_entry = gt_entries[0]  # Each folio has one entry in a list

            # Match by position - if response has entry at this index, use it
            response_entry = None
            match_found = False
            if idx < len(response_folios_list):
                response_entry = response_folios_list[idx]
                if isinstance(response_entry, dict):
                    match_found = True

            # Score folio number
            gt_folio = self.normalize_empty(gt_entry.get("folio", ""))
            resp_folio = self.normalize_empty(response_entry.get("folio", "") if response_entry else "")

            if gt_folio or resp_folio:  # Only score if at least one is non-empty
                folio_similarity = calculate_fuzzy_score(test_value=resp_folio, gold_value=gt_folio) if match_found else 0.0
                folio_cer = self.calculate_cer(gt_folio, resp_folio) if match_found else 1.0

                results.append({
                    "folio_ref": folio_ref,
                    "field": "folio",
                    "match_found": match_found,
                    "similarity": round(folio_similarity, 3),
                    "cer": round(folio_cer, 3),
                    "response_text": resp_folio if match_found else None,
                    "ground_truth_text": gt_folio
                })

            # Score main text
            gt_text = self.normalize_empty(gt_entry.get("text", ""))
            resp_text = self.normalize_empty(response_entry.get("text", "") if response_entry else "")

            text_similarity = calculate_fuzzy_score(test_value=resp_text, gold_value=gt_text) if match_found else 0.0
            text_cer = self.calculate_cer(gt_text, resp_text) if match_found else 1.0

            results.append({
                "folio_ref": folio_ref,
                "field": "text",
                "match_found": match_found,
                "similarity": round(text_similarity, 3),
                "cer": round(text_cer, 3),
                "response_text": resp_text if match_found else None,
                "ground_truth_text": gt_text
            })

            # Score additions (addition1, addition2, addition3, etc.)
            # Find all addition fields in ground truth
            for i in range(1, 10):  # Support up to addition9
                addition_key = f"addition{i}"
                gt_addition = gt_entry.get(addition_key)

                if gt_addition is None:
                    break  # No more additions

                # Normalize both values
                gt_addition = self.normalize_empty(gt_addition)
                resp_addition = self.normalize_empty(response_entry.get(addition_key, "") if response_entry else "")

                # Skip scoring if both are empty (correctly empty field)
                if not gt_addition and not resp_addition:
                    continue

                # Only score if at least one is non-empty
                addition_similarity = calculate_fuzzy_score(test_value=resp_addition, gold_value=gt_addition) if match_found else 0.0
                addition_cer = self.calculate_cer(gt_addition, resp_addition) if match_found else 1.0

                results.append({
                    "folio_ref": folio_ref,
                    "field": addition_key,
                    "match_found": match_found,
                    "similarity": round(addition_similarity, 3),
                    "cer": round(addition_cer, 3),
                    "response_text": resp_addition if match_found else None,
                    "ground_truth_text": gt_addition
                })

        return results

