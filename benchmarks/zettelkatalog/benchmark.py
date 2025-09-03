import logging

from scripts.benchmark_base import Benchmark
from scripts.scoring_helper import get_all_keys, get_nested_value, calculate_fuzzy_score


class Zettelkatalog(Benchmark):

    def score_benchmark(self, all_scores):
        return {"keine": "antwort"}

    def score_request_answer(self, image_name, response, ground_truth):
        """

        """

        data = self.prepare_scoring_data(response)
        ground_truth = ground_truth["response_text"]

        logging.info(image_name)
        logging.info(data)
        logging.info(ground_truth)

        return {"keine": "antwort"}

    def create_request_render(self, image_name, result, score, truth):
        return "lala"
