from scripts.benchmark_base import Benchmark

class TestBenchmark2(Benchmark):

    def resize_images(self) -> bool:
        return True

    def score_benchmark(self, all_scores):
        return {"score": "niy"}

    def score_request_answer(self, image_name, response, ground_truth):
        data = self.prepare_scoring_data(response)
        """print(data)
        print("-------------------------------")
        print(ground_truth)"""
        return {"score": 66, "scoresdfsdf_2": 77, "score_3": 88}

    def create_request_render(self, image_name, result, score, truth):
        render = f"""
### Result for image: {image_name}

#### Prompt:
  {self.load_prompt(image_name)}

#### Response:
  {result['response_text']}

#### Ground Truth:
  {truth}"""

        return render