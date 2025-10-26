from scripts.benchmark_base import Benchmark

class TestBenchmark(Benchmark):

    def resize_images(self) -> bool:
        return True

    def score_benchmark(self, all_scores):
        return {"score": "niy"}
