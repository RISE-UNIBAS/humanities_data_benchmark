""" This module contains the base class for all benchmark workflows. """
import importlib
import json
import logging
import os
import re
import tempfile
from abc import ABC, abstractmethod
from datetime import datetime

from data_loader import read_file, resize_image, write_file
from scoring_helper import remove_none
from simple_ai_clients import AiApiClient


class Benchmark(ABC):
    """ Base class for all benchmark workflows. """

    def __init__(self, config, api_key, benchmark_directory):
        """ Initialize the benchmark. """

        self.id = config.get('id')
        self.name = config['name']
        self.benchmark_dir = benchmark_directory
        self.provider = config['provider']
        self.model = config['model']
        self.api_key = api_key
        self.role_description = config['role_description']
        self.prompt_file = config['prompt_file']
        if self.prompt_file is None or self.prompt_file == "":
            self.prompt_file = "prompt.txt"
        self.prompt = self.load_prompt()
        self.request_render = ""
        self.dataclass_name = config['dataclass']
        self.dataclass = self.load_dataclass()
        if config['rules'] == "":
            self.rules = None
        else:
            self.rules = json.loads(config['rules'])

        kwargs = {
            "api": self.provider,
            "api_key": self.api_key,
            "gpt_role_description": self.role_description,
        }
        if self.dataclass:
            kwargs["dataclass"] = self.dataclass

        self.client = AiApiClient(**kwargs)
        logging.debug(f"Initialized benchmark {config['name']}")

    def is_runnable(self) -> bool:
        """ Check if the benchmark is runnable. """
        if not self.prompt:
            logging.error(f"Prompt not found for {self.name}")
            return False
        if not os.path.exists(self.benchmark_dir):
            logging.error(f"Benchmark directory not found: {self.benchmark_dir}")
            return False
        if not os.path.exists(os.path.join(self.benchmark_dir, "images")):
            logging.error(f"Images directory not found: {self.benchmark_dir}")
            return False
        if not os.path.exists(os.path.join(self.benchmark_dir, "ground_truths")):
            logging.error(f"Ground truths directory not found: {self.benchmark_dir}")
            return False
        if not self.provider in ["openai", "genai", "anthropic", "mistral"]:
            logging.error(f"Invalid provider: {self.provider}")
            return False
        if not self.model:
            logging.error(f"Model not found for {self.name}")
            return False
        return True

    def load_prompt(self) -> str:
        """ Load the prompt from the benchmark directory. """
        prompt_path = os.path.join(self.benchmark_dir, "prompts", self.prompt_file)
        prompt = read_file(prompt_path)
        logging.debug(f"Loaded prompt from {prompt_path}")
        if self.has_file_information:
            try:
                kwargs = {}  # Add file information here
                return prompt.format(**kwargs)
            except KeyError as e:
                return prompt
        return prompt

    def load_dataclass(self) -> None | type:
        """ Dynamically load a dataclass from dataclass.py """
        class_name = self.dataclass_name
        if class_name is None or class_name == "default" or class_name == "":
            return None

        try:
            dataclass_module = importlib.import_module(f"benchmarks.{self.name}.dataclass")
            logging.debug(f"Loaded dataclass {class_name}")
            return getattr(dataclass_module, class_name)
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Could not load dataclass {class_name}: {e}")

    def load_ground_truth(self,
                          image_name: str) -> dict:
        """ Load the ground truth from the benchmark directory. """
        ground_truth_path = os.path.join(self.benchmark_dir, "ground_truths", f"{image_name}.json")
        ground_truth_text = read_file(ground_truth_path)

        if self.convert_truth_to_json:
            try:
                return json.loads(ground_truth_text)
            except json.JSONDecodeError as e:
                return {"error": "Invalid JSON format."}
        return {"response_text": ground_truth_text}

    def ask_llm(self,
                image_paths: list[str]) -> dict:
        """ Ask the language model a question. """
        self.client.clear_image_resources()

        if self.resize_images:
            with tempfile.TemporaryDirectory() as temp_dir:
                resized_images = [
                    resize_image(image_path, temp_dir)
                    for image_path in image_paths
                ]

                for resized_image_path in resized_images:
                    self.client.add_image_resource(resized_image_path)

                return self.client.prompt(model=self.model, prompt=self.prompt)
        else:
            for image_path in image_paths:
                self.client.add_image_resource(image_path)

            return self.client.prompt(model=self.model, prompt=self.prompt)

    def get_request_answer_path(self):
        date_str = datetime.now().strftime('%Y-%m-%d')
        return str(os.path.join('..', 'results', date_str, self.id))

    def get_request_answer_file_name(self, image_name):
        """ Get the path to the answer file. """
        return os.path.join(self.get_request_answer_path(), self.get_request_name(image_name) + ".json")

    def get_request_render_path(self):
        date_str = datetime.now().strftime('%Y-%m-%d')
        return str(os.path.join('..', 'renders', date_str, self.id))

    def get_request_render_file_name(self, image_name):
        """ Get the path to the render file. """
        return os.path.join(self.get_request_render_path(), f'{image_name}.md')

    def save_request_answer(self,
                            image_name: str,
                            answer: dict) -> None:
        """ Save the answer to a file. """

        save_path = self.get_request_answer_path()
        os.makedirs(save_path, exist_ok=True)

        file_name = os.path.join(save_path,
                                 f"{self.get_request_name(image_name)}.json")
        write_file(file_name, answer)
        logging.info(f"Saved answer to {file_name}")

    def save_benchmark_score(self,
                             score: dict) -> None:
        """ Save the benchmark score to a file. """
        date_str = datetime.now().strftime('%Y-%m-%d')
        save_path = os.path.join('..', "results", date_str, self.id, "scoring.json")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        write_file(save_path, score)

    def prepare_scoring_data(self,
                             answer: dict) -> dict:
        """ Prepare the data for scoring. """
        if "response_text" in answer:
            response_text = answer["response_text"]
            json_text = None
            if self.convert_result_to_json and "```json" in response_text:
                json_match = re.search(r'```json\s*([\[{].*?[\]}])\s*```', response_text, re.DOTALL)
                if json_match:
                    json_text = json_match.group(1)

            if json_text is None:
                json_text = response_text

            if isinstance(json_text, dict):
                return json_text

            try:
                json_dict = json.loads(json_text)
                if self.remove_none_values:
                    return remove_none(json_dict)
                return json_dict
            except json.JSONDecodeError as e:
                return {"error": "Invalid JSON format."}

        return {"error": "No response text found."}

    def save_render(self,
                    image_name: str,
                    render: str) -> None:

        save_path = self.get_request_render_path()
        os.makedirs(save_path, exist_ok=True)
        write_file(self.get_request_render_file_name(image_name), render)

    def run(self, regenerate_existing_results=True):
        """Run the benchmark."""
        images_dir = os.path.join(self.benchmark_dir, 'images')
        image_files = sorted(os.listdir(images_dir))
        processed_images = set()

        # Update ground truth
        if self.update_required:
            self.update_ground_truth()

        # Group images by request
        image_groups = {}

        for image_file in image_files:
            if image_file in processed_images:
                continue

            match = re.match(self.get_page_part_regex(), image_file, re.IGNORECASE)
            if match:
                base_name = match.group(1)
                grouped_images = sorted([
                    img for img in image_files if img.startswith(base_name + '_p')
                ])
                image_groups[base_name] = grouped_images
                processed_images.update(grouped_images)
            else:
                image_name, _ = os.path.splitext(image_file)
                image_groups[image_name] = [image_file]
                processed_images.add(image_file)

        # Process each image group
        benchmark_scores = []
        for image_name, img_files in image_groups.items():
            image_paths = [os.path.join(images_dir, img) for img in img_files]
            if self.skip_image(image_name):
                logging.info(f"Skipping {image_name} as per configuration.")
                continue
            if (regenerate_existing_results and os.path.exists(self.get_request_answer_file_name(image_name))) or \
                    (not os.path.exists(self.get_request_answer_file_name(image_name))):
                logging.info(f"Processing {self.id}, {image_name}...")
                answer = self.ask_llm(image_paths)
                self.save_request_answer(image_name, answer)
            else:
                logging.info(f"Skipping {image_name} as the answer already exists.")
                answer_text = read_file(self.get_request_answer_file_name(image_name))
                answer = json.loads(answer_text)

            ground_truth = self.load_ground_truth(image_name)
            score = self.score_request_answer(image_name, answer, ground_truth)
            benchmark_scores.append(score)
            render = self.create_request_render(image_name, answer, score, ground_truth)
            self.save_render(image_name, render)

        benchmark_score = self.score_benchmark(benchmark_scores)
        self.save_benchmark_score(benchmark_score)

    def get_request_name(self, image_name: str) -> str:
        """ Get the name of the request. """
        return f"request_{self.id}_{os.path.splitext(image_name)[0]}"

    @abstractmethod
    def create_request_render(self,
                              image_name: str,
                              result: dict,
                              score: dict,
                              truth) -> str:
        """ Create a markdown render of the request. """
        pass

    @abstractmethod
    def score_request_answer(self,
                             image_name: str,
                             response: dict,
                             ground_truth: dict) -> dict:
        """ Score the response. """
        pass

    @abstractmethod
    def score_benchmark(self, all_scores):
        """ Score the benchmark. """
        pass

    def remove_none_values(self) -> bool:
        """If True, remove None values from the response before scoring."""
        return True

    def convert_result_to_json(self) -> bool:
        """If the result is a JSON string, convert it to a JSON object."""
        return True

    def convert_truth_to_json(self) -> bool:
        """If the result is a JSON string, convert it to a JSON object."""
        return True

    def resize_images(self) -> bool:
        """If images are too large, resize them before sending to the model."""
        return False

    def get_page_part_regex(self) -> str:
        """If multiple images are part of a single request, this regex will match the base name."""
        return r'(.+)_p\d+\.(jpg|jpeg|png)$'

    def get_title(self) -> str:
        """Title of the benchmark. Used in the result table."""
        return f"{self.name} ({self.provider}/{self.model})"

    def has_file_information(self) -> bool:
        """If the prompt file contains file information."""
        return False

    def skip_image(self,
                   image_name: str) -> bool:
        """ Skip image. """
        return False

    def update_required(self) -> bool:
        """ If an update of the ground truth is required before running the benchmark. """
        return False

    def update_ground_truth(self) -> None:
        """ Update the ground truth. """
        return None


class DefaultBenchmark(Benchmark):
    """ Default benchmark class. """

    def score_benchmark(self, all_scores):
        """ Score the benchmark. """
        return {"score": "niy"}

    def score_request_answer(self,
                             image_name: str,
                             response: dict,
                             ground_truth: dict) -> dict:
        """ Score the response. """
        return {}

    def create_request_render(self,
                              image_name: str,
                              result: dict,
                              score: dict,
                              truth) -> str:
        """ Create a markdown render of the request. """
        return ("### Result for image: {image_name}"
                "\n\n"
                "no details available")
