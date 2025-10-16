import logging
from typing import Dict

from scripts.benchmark_base import Benchmark
from scripts.scoring_helper import get_all_keys, get_nested_value, calculate_fuzzy_score


class BibliographicData(Benchmark):

    def get_prompt_kwargs(self, filename: str) -> Dict:
        """If the prompt file contains file information."""
        page_number = filename.split("_")[-1].split(".")[0]  # Extract page number from filename
        return {
            "page_number": page_number
        }

    def score_benchmark(self, all_scores):
        total_score = 0
        for score in all_scores:
            logging.debug(f"Fuzzy score: {score['fuzzy']}")
            total_score += score['fuzzy']

        return {"fuzzy": total_score / len(all_scores)}

    def score_request_answer(self, image_name, response, ground_truth):
        data = self.prepare_scoring_data(response)
        
        # Check if data is a list (array) but ground_truth has entries
        if isinstance(data, list) and "entries" in ground_truth:
            # Create entries wrapper to match ground truth structure
            data = {"entries": data}
        
        my_keys = get_all_keys(ground_truth)
        
        avg_score = 0
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

    def create_request_render(self, image_name, result, score, truth):
        data = self.prepare_scoring_data(result)
        
        # Check if data is a list (array) but truth has entries
        if isinstance(data, list) and "entries" in truth:
            # Create entries wrapper to match ground truth structure
            data = {"entries": data}
            
        my_keys = get_all_keys(truth)
        avg_score = 0
        md_table_body = ""
        total_keys = 0
        
        for k in my_keys:
            # Skip metadata fields to focus on bibliographic entries
            if k.startswith("metadata"):
                continue
                
            test_value = get_nested_value(data, k)
            gold_value = get_nested_value(truth, k)
            item_score = calculate_fuzzy_score(test_value, gold_value)
            avg_score += item_score
            total_keys += 1
            md_table_body += f"\n| {k} | {test_value} | {gold_value} | {item_score} |"
            
        if total_keys > 0:
            avg_score /= total_keys
        else:
            avg_score = 0

        render = (
            f"### Result for image: {image_name}\n"
            f"Average Fuzzy Score: **{avg_score}**\n"
            "<small>\n\n"
            f"| Key | Value | Ground Truth | Score |\n"
            f"| --- | --- | --- | --- |"
            f"{md_table_body}\n\n"
            "</small>\n"
        )

        return render