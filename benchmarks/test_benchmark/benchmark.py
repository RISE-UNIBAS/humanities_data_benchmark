from scripts.benchmark_base import Benchmark


class TestBenchmark(Benchmark):

    def score_request_answer(self, image_name: str, response: dict, ground_truth: dict) -> dict:
        pass

    def resize_images(self) -> bool:
        return True

    def score_benchmark(self, all_scores):
        return {"score": "niy"}
