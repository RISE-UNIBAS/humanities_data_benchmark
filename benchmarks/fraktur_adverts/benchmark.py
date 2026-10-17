import logging
import re
import os
from collections import defaultdict

import Levenshtein
from scripts.benchmark_base import Benchmark
from scripts.scoring_helper import calculate_fuzzy_score

# Constants
DEFAULT_SECTION = "Es wird zum Verkauf angetragen"
SECTION_MATCH_THRESHOLD = 0.95


class FrakturAdverts(Benchmark):
    """
    Benchmark for Fraktur text extraction from historical documents.
    
    This benchmark evaluates a model's ability to accurately extract and transcribe
    structured advertisements from historical documents written in Fraktur script.
    It measures both fuzzy matching scores and character error rates (CER) between
    the model's predictions and ground truth data.
    """

    def calculate_cer(self, reference_text: str, hypothesis_text: str) -> float:
        """
        Calculate Character Error Rate (CER) between a reference text and a hypothesis text.
        
        CER is calculated as the Levenshtein distance (edit distance) divided by the number
        of characters in the reference text. Lower scores indicate better performance.
        
        Args:
            reference_text (str): The ground truth text.
            hypothesis_text (str): The predicted text.
            
        Returns:
            float: Character Error Rate, a value between 0.0 (perfect match) and potentially >1.0
                  (when hypothesis has more errors than reference characters).
        """
        if not reference_text:
            return 1.0  # Maximum error if reference is empty

        if not hypothesis_text:
            return 1.0  # Maximum error if hypothesis is empty

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
        on Fraktur text extraction.
        
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
        Score a model response by comparing extracted advertisements to ground truth.
        
        This method processes the model's response, compares the extracted advertisements 
        with the ground truth data, and calculates both fuzzy similarity scores and 
        character error rates (CER) for each advertisement. Special handling is applied
        for image_4 which requires default section assignment.
        
        Args:
            image_name (str): Name of the image being processed (e.g., "image_1", "image_4").
            response (dict): The model's full JSON response containing extracted advertisements.
            ground_truth (dict): The ground truth data for comparison, containing expected advertisements.
            
        Returns:
            dict: Dictionary with:
                - 'fuzzy': Average fuzzy similarity score (higher is better, max 1.0)
                - 'cer': Average character error rate (lower is better, min 0.0)
        """

        data = self.prepare_scoring_data(response)
        results = self.compare_ads(response=data,
                                   ground_truth=ground_truth,
                                   image_name=image_name)

        # Calculate scores
        total_fuzzy = 0
        total_cer = 0

        for result in results:
            total_fuzzy += result["similarity"]

            # Calculate CER if we have both texts
            if result["match_found"]:
                # Use the text from the ground truth and the response for CER calculation
                gt_text = result["ground_truth_text"]
                resp_text = result["response_text"]

                # Calculate and store the CER
                cer = self.calculate_cer(gt_text, resp_text)
                result["cer"] = round(cer, 3)
                total_cer += cer
            else:
                # Missing advertisement is maximum error
                result["cer"] = 1.0
                total_cer += 1.0

        # Ensure we don't divide by zero
        if len(results) > 0:
            avg_fuzzy = total_fuzzy / len(results)
            avg_cer = total_cer / len(results)
        else:
            avg_fuzzy = 0.0
            avg_cer = 1.0

        # compare_ads matched each advertisement by section and number prefix and
        # scored the pair; the loop above also filled in each one's CER. Keep that
        # instead of only its average, so the comparison view can show which advert
        # was matched to which and how far apart the two texts were.
        field_scores = {}
        for index, result in enumerate(results):
            key = "%s %s" % (result.get("section", "?"), result.get("number", index))
            field_scores[key] = {
                "response": result.get("response_text"),
                "ground_truth": result.get("ground_truth_text"),
                "score": result.get("similarity"),
                "cer": result.get("cer"),
                "match_found": result.get("match_found"),
            }

        return {
            "fuzzy": round(avg_fuzzy, 2),
            "cer": round(avg_cer, 3),  # Use 3 decimal places for CER for more precision
            "field_scores": field_scores
        }

    def extract_number_prefix(self,
                              text: str) -> int | None:
        """
        Extract the leading number prefix (e.g., '1.', '16.') from advertisement text.
        
        This method identifies the numbered list format commonly used in historical
        classified advertisements by extracting the leading ordinal number. It matches
        patterns like "16. Bey Hrn. Rudolf..." and extracts the number 16.
        
        Args:
            text (str): The advertisement text to analyze.
            
        Returns:
            int or None: The extracted number as an integer if found (e.g., 16), 
                        None if no number prefix is found.
        """

        match = re.match(r"^\s*(\d+)\.", text)

        return int(match.group(1)) if match else None

    def group_by_section_and_number(self,
                                    ad_list: list,
                                    image_name: str = None) -> dict:
        """ {section: {number: advert}} for the numbered adverts of a list.

        An advert without a number prefix is left out; a later advert with the same section
        and number replaces an earlier one. On image_4 an advert without a section belongs to
        DEFAULT_SECTION, the heading the page continues from the previous page.
        """
        grouped = defaultdict(dict)
        if not ad_list or not isinstance(ad_list, list):
            return grouped

        for ad in ad_list:
            if not isinstance(ad, dict):
                continue
            try:
                section = (ad.get("tags_section") or "").strip()
                if image_name == "image_4" and not section:
                    section = DEFAULT_SECTION
                    ad["tags_section"] = DEFAULT_SECTION
                number = self.extract_number_prefix(ad.get("text", ""))
                if section and number:
                    grouped[section][number] = ad
            except (AttributeError, TypeError) as e:
                logging.warning(f"Error grouping advertisement: {e}")
        return grouped

    @staticmethod
    def _result(section, number, gt_ad, response_ad):
        """ One compared advert: matched (with its similarity) or missing. """
        if response_ad is None:
            return {"section": section, "number": number, "match_found": False, "similarity": 0.0,
                    "response_text": None, "ground_truth_text": gt_ad["text"]}
        similarity = calculate_fuzzy_score(test_value=response_ad["text"], gold_value=gt_ad["text"])
        return {"section": section, "number": number, "match_found": True, "similarity": round(similarity, 3),
                "response_text": response_ad["text"], "ground_truth_text": gt_ad["text"]}

    def compare_ads(self,
                    response: dict,
                    ground_truth: dict | list,
                    image_name: str = None):
        """
        Compare the numbered adverts of the ground truth with the response's.

        Adverts are paired by section and number prefix. A ground-truth section is looked up
        in the response by name, else by the first response section whose name scores at least
        SECTION_MATCH_THRESHOLD. On image_4, whose adverts continue DEFAULT_SECTION, only that
        section is compared, and an advert is also found by its number in any response section.

        Returns one dict per ground-truth advert: section, number, match_found, similarity,
        response_text, ground_truth_text.
        """
        if isinstance(ground_truth, dict):
            ground_truth = [entry for ads in ground_truth.values() for entry in ads]
        try:
            response_grouped = self.group_by_section_and_number(response.get("advertisements", []), image_name)
        except (KeyError, AttributeError, TypeError) as e:
            logging.warning(f"Error getting response advertisements: {e}")
            response_grouped = {}
        ground_truth_grouped = self.group_by_section_and_number(ground_truth, image_name)

        if image_name == "image_4" and DEFAULT_SECTION in ground_truth_grouped:
            default_ads = response_grouped.get(DEFAULT_SECTION, {})
            results = []
            for number, gt_ad in ground_truth_grouped[DEFAULT_SECTION].items():
                response_ad = default_ads.get(number) or next(
                    (ads[number] for ads in response_grouped.values() if number in ads), None)
                results.append(self._result(DEFAULT_SECTION, number, gt_ad, response_ad))
            return results

        results = []
        for section, gt_ads in ground_truth_grouped.items():
            response_ads = response_grouped.get(section) or next(
                (ads for name, ads in response_grouped.items()
                 if calculate_fuzzy_score(test_value=name, gold_value=section) >= SECTION_MATCH_THRESHOLD), {})
            for number, gt_ad in gt_ads.items():
                results.append(self._result(section, number, gt_ad, response_ads.get(number)))
        return results
