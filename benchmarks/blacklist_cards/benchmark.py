import logging
from scripts.benchmark_base import Benchmark
from scripts.scoring_helper import get_all_keys, get_nested_value, calculate_fuzzy_score


class BlacklistCards(Benchmark):

    score_unparseable_as_miss = True

    def score_benchmark(self, all_scores):
        if not all_scores:
            return {"fuzzy": 0.0}
        total_score = 0
        for score in all_scores:
            logging.debug(f"Fuzzy score: {score['fuzzy']}")
            total_score += score['fuzzy']

        return {"fuzzy": total_score / len(all_scores)}

    def score_request_answer(self, image_name, response, ground_truth):
        data = self.prepare_scoring_data(response)

        my_keys = get_all_keys(ground_truth)

        avg_score = 0
        total_keys = 0
        field_scores = {}
        for k in my_keys:
            test_value = get_nested_value(data, k)
            gold_value = get_nested_value(ground_truth, k)

            # None, "null" and [] all mean empty
            if test_value is None or test_value == "null" or test_value == []:
                test_value = ""
            if gold_value is None or gold_value == "null" or gold_value == []:
                gold_value = ""

            # An unparseable response is a miss on every field, empty ones included.
            score = calculate_fuzzy_score(test_value, gold_value) if isinstance(data, dict) else 0.0
            field_scores[k] = {
                'response': test_value,
                'ground_truth': gold_value,
                'score': score,
            }
            avg_score += score
            total_keys += 1

        if total_keys > 0:
            avg_score /= total_keys
        else:
            avg_score = 0

        # Record what was compared, not just the average. The scorer already has the
        # two values and the similarity it assigned; keeping them lets the comparison
        # view show this scorer's own judgement instead of re-deriving one that would
        # disagree with it. Same shape as library_cards, which has always done this.
        return {"fuzzy": avg_score, "field_scores": field_scores}
