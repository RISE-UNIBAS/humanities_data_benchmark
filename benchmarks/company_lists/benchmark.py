import logging
from scripts.benchmark_base import Benchmark
from scripts.scoring_helper import get_all_keys, get_nested_value, calculate_fuzzy_score


class CompanyLists(Benchmark):

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
        render = "not applicable anymore"
        return render