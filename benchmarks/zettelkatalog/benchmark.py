from scripts.benchmark_base import Benchmark
from scripts.scoring_helper import get_all_keys, get_nested_value, calculate_fuzzy_score


class Zettelkatalog(Benchmark):

    def score_benchmark(self, all_scores):
        return {"keine": "antwort"}

    def score_request_answer(self, image_name, response, ground_truth):
        return {"keine": "antwort"}

    def create_request_render(self, image_name, result, score, truth):
        return "muh"
