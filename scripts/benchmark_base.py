""" This module contains the base class for all benchmark workflows. """
import importlib
import json
import logging
import os
import re
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Union, Pattern, Optional, Iterable, Set

from data_loader import read_file, write_file
from ai_client import create_ai_client, LLMResponse


class Benchmark(ABC):
    """ Base class for all benchmark workflows. """

    multi_image_support = False
    multi_text_support = False
    use_shared_context = False  # Enable multi-stage requests with shared context

    def __init__(self, config, api_key, benchmark_directory):
        """ Initialize the benchmark. """

        self.id = config.get('id')                          # Unique Test ID 'T0001'
        self.name = config.get('name')                      # Unique benchmark dataset name (=directory name)
        self.benchmark_dir = benchmark_directory            # Path to the benchmark directory
        self.provider = config['provider']                  # AI provider
        self.model = config['model']                        # Model name
        self.api_key = api_key                              # API key for the provider
        self.role_description = config.get['role_description']  # Role description for the system prompt
        self.prompt_file = config['prompt_file']            # Prompt file name
        self.date = datetime.now().strftime('%Y-%m-%d')     # Date of the benchmark run
        self.temperature = config.get('temperature', 0.5)  # Temperature setting for the model

        # Prompt
        if self.prompt_file is None or self.prompt_file == "":
            self.prompt_file = "prompt.txt"
        self.prompt_file_exists = os.path.exists(os.path.join(self.benchmark_dir, "prompts", self.prompt_file))
        self.prompt = None # Load later to allow dynamic formatting on request basis

        # Dataclass
        self.dataclass_name = config['dataclass']
        self.dataclass = self.load_dataclass()

        # Rules
        if config['rules'] == "":
            self.rules = None
        else:
            self.rules = json.loads(config['rules'])

        kwargs = {}
        if self.dataclass:
            kwargs["dataclass"] = self.dataclass

        self.client = create_ai_client(self.provider,
                                       self.api_key,
                                       system_prompt=self.role_description,
                                       **kwargs)

        # Shared context support (for multi-stage requests)
        self.conversation_id = None  # Track conversation for subsequent requests
        self.shared_context_established = False

        logging.debug(f"Initialized benchmark {config['name']}")

    def is_runnable(self) -> bool:
        """ Check if the benchmark is runnable. """
        if not self.prompt_file_exists:
            logging.error(f"Prompt not found for {self.name}")
            return False
        if not os.path.exists(self.benchmark_dir):
            logging.error(f"Benchmark directory not found: {self.benchmark_dir}")
            return False
        if not os.path.exists(os.path.join(self.benchmark_dir, "images")) and \
              not os.path.exists(os.path.join(self.benchmark_dir, "texts")):
            logging.error(f"'images' or 'texts' directory not found: {self.benchmark_dir}")
            return False
        if not os.path.exists(os.path.join(self.benchmark_dir, "ground_truths")):
            logging.error(f"Ground truths directory not found: {self.benchmark_dir}")
            return False
        if not self.provider in ["openai", "genai", "anthropic", "mistral", "openrouter", "scicore"]:
            logging.error(f"Invalid provider: {self.provider}")
            return False
        if not self.model:
            logging.error(f"Model not found for {self.name}")
            return False
        return True

    def load_prompt(self,
                    object_basename: str) -> str:
        """ Load the prompt from the benchmark directory. """
        prompt_path = os.path.join(self.benchmark_dir, "prompts", self.prompt_file)
        prompt = read_file(prompt_path)
        logging.debug(f"Loaded prompt from {prompt_path}")
        prompt_kwargs = self.get_prompt_kwargs(object_basename)
        if prompt_kwargs:
            try:
                return prompt.format(**prompt_kwargs)
            except KeyError as e:
                logging.error(f"Missing key in prompt formatting: {e}")
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
                          object_basename: str) -> dict:
        """ Load the ground truth from the benchmark directory. """

        ground_truth_path = os.path.join(self.benchmark_dir, "ground_truths", f"{object_basename}.json")
        ground_truth_text = read_file(ground_truth_path)

        if self.convert_truth_to_json:
            try:
                return json.loads(ground_truth_text)
            except json.JSONDecodeError as e:
                return {"error": "Invalid JSON format."}
        return {"response_text": ground_truth_text}

    @staticmethod
    def get_all_basenames(
            directories: Iterable[Union[str, Path]],
            page_pattern: Optional[Pattern] = None,
    ) -> List[str]:
        """
        Return all logical basenames across multiple directories.

        Parameters
        ----------
        directories : Iterable[str | Path]
            Directories to scan (non-recursive).
        page_pattern : Optional[regex]
            Regex matching a variable suffix (e.g. page number) that should be removed.
            If None: uses default "_p<digits>$" pattern.

        Returns
        -------
        List[str]
            Sorted list of unique basenames.
        """

        if page_pattern is None:
            # default pattern: _p001, _p1, _p00042 etc. just before extension
            page_pattern = re.compile(r"_p\d+$")

        basenames: Set[str] = set()

        for directory in directories:
            directory = Path(directory)
            if directory.is_dir():
                for item in directory.iterdir():
                    if not item.is_file():
                        continue

                    stem = item.stem  # filename without final .ext

                    # Strip page pattern if present
                    clean = page_pattern.sub("", stem)

                    basenames.add(clean)

        return sorted(basenames)

    @staticmethod
    def get_files_by_basename(
            directory: Union[str, Path],
            basename: Union[str, Pattern],
            group: bool = False,
            valid_extensions: Optional[List[str]] = None,
    ) -> List[Path]:
        """
        Return files in `directory` matching a given basename pattern.

        Parameters
        ----------
        directory : str or Path
            Directory to search (non-recursive).
        basename : str or compiled regex
            For exact match: 'xy'
            For group match: 'xy_' (matches xy_part1.ext, xy_part2.ext, ...)
        group : bool
            If False: exact basename.<ext>
            If True: basename*.<ext>, but only one final extension allowed.
        valid_extensions : list of str (optional)
            If provided, only files whose final extension is in the list are returned.

        Returns
        -------
        List[Path]
            Sorted list of full file paths.
        """
        directory = Path(directory)

        if isinstance(basename, str):
            if group:
                # basename*.<one-ext>
                pattern_str = rf"^{re.escape(basename)}[^.]*\.[^.]+$"
            else:
                # exact basename.<one-ext>
                pattern_str = rf"^{re.escape(basename)}\.[^.]+$"

            pattern = re.compile(pattern_str)
        else:
            pattern = basename  # custom regex already given

        matches: List[Path] = []

        for item in directory.iterdir():
            if item.is_file() and pattern.match(item.name):
                if valid_extensions:
                    if item.suffix.lower() in [e.lower() for e in valid_extensions]:
                        matches.append(item)
                else:
                    matches.append(item)

        return sorted(matches)

    def get_image_paths(self, object_basename: str) -> List[str]:
        """ Get the image paths for the object. """
        images_dir = os.path.join(self.benchmark_dir, 'images')
        if not os.path.exists(images_dir):
            return []
        paths = self.get_files_by_basename(images_dir, object_basename, group=self.multi_image_support)
        return [str(p) for p in paths]

    def get_text_paths(self, object_basename: str) -> List[str]:
        """ Get the text paths for the object. """
        texts_dir = os.path.join(self.benchmark_dir, 'texts')
        if not os.path.exists(texts_dir):
            return []
        paths = self.get_files_by_basename(texts_dir, object_basename, group=self.multi_text_support)
        return [str(p) for p in paths]

    def ask_llm(self, object_basename: str) -> LLMResponse:
        """ Ask the language model a question. """

        kwargs = {
            "temperature": self.temperature
        }
        image_paths = self.get_image_paths(object_basename)
        text_paths = self.get_text_paths(object_basename)
        self.prompt = self.load_prompt(object_basename)

        if image_paths:
            kwargs["images"] = image_paths
        if text_paths:
            kwargs["files"] = text_paths

        if self.dataclass:
            kwargs["response_format"] = self.dataclass

        # Add conversation continuation if shared context is enabled
        if self.use_shared_context and self.conversation_id:
            kwargs["conversation_id"] = self.conversation_id

        return self.client.prompt(self.model, self.prompt, **kwargs)

    def get_request_answer_path(self):
        return str(os.path.join('..', 'results', self.date, self.id))

    def get_request_answer_file_name(self, object_basename: str) -> str:
        """ Get the path to the answer file. """
        return os.path.join(self.get_request_answer_path(), self.get_request_name(object_basename) + ".json")

    def load_saved_answer(self, object_basename: str):
        """ Load a previously saved answer and score from file. """
        file_name = self.get_request_answer_file_name(object_basename)
        if not os.path.exists(file_name):
            return None, None

        try:
            answer_json_str = read_file(file_name)
            answer_data = json.loads(answer_json_str)
            score = answer_data.get('score', None)

            # Reconstruct Usage object
            usage_data = answer_data.get('usage', {})
            from ai_client.response import Usage
            from ai_client.pricing import calculate_cost

            input_cost = usage_data.get('input_cost_usd')
            output_cost = usage_data.get('output_cost_usd')
            estimated_cost = usage_data.get('estimated_cost_usd')

            # Recalculate costs if missing
            if input_cost is None or output_cost is None or estimated_cost is None:
                provider = answer_data.get('provider', '')
                model = answer_data.get('model', '')
                input_tokens = usage_data.get('input_tokens', 0)
                output_tokens = usage_data.get('output_tokens', 0)

                cost_result = calculate_cost(provider, model, input_tokens, output_tokens)
                if cost_result:
                    input_cost, output_cost, estimated_cost = cost_result

            usage = Usage(
                input_tokens=usage_data.get('input_tokens', 0),
                output_tokens=usage_data.get('output_tokens', 0),
                total_tokens=usage_data.get('total_tokens', 0),
                cached_tokens=usage_data.get('cached_tokens'),
                input_cost_usd=input_cost,
                output_cost_usd=output_cost,
                estimated_cost_usd=estimated_cost
            )

            # Reconstruct LLMResponse object
            timestamp_str = answer_data.get('timestamp')
            if timestamp_str:
                timestamp = datetime.fromisoformat(timestamp_str)
            else:
                timestamp = datetime.now()

            answer = LLMResponse(
                text=answer_data.get('text', ''),
                model=answer_data.get('model', ''),
                provider=answer_data.get('provider', ''),
                finish_reason=answer_data.get('finish_reason', ''),
                usage=usage,
                raw_response=answer_data.get('raw_response', {}),
                duration=answer_data.get('duration', 0.0),
                timestamp=timestamp,
                parsed=answer_data.get('parsed')
            )

            return answer, score
        except Exception as e:
            logging.warning(f"Failed to load saved answer for {object_basename}: {e}")
            return None, None

    def save_request_answer(self,
                            object_basename: str,
                            answer: LLMResponse,
                            score: dict) -> None:
        """ Save the answer to a file. """

        save_path = self.get_request_answer_path()
        os.makedirs(save_path, exist_ok=True)

        file_name = os.path.join(save_path,
                                 f"{self.get_request_name(object_basename)}.json")
        answer_json = answer.to_dict()
        answer_json['score'] = score
        try:
            raw_answer = answer.raw_response.json()
            answer_json['raw_response'] = raw_answer
        except Exception:
            logging.warning(f"Failed to save RAW answer for {object_basename}")

        write_file(file_name, answer_json)
        logging.info(f"Saved answer to {file_name}")

    def save_benchmark_score(self,
                             score: dict) -> None:
        """ Save the benchmark score to a file. """
        save_path = os.path.join('..', "results", self.date, self.id, "scoring.json")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        write_file(save_path, score)

    def prepare_scoring_data(self,
                             answer: LLMResponse) -> dict:
        """ Prepare the data for scoring. """
        return answer.parsed


    def get_shared_context_files(self) -> List[str]:
        """
        Return list of file paths to send as shared context.
        This context is sent once at the beginning and can be referenced in subsequent requests.

        Override this method in your benchmark to specify shared context files.

        Returns:
            List of absolute file paths (e.g., ['/path/to/context/essay.txt'])

        Example:
            return [os.path.join(self.benchmark_dir, 'context', 'reference_document.txt')]
        """
        return []

    def get_shared_context_prompt(self) -> str:
        """
        Return the initial prompt to accompany shared context.

        This prompt is sent with the shared context files to establish the conversation.
        It should explain what the context is and what task will follow.

        Override this method in your benchmark to specify the initial prompt.

        Returns:
            Prompt text as string

        Example:
            return '''I have provided you with an essay. Please read it carefully.
            In subsequent messages, I will ask you to analyze various texts in relation to this essay.'''
        """
        return ""

    def _establish_shared_context(self):
        """
        Establish shared context by sending initial request with context files.

        This is called automatically by run() if use_shared_context=True.
        """
        if self.shared_context_established:
            logging.debug("Shared context already established, skipping")
            return

        shared_files = self.get_shared_context_files()
        shared_prompt = self.get_shared_context_prompt()

        if not shared_files and not shared_prompt:
            logging.warning("use_shared_context=True but no context files or prompt provided")
            return

        logging.info(f"Establishing shared context with {len(shared_files)} file(s)")

        # Send initial request to establish context
        kwargs = {}
        if shared_files:
            kwargs["files"] = shared_files
            kwargs["cache_context"] = True  # Signal to AI client to enable caching

        try:
            # This establishes the conversation/cache
            response = self.client.prompt(
                self.model,
                shared_prompt,
                **kwargs
            )

            # Store conversation ID for subsequent requests
            if hasattr(response, 'conversation_id'):
                self.conversation_id = response.conversation_id
                logging.info(f"Shared context established. Conversation ID: {self.conversation_id}")
            else:
                logging.info("Shared context sent (no conversation ID returned)")

            self.shared_context_established = True

        except Exception as e:
            logging.error(f"Failed to establish shared context: {e}")
            raise

    def before_run(self):
        """ Hook to run before the benchmark starts. """
        pass

    def after_run(self):
        """ Hook to run after the benchmark ends. """
        pass

    def before_object(self, object_basename: str):
        """ Hook to run before processing each object. """
        pass

    def after_object(self, object_basename: str):
        """ Hook to run after processing each object. """
        pass

    def run(self, regenerate_existing_results=True):
        """Run the benchmark."""

        logging.info(f"Running {self.get_title()}...")
        if not self.is_runnable():
            logging.error(f"Skipping {self.get_title()} (not runnable).")
            return

        self.before_run()

        # Establish shared context if enabled
        if self.use_shared_context:
            self._establish_shared_context()

        images_dir = os.path.join(self.benchmark_dir, 'images')
        texts_dir = os.path.join(self.benchmark_dir, 'texts')
        object_basenames = self.get_all_basenames([images_dir, texts_dir],
                                                  page_pattern=re.compile(r"_p\d+$")) # TODO
        logging.info(f"Found {len(object_basenames)} objects to process.")

        # Process each object
        benchmark_scores = []
        all_answers = []
        for object_basename in object_basenames:

            answer_file_name = self.get_request_answer_file_name(object_basename)
            should_process = (regenerate_existing_results and os.path.exists(answer_file_name)) or \
                             (not os.path.exists(answer_file_name))
            should_process = should_process and (not self.skip_object(object_basename))

            self.before_object(object_basename)
            if should_process:
                logging.info(f"Processing {self.id}, {object_basename}...")
                answer = self.ask_llm(object_basename)
                ground_truth = self.load_ground_truth(object_basename)
                score = self.score_request_answer(object_basename, answer, ground_truth)
                self.save_request_answer(object_basename, answer, score)
                benchmark_scores.append(score)
                all_answers.append(answer)
                logging.info(f"Finished {object_basename} with score: {score}")
            else:
                logging.info(f"Skipping {self.id}, {object_basename}...")
                # Load existing saved results
                saved_answer, saved_score = self.load_saved_answer(object_basename)
                benchmark_scores.append(saved_score)
                all_answers.append(saved_answer)
            self.after_object(object_basename)

        # Score the benchmark
        benchmark_score = self.score_benchmark(benchmark_scores)
        logging.info(f"Benchmark score: {benchmark_score}")

        # Calculate cost based on usage tokens and pricing data
        cost_summary = self.calculate_cost(all_answers)
        benchmark_score['cost_summary'] = cost_summary
        logging.info(f"Cost summary: {cost_summary}")

        self.save_benchmark_score(benchmark_score)

        self.after_run()

    @staticmethod
    def calculate_cost(all_answers):
        total_output_tokens = 0
        total_input_tokens = 0
        total_cached_tokens = 0
        total_input_cost = 0.0
        total_output_cost = 0.0
        total_cost = 0.0

        for answer in all_answers:
            if answer is None:
                continue
            total_output_tokens += answer.usage.output_tokens
            total_input_tokens += answer.usage.input_tokens
            if answer.usage.cached_tokens:
                total_cached_tokens += answer.usage.cached_tokens
            if answer.usage.input_cost_usd:
                total_input_cost += answer.usage.input_cost_usd
            if answer.usage.output_cost_usd:
                total_output_cost += answer.usage.output_cost_usd
            if answer.usage.estimated_cost_usd:
                total_cost += answer.usage.estimated_cost_usd

        return {
            'total_input_tokens': total_input_tokens,
            'total_output_tokens': total_output_tokens,
            'total_tokens': total_input_tokens + total_output_tokens,
            'input_cost_usd': total_input_cost,
            'output_cost_usd': total_output_cost,
            'total_cost_usd': total_cost,
        }

    def get_request_name(self, object_basename: str) -> str:
        """ Get the name of the request. """
        return f"request_{self.id}_{object_basename}"


    @abstractmethod
    def score_request_answer(self,
                             object_basename: str,
                             response: LLMResponse,
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


    def convert_truth_to_json(self) -> bool:
        """If the result is a JSON string, convert it to a JSON object."""
        return True

    def resize_images(self) -> bool:
        """If images are too large, resize them before sending to the model."""
        return False

    def get_title(self) -> str:
        """Title of the benchmark. Used in the result table."""
        return f"{self.name} ({self.provider}/{self.model})"

    def get_prompt_kwargs(self,
                          filename: str) -> Dict:
        """If the prompt file contains file information."""
        return {}

    def skip_object(self,
                    object_basename: str) -> bool:
        """ Skip object. """
        return False


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
