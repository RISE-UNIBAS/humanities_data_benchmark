"""Unit tests for the run-cost guardrails on Benchmark.

Both mechanisms exist because of the qwen/qwen3.8-27b run of 2026-09-08, which billed
roughly $100 for 5 of 15 benchmarks: uncapped generations ran to the model's full
131,072-token ceiling, and a 402 was retried for hours after the credits were gone.
See dev/DEPENDENCY_PATCHES.md.
"""
import threading
from pathlib import Path
from unittest.mock import patch

import pytest

from ai_client import LLMResponse, Usage
import benchmark_base as bb


BASE_CONFIG = dict(id="T9999", name="library_cards", provider="openrouter",
                   model="test/model", role_description="", prompt_file="prompt.txt",
                   dataclass="", temperature="0.0", rules="")
BENCHMARK_DIR = Path(__file__).resolve().parents[1] / "benchmarks" / "library_cards"


def _error(message):
    return LLMResponse(text="", model="m", provider="openrouter", finish_reason="error",
                       usage=Usage(), raw_response={"error": message}, duration=0.0)


def _make(config_overrides=None, cls=None):
    """Build a benchmark with the AI client stubbed out, returning it and the kwargs used."""
    captured = {}

    def fake_create(provider, api_key, **kwargs):
        captured.update(kwargs)
        return object()

    config = dict(BASE_CONFIG, **(config_overrides or {}))
    with patch.object(bb, "create_ai_client", fake_create):
        benchmark = (cls or bb.DefaultBenchmark)(config, "key", BENCHMARK_DIR)
    return benchmark, captured


class TestMaxTokensCap:
    def test_default_cap_is_sent(self):
        _, kwargs = _make()
        assert kwargs["max_tokens"] == bb.DEFAULT_MAX_OUTPUT_TOKENS

    def test_default_cap_is_well_below_a_full_context_window(self):
        # 131072 is what the 2026-09-08 runaway generations actually billed.
        assert bb.DEFAULT_MAX_OUTPUT_TOKENS < 131072

    def test_rules_override_wins(self):
        _, kwargs = _make({"rules": '{"max_tokens": 4096}'})
        assert kwargs["max_tokens"] == 4096

    def test_subclass_attribute_raises_the_ceiling(self):
        class Roomy(bb.DefaultBenchmark):
            max_output_tokens = 98304

        _, kwargs = _make(cls=Roomy)
        assert kwargs["max_tokens"] == 98304

    def test_rules_override_beats_subclass_attribute(self):
        class Roomy(bb.DefaultBenchmark):
            max_output_tokens = 98304

        _, kwargs = _make({"rules": '{"max_tokens": 1234}'}, cls=Roomy)
        assert kwargs["max_tokens"] == 1234

    def test_genai_uses_its_own_parameter_name(self):
        _, kwargs = _make({"provider": "genai"})
        assert kwargs["max_output_tokens"] == bb.DEFAULT_MAX_OUTPUT_TOKENS
        assert "max_tokens" not in kwargs


class TestFatalProviderErrorDetection:
    @pytest.mark.parametrize("message", [
        "Error code: 402 - {'error': {'message': 'Insufficient credits.'}}",
        "Error code: 401 - invalid_api_key",
        "Error code: 403 - forbidden",
    ])
    def test_unrecoverable_errors_are_fatal(self, message):
        assert bb.Benchmark._is_fatal_provider_error(_error(message)) is True

    @pytest.mark.parametrize("message", [
        "Error code: 429 - rate limit exceeded",
        "Error code: 500 - internal server error",
        "Connection error.",
    ])
    def test_transient_errors_stay_retryable(self, message):
        assert bb.Benchmark._is_fatal_provider_error(_error(message)) is False

    @pytest.mark.parametrize("finish_reason", ["stop", "length"])
    def test_non_error_answers_are_never_fatal(self, finish_reason):
        answer = LLMResponse(text="", model="m", provider="openrouter",
                             finish_reason=finish_reason, usage=Usage(),
                             raw_response={}, duration=0.0)
        assert bb.Benchmark._is_fatal_provider_error(answer) is False

    def test_missing_answer_is_not_fatal(self):
        assert bb.Benchmark._is_fatal_provider_error(None) is False


class TestRunAbortsOnFatalError:
    def _run_with_fatal_error(self, workers):
        benchmark, _ = _make()
        calls, saved = [], []
        lock = threading.Lock()

        def fake_ask(basename):
            with lock:
                calls.append(basename)
            return _error("Error code: 402 - Insufficient credits")

        benchmark.ask_llm = fake_ask
        benchmark.save_request_answer = lambda *a, **k: saved.append(a)
        benchmark.save_benchmark_score = lambda *a, **k: saved.append(("score",) + a)

        with pytest.raises(bb.FatalProviderError):
            benchmark.run(regenerate_existing_results=True, workers=workers)
        return calls, saved

    @pytest.mark.parametrize("workers", [1, 10])
    def test_stops_far_short_of_the_full_object_list(self, workers):
        calls, _ = self._run_with_fatal_error(workers)
        # library_cards has 263 objects; only the in-flight batch should get through.
        assert 0 < len(calls) <= workers

    @pytest.mark.parametrize("workers", [1, 10])
    def test_writes_nothing(self, workers):
        # An error file would count as a finished object and be skipped on resume.
        _, saved = self._run_with_fatal_error(workers)
        assert saved == []
