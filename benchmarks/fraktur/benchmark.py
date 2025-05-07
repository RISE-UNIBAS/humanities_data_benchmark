import logging

from scripts.benchmark_base import Benchmark
from scripts.scoring_helper import get_all_keys, get_nested_value, calculate_fuzzy_score
import re
from collections import defaultdict
from difflib import SequenceMatcher

class Fraktur(Benchmark):

    def score_benchmark(self, all_scores):
        return "miau"

    def score_request_answer(self, image_name, response, ground_truth):
        data = self.prepare_scoring_data(response)


        # extract gt
        # pro überschrift, anhand der ad nummer (am anfang vom text)

        # extract completion data
        # same

        # compare gt and completion data for scoring
        """avg_score = 0
        total_keys = 0
        for k in my_keys:
            test_value = get_nested_value(data, k)
            gold_value = get_nested_value(ground_truth, k)

            # Skip metadata fields to focus on bibliographic entries
            if k.startswith("metadata"):
                continue

            score = calculate_fuzzy_score(test_value, gold_value)
            avg_score += score
            total_keys += 1

        if total_keys > 0:
            avg_score /= total_keys
        else:
            avg_score = 0

        return {"fuzzy": avg_score}
        """

        results = self.compare_ads(generated=data,
                                    ground_truth=ground_truth)

        logging.info(results)
        return None


    def extract_number_prefix(self,
                              text):
        """Extract leading number like '1.' from text"""
        match = re.match(r"^\s*(\d+)\.", text)

        return int(match.group(1)) if match else None

    def group_by_section_and_number(self,
                                    ad_list):
        """Group ads by tags_section and leading number in text"""
        grouped = defaultdict(dict)
        for ad in ad_list:
            if not isinstance(ad, dict):
                continue  # skip malformed entries
            section = ad.get("tags_section", "").strip()
            number = self.extract_number_prefix(ad.get("text", ""))
            if section and number:
                grouped[section][number] = ad
        return grouped

    def compare_ads(self, generated, ground_truth):
        # Flatten ground_truth values (list of list of dicts) into single list
        ground_truth_flat = [entry for ads in ground_truth.values() for entry in ads]

        # Group generated and ground_truth data
        generated_grouped = self.group_by_section_and_number(generated["advertisements"])
        ground_truth_grouped = self.group_by_section_and_number(ground_truth_flat)

        results = []

        for section, gt_ads in ground_truth_grouped.items():
            gen_ads = generated_grouped.get(section, {})
            for number, gt_ad in gt_ads.items():
                gen_ad = gen_ads.get(number)
                if gen_ad:
                    similarity = SequenceMatcher(None, gt_ad["text"], gen_ad["text"]).ratio()
                    results.append({
                        "section": section,
                        "number": number,
                        "match_found": True,
                        "similarity": round(similarity, 3),
                        "generated_text": gen_ad["text"],
                        "ground_truth_text": gt_ad["text"]
                    })
                else:
                    results.append({
                        "section": section,
                        "number": number,
                        "match_found": False,
                        "similarity": 0.0,
                        "generated_text": None,
                        "ground_truth_text": gt_ad["text"]
                    })
        return results

    def create_request_render(self, image_name, result, score, truth):
        data = self.prepare_scoring_data(result)

        render = f"MIAU"

        return render
