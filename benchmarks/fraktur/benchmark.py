import logging

from scripts.benchmark_base import Benchmark
from scripts.scoring_helper import get_all_keys, get_nested_value, calculate_fuzzy_score
import re
from collections import defaultdict
from difflib import SequenceMatcher


class Fraktur(Benchmark):

    def score_benchmark(self, all_scores):
        """

        """

        total_score = 0
        for score in all_scores:
            total_score += score['fuzzy']

        return {"fuzzy": total_score / len(all_scores)}

    def score_request_answer(self,
                             image_name,
                             response,
                             ground_truth):
        """

        """

        data = self.prepare_scoring_data(response)
        results = self.compare_ads(response=data,
                                   ground_truth=ground_truth)

        # avg fuzzy score over all ads on a page
        avg_score = sum([result["similarity"] for result in results]) / len(results)

        return {"fuzzy": avg_score}

    def extract_number_prefix(self,
                              text):
        """Extract leading number like '1.' from text"""

        match = re.match(r"^\s*(\d+)\.", text)

        return int(match.group(1)) if match else None

    def group_by_section_and_number(self,
                                    ad_list: list) -> dict:
        """Group ads by tags_section and leading number in text.

        """

        grouped = defaultdict(dict)
        for ad in ad_list:
            if not isinstance(ad, dict):
                continue  # skip malformed entries
            section = ad.get("tags_section", "").strip()
            number = self.extract_number_prefix(ad.get("text", ""))
            if section and number:
                grouped[section][number] = ad
        return grouped

    def compare_ads(self,
                    response: dict,
                    ground_truth: dict):
        """

        """

        # Flatten ground_truth values (list of list of dicts) into single list
        ground_truth_flat = [entry for ads in ground_truth.values() for entry in ads]

        # Group response and ground_truth data
        try:
            response_grouped = self.group_by_section_and_number(response["advertisements"])
        except KeyError:
            response_grouped = {}
        ground_truth_grouped = self.group_by_section_and_number(ground_truth_flat)

        # Compare ads per section
        results = []
        for section, gt_ads in ground_truth_grouped.items():
            response_ads = response_grouped.get(section, {})

            for number, gt_ad in gt_ads.items():
                response_ad = response_ads.get(number)
                if response_ad:
                    similarity = calculate_fuzzy_score(test_value=response_ad["text"], gold_value=gt_ad["text"])#SequenceMatcher(None, gt_ad["text"], response_ad["text"]).ratio()
                    results.append({
                        "section": section,
                        "number": number,
                        "match_found": True,
                        "similarity": round(similarity, 3),
                        "response_text": response_ad["text"],
                        "ground_truth_text": gt_ad["text"]
                    })
                else:
                    results.append({
                        "section": section,
                        "number": number,
                        "match_found": False,
                        "similarity": 0.0,
                        "response_text": None,
                        "ground_truth_text": gt_ad["text"]
                    })
        return results

    def create_request_render(self, image_name, result, score, truth):
        data = self.prepare_scoring_data(result)
        results = self.compare_ads(response=data, ground_truth=truth)
        
        # Add result header and overall score at the top
        render = f"**Result for image: {image_name}**\n\n"
        render += f"**Average fuzzy score:** {score['fuzzy']:.3f}\n\n"
        
        # Create markdown table with 4 columns
        render += "| Section | Prediction | Ground Truth | Score |\n"
        render += "|---------|------------|--------------|-------|\n"
        
        for item in results:
            section = item["section"]
            prediction = item["response_text"] or "N/A"
            ground_truth = item["ground_truth_text"]
            similarity = f"{item['similarity']:.3f}"
            
            # Format multi-line text for markdown table
            prediction = prediction.replace("\n", "<br>")
            ground_truth = ground_truth.replace("\n", "<br>")
            
            render += f"| {section} | {prediction} | {ground_truth} | {similarity} |\n"
        
        return render
