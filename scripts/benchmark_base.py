""" This module contains the base class for all benchmark workflows. """
import importlib
import json
import logging
import os
import re
import threading
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Union, Pattern, Optional, Iterable, Set
from data_loader import read_file, write_file
from ai_client import create_ai_client, LLMResponse, Usage, deepseek_client
from ai_client.pricing import calculate_cost, set_pricing_file
from local import is_local_provider, get_backend
from local.backends.base import LocalRequest

logger = logging.getLogger(__name__)

# TODO: hotfix, to be fixed in generic-llm-api-client
# 0.4.6 ships ("vl", "vision"), which misses deepseek-flash.
DEEPSEEK_VISION_MODEL_KEYWORDS = ("deepseek-flash",)
deepseek_client._VISION_MODEL_KEYWORDS = tuple(dict.fromkeys(
    deepseek_client._VISION_MODEL_KEYWORDS + DEEPSEEK_VISION_MODEL_KEYWORDS))

_PRICING_FILE = Path(__file__).parent / "data" / "pricing.json"
if _PRICING_FILE.exists():
    set_pricing_file(str(_PRICING_FILE))
else:
    logger.warning("Pricing table not found at %s; falling back to the ai_client bundled "
                   "table, which may not price newer models at all.", _PRICING_FILE)


# TODO: hotfix, to be fixed in generic-llm-api-client
def _send_cap_as_max_completion_tokens(client):
    """Rename max_tokens to max_completion_tokens on OpenAI's chat endpoints.

    gpt-5 and newer 400 on max_tokens; ai_client 0.4.6 hard-codes the name. See
    dev/DEPENDENCY_PATCHES.md section 8.
    """
    api_client = getattr(client, "api_client", None)
    if api_client is None:
        return
    endpoints = []
    for attribute in ("chat", "beta"):
        section = getattr(api_client, attribute, None)
        completions = getattr(getattr(section, "chat", section), "completions", None)
        if completions is not None:
            endpoints.append(completions)

    for endpoint in endpoints:
        for method_name in ("create", "parse"):
            original = getattr(endpoint, method_name, None)
            if original is None or getattr(original, "_renames_token_cap", False):
                continue

            def renaming(*args, _original=original, **kwargs):
                if "max_tokens" in kwargs:
                    kwargs["max_completion_tokens"] = kwargs.pop("max_tokens")
                return _original(*args, **kwargs)

            renaming._renames_token_cap = True
            try:
                setattr(endpoint, method_name, renaming)
            except AttributeError:
                logger.warning("Could not rename max_tokens on %s.%s; gpt-5 class models "
                               "will fail with 400 Unsupported parameter",
                               type(endpoint).__name__, method_name)


DEFAULT_MAX_OUTPUT_TOKENS = 16384
"""Output ceiling when nothing else asks for more; caps the cost of a repetition loop."""

MODEL_LONG_OUTPUT = {
    # Raises the default for models whose long answers finish `stop` and score.
    "deepseek-flash": 32768,
}

# Per-model ceiling, clamping whatever cap the default, MODEL_LONG_OUTPUT or the rules produce.
# Above it a provider refuses the request outright. Listed only where it binds.
MODEL_MAX_OUTPUT_TOKENS = {
    "gpt-4o": 16384,
    "gpt-4o-mini": 16384,
    "gpt-4.1": 32768,
    "gpt-4.1-mini": 32768,
    "gpt-4.1-nano": 32768,
    # publicai counts the cap against its capacity budget; largest answer on record is 3,560.
    "swiss-ai/Apertus-v1.5-70B:publicai": 4096,
    "swiss-ai/Apertus-v1.5-8B:publicai": 4096,
    # Cohere: 400 TOO_MANY_TOKENS above these.
    "command-r-08-2024": 4096,
    "command-r-plus-08-2024": 4096,
    "command-r7b-12-2024": 4096,
    "command-a-03-2025": 8192,
    "command-a-vision-07-2025": 8192,
    # Anthropic: 400 above 64,000 on these three; later Claude models allow 128,000.
    "claude-haiku-4-5-20251001": 64000,
    "claude-opus-4-5-20251101": 64000,
    "claude-sonnet-4-5-20250929": 64000,
    # Loop to whatever cap they get, so they stay clamped when a benchmark raises it.
    "qwen/qwen3.5-9b": 16384,
    "qwen/qwen3.5-27b": 16384,
    "qwen/qwen3.5-35b-a3b": 16384,
    "qwen/qwen3.5-122b-a10b": 16384,
    "qwen/qwen3.5-397b-a17b": 16384,
    "qwen/qwen3.5-flash-02-23": 16384,
    "qwen/qwen3.5-plus-02-15": 16384,
    "meta/muse-spark-1.2": 16384,
    "meta/muse-spark-1.3": 16384,
}

# Provider errors that no amount of retrying will fix. Matched against the message
# stored in LLMResponse.raw_response['error'] by the client's error path.
FATAL_ERROR_MARKERS = (
    "Error code: 402",
    "Error code: 401",
    "Error code: 403",
    "Insufficient credits",
    "invalid_api_key",
)


class FatalProviderError(RuntimeError):
    """ Raised when a run is aborted because the provider rejected the request outright. """


class Benchmark(ABC):
    """ Base class for all benchmark workflows. """

    multi_image_support = False
    multi_text_support = False
    use_shared_context = False  # Enable multi-stage requests with shared context (conversation-based)
    cache_context_per_request = False  # Enable per-request caching of context files/images
    # Score an unparseable answer as a miss instead of dropping it from the denominator.
    score_unparseable_as_miss = False
    max_output_tokens = DEFAULT_MAX_OUTPUT_TOKENS  # Per-request output ceiling; raise per benchmark if needed

    def __init__(self, config, api_key, benchmark_directory):
        """ Initialize the benchmark. """

        self.id = config.get('id')                          # Unique Test ID 'T0001'
        self.name = config.get('name')                      # Unique benchmark dataset name (=directory name)
        self.benchmark_dir = benchmark_directory            # Path to the benchmark directory
        self.provider = config['provider']                  # AI provider
        self.model = config['model']                        # Model name
        self.api_key = api_key                              # API key for the provider
        self.role_description = config.get('role_description')  # Role description for the system prompt
        self.prompt_file = config['prompt_file']            # Prompt file name
        # Results folder to read and write; BENCHMARK_RUN_DATE pins it across midnight.
        self.date = os.environ.get('BENCHMARK_RUN_DATE') \
            or datetime.now().strftime('%Y-%m-%d')
        try:                                                # Temperature setting for the model
            self.temperature = float(config.get('temperature', 0.5))
        except (ValueError, TypeError):
            self.temperature = 0.5

        # TODO: hotfix, to be fixed in generic-llm-api-client
        if self.model in ["gpt-5", "gpt-5-mini", "gpt-5-nano", "gpt-5.1-2025-11-13", "gpt-5.2", "o3", "gpt-5.5-2026-04-23", "gpt-5.3-codex", "gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna", "gpt-6-astra"]:
            self.temperature = 1
        if self.model in ["claude-opus-4-7", "claude-opus-4-8", "claude-sonnet-5", "claude-fable-5", "claude-fable-5-1", "claude-opus-5"]:
            self.temperature = None

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
            try:
                self.rules = json.loads(config['rules'])
            except json.JSONDecodeError as e:
                logging.error(f"Invalid JSON in rules for {self.name}: {e}")
                self.rules = None

        if is_local_provider(self.provider):
            self.client = None
            self.local_backend = get_backend(self.provider)
        else:
            self.local_backend = None
            kwargs = {}
            if self.dataclass:
                kwargs["dataclass"] = self.dataclass
            if self.rules and "api_style" in self.rules and self.rules["api_style"]:
                kwargs["api_style"] = self.rules["api_style"]
            base_url = self.rules.get("base_url") if self.rules else None
            # Without a cap the provider default applies: for reasoning models, the whole
            # context window. A rules override or the benchmark's own value takes precedence.
            cap = (self.rules or {}).get("max_tokens") or self.max_output_tokens
            if cap == DEFAULT_MAX_OUTPUT_TOKENS and self.model in MODEL_LONG_OUTPUT:
                cap = MODEL_LONG_OUTPUT[self.model]
            ceiling = MODEL_MAX_OUTPUT_TOKENS.get(self.model)
            if ceiling is not None and cap > ceiling:
                logger.info("Clamping the output cap for %s from %d to its ceiling of %d",
                            self.model, cap, ceiling)
                cap = ceiling
            kwargs["max_output_tokens" if self.provider == "genai" else "max_tokens"] = cap
            self.client = create_ai_client(self.provider,
                                           self.api_key,
                                           system_prompt=self.role_description,
                                           base_url=base_url,
                                           **kwargs)
            if self.provider == "openai":
                _send_cap_as_max_completion_tokens(self.client)

        # Shared context support (for multi-stage requests)
        self.conversation_id = None  # Track conversation for subsequent requests
        self.shared_context_established = False

        # Set when a provider error makes the rest of the run pointless (see FATAL_ERROR_MARKERS)
        self._abort = threading.Event()

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
        if self.provider not in ["openai", "genai", "anthropic", "mistral", "openrouter", "scicore", "cohere", "deepseek", "x-ai", "alibaba", "huggingface"] \
                and not is_local_provider(self.provider):
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
        prompt_kwargs = self.get_prompt_kwargs(object_basename, self.get_image_paths(object_basename) + self.get_text_paths(object_basename))
        if prompt_kwargs:
            try:
                prompt = prompt.format(**prompt_kwargs)
            except KeyError as e:
                logging.error(f"Missing key in prompt formatting: {e}")

        if self.rules and self.rules.get("api_style") == "responses" and self.dataclass:
            dc_string = self.dataclass.model_json_schema()
            prompt += f"\n\nPlease respond with a JSON matching this exact schema: {json.dumps(dc_string)}"
            logging.debug(f"Extended prompt with dataclass schema for responses API style")

        logging.info("Final prompt:\n" + prompt)
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
            page_pattern = re.compile(r"____p\d+$")

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
        prompt = self.load_prompt(object_basename)  # local var avoids race condition in parallel runs

        # Add per-request cached context if enabled
        if self.cache_context_per_request:
            context_images = self.get_shared_context_images()
            context_files = self.get_shared_context_files()

            # Combine context images with per-object images (context first)
            if context_images:
                image_paths = context_images + (image_paths if image_paths else [])
                kwargs["cache"] = True  # Enable caching for context

            # Combine context files with per-object files (context first)
            if context_files:
                text_paths = context_files + (text_paths if text_paths else [])
                kwargs["cache"] = True  # Enable caching for context

        if image_paths:
            kwargs["images"] = image_paths
        if text_paths:
            kwargs["files"] = text_paths

        if self.dataclass and not (self.rules and self.rules.get("api_style") == "responses"):
            kwargs["response_format"] = self.dataclass

        # Add conversation continuation if shared context is enabled
        if self.use_shared_context and self.conversation_id:
            kwargs["conversation_id"] = self.conversation_id

        # Dispatch to local backend if applicable
        if self.local_backend is not None:
            return self.local_backend.run(LocalRequest(
                prompt=prompt,
                images=image_paths,
                files=text_paths,
                dataclass=self.dataclass,
                temperature=self.temperature,
            ))

        return self.client.prompt(self.model, prompt, **kwargs)

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

        if answer is None:
            logging.warning(f"No answer to save for {object_basename}")
            return

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

    def get_shared_context_images(self) -> List[str]:
        """
        Return list of image paths to include in shared context (cached).

        These images will be sent once and cached for all subsequent requests.
        Perfect for reference images like signature guides or style examples.

        Override this method in your benchmark to specify context images.

        Returns:
            List of absolute paths to image files

        Example:
            return [os.path.join(self.benchmark_dir, 'context', 'signature_reference.jpg')]
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
        Establish shared context by sending initial request with context files and/or images.

        This is called automatically by run() if use_shared_context=True.
        """
        if self.shared_context_established:
            logging.debug("Shared context already established, skipping")
            return

        shared_files = self.get_shared_context_files()
        shared_images = self.get_shared_context_images()
        shared_prompt = self.get_shared_context_prompt()

        if not shared_files and not shared_images and not shared_prompt:
            logging.warning("use_shared_context=True but no context files, images, or prompt provided")
            return

        file_count = len(shared_files)
        image_count = len(shared_images)
        logging.info(f"Establishing shared context with {file_count} file(s) and {image_count} image(s)")

        # Send initial request to establish context
        kwargs = {}
        if shared_files:
            kwargs["files"] = shared_files
            kwargs["cache"] = True  # Enable caching for files
        if shared_images:
            kwargs["images"] = shared_images
            kwargs["cache"] = True  # Enable caching for images

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

    def get_basename_pattern(self) -> Optional[Pattern[str]]:
        return None

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

    @staticmethod
    def _is_fatal_provider_error(answer: LLMResponse) -> bool:
        """ Check whether a failed answer carries a provider error that retrying cannot fix. """
        if answer is None or answer.finish_reason != "error":
            return False
        message = str((answer.raw_response or {}).get("error", ""))
        return any(marker in message for marker in FATAL_ERROR_MARKERS)

    def _process_object(self, object_basename: str, regenerate_existing_results: bool):
        """Process a single object (request + score). Safe to run in parallel threads."""
        if self._abort.is_set():
            return None, None

        prefix = f"[{object_basename}]"
        answer_file_name = self.get_request_answer_file_name(object_basename)
        should_process = (regenerate_existing_results and os.path.exists(answer_file_name)) or \
                         (not os.path.exists(answer_file_name))
        should_process = should_process and (not self.skip_object(object_basename))

        self.before_object(object_basename)
        if should_process:
            logging.info(f"{prefix} Processing {self.id}, {object_basename}...")
            answer = self.ask_llm(object_basename)
            if self._is_fatal_provider_error(answer):
                # Not saved: an error file would count as finished and be skipped on resume.
                logging.critical(f"{prefix} Fatal provider error for {self.id}, aborting run: "
                                 f"{(answer.raw_response or {}).get('error', '')}")
                self._abort.set()
                return None, None
            if answer is None:
                logging.error(f"{prefix} LLM returned None for {self.id}, {object_basename}")
                score = None
            elif self.dataclass and answer.parsed is None and not self.score_unparseable_as_miss:
                logging.error(f"{prefix} No parseable JSON for {self.id}, {object_basename} "
                              f"(truncated, empty or non-JSON completion); scoring skipped")
                score = None
            else:
                ground_truth = self.load_ground_truth(object_basename)
                score = self.score_request_answer(object_basename, answer, ground_truth)
            self.save_request_answer(object_basename, answer, score)
            logging.info(f"{prefix} Finished with score: {score}")
        else:
            logging.info(f"{prefix} Skipping {self.id}, {object_basename}...")
            answer, score = self.load_saved_answer(object_basename)
        self.after_object(object_basename)
        return answer, score

    def run(self, regenerate_existing_results=True, workers=1):
        """Run the benchmark.

        Args:
            regenerate_existing_results: Re-run requests that already have saved results.
            workers: Number of parallel worker threads. Values >1 speed up LLM-bound runs
                     significantly. Requires use_shared_context=False.
        """

        logging.info(f"Running {self.get_title()}...")
        if not self.is_runnable():
            logging.error(f"Skipping {self.get_title()} (not runnable).")
            return

        if workers > 1 and self.use_shared_context:
            logging.warning("workers > 1 is not supported with use_shared_context=True; falling back to 1 worker.")
            workers = 1

        self.before_run()

        # Establish shared context if enabled
        if self.use_shared_context:
            self._establish_shared_context()

        images_dir = os.path.join(self.benchmark_dir, 'images')
        texts_dir = os.path.join(self.benchmark_dir, 'texts')
        object_basenames = self.get_all_basenames([images_dir, texts_dir],
                                                  page_pattern=self.get_basename_pattern())
        logging.info(f"Found {len(object_basenames)} objects to process (workers={workers}).")

        # Process objects — serially or in parallel
        if workers > 1:
            results = self._run_parallel(object_basenames, regenerate_existing_results, workers)
        else:
            results = [self._process_object(bn, regenerate_existing_results) for bn in object_basenames]

        if self._abort.is_set():
            # Raised before scoring so a truncated run is never written out as a result.
            raise FatalProviderError(
                f"{self.get_title()} aborted on a fatal provider error; no score saved.")

        all_answers = [r[0] for r in results]
        benchmark_scores = [r[1] for r in results if r[1] is not None]

        # Score the benchmark
        benchmark_score = self.score_benchmark(benchmark_scores)
        logging.info(f"Benchmark score: {benchmark_score}")

        # Calculate cost based on usage tokens and pricing data
        cost_summary = self.calculate_cost(all_answers)
        benchmark_score['cost_summary'] = cost_summary
        logging.info(f"Cost summary: {cost_summary}")

        self.save_benchmark_score(benchmark_score)

        self.after_run()

    def _run_parallel(self, object_basenames: List[str], regenerate_existing_results: bool, workers: int):
        """Run object processing in parallel, returning results in original order."""
        results = [None] * len(object_basenames)
        futures = {}
        with ThreadPoolExecutor(max_workers=workers) as executor:
            for i, basename in enumerate(object_basenames):
                future = executor.submit(self._process_object, basename, regenerate_existing_results)
                futures[future] = i
            for future in as_completed(futures):
                i = futures[future]
                try:
                    results[i] = future.result()
                except Exception as e:
                    logging.error(f"[{object_basenames[i]}] Failed with exception: {e}")
                    results[i] = (None, None)
        return results

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
        """ Score the response.

        The returned dict is stored verbatim in the request answer file, so every value
        in it must be JSON-serializable -- plain strings and numbers, not the objects
        the scorer compared.

        Besides its metrics, it should carry `field_scores`: what this scorer compared,
        keyed by whatever unit it compares (a field name, a folio reference, a matched
        box). Each entry is

            {"response": <value seen>, "ground_truth": <value expected>, "score": <0..1>}

        with `score` None where the scorer states its verdict some other way -- counts
        of true and false positives, say -- rather than as a per-field similarity. Extra
        scalar keys are kept and shown alongside.

        This is what lets a comparison view report the scorer's own judgement. Each
        benchmark matches differently -- by box overlap, by folio position, against a
        fuzzy threshold -- so an independent diff would contradict the score beside it.
        Enforced by tests/integrity/test_field_scores_integrity.py; consumed by
        scripts/generate_test_report.py and the run-comparison widget.
        """
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
                          basename: str,
                          filenames: List[str]) -> Dict:
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
