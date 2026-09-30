"""Unit tests for the pure/static helpers on Benchmark."""
import re
from types import SimpleNamespace

import pytest

from ai_client import LLMResponse, Usage
from ai_client import pricing as ai_pricing
from benchmark_base import Benchmark


def _touch(directory, *names):
    for n in names:
        (directory / n).write_text("", encoding="utf-8")


class TestGetAllBasenames:
    def test_strips_page_suffix_with_custom_pattern(self, tmp_path):
        _touch(tmp_path, "doc_p001.jpg", "doc_p002.jpg", "other.jpg")
        result = Benchmark.get_all_basenames([tmp_path], page_pattern=re.compile(r"_p\d+$"))
        assert result == ["doc", "other"]  # doc_p001/doc_p002 collapse to one

    def test_default_pattern_passes_through_plain_stems(self, tmp_path):
        _touch(tmp_path, "b.jpg", "a.jpg")
        assert Benchmark.get_all_basenames([tmp_path]) == ["a", "b"]  # sorted

    def test_dedupes_across_directories(self, tmp_path):
        d1, d2 = tmp_path / "d1", tmp_path / "d2"
        d1.mkdir(); d2.mkdir()
        _touch(d1, "shared_p1.jpg")
        _touch(d2, "shared_p2.txt")
        result = Benchmark.get_all_basenames([d1, d2], page_pattern=re.compile(r"_p\d+$"))
        assert result == ["shared"]

    def test_missing_directory_ignored(self, tmp_path):
        _touch(tmp_path, "a.jpg")
        result = Benchmark.get_all_basenames([tmp_path, tmp_path / "does_not_exist"])
        assert result == ["a"]


class TestGetFilesByBasename:
    def test_exact_match_excludes_prefixed(self, tmp_path):
        _touch(tmp_path, "foo.txt", "foo.json", "foo_bar.txt", "other.txt")
        result = sorted(p.name for p in Benchmark.get_files_by_basename(tmp_path, "foo"))
        assert result == ["foo.json", "foo.txt"]

    def test_group_match_includes_prefixed(self, tmp_path):
        _touch(tmp_path, "foo.txt", "foo.json", "foo_bar.txt", "other.txt")
        result = sorted(p.name for p in Benchmark.get_files_by_basename(tmp_path, "foo", group=True))
        assert result == ["foo.json", "foo.txt", "foo_bar.txt"]

    def test_valid_extensions_filter_case_insensitive(self, tmp_path):
        _touch(tmp_path, "foo.TXT", "foo.json")
        result = sorted(p.name for p in Benchmark.get_files_by_basename(
            tmp_path, "foo", valid_extensions=[".txt"]))
        assert result == ["foo.TXT"]

    def test_custom_regex(self, tmp_path):
        _touch(tmp_path, "img01.jpg", "img02.jpg", "doc.txt")
        pattern = re.compile(r"^img\d+\.jpg$")
        result = sorted(p.name for p in Benchmark.get_files_by_basename(tmp_path, pattern))
        assert result == ["img01.jpg", "img02.jpg"]

    def test_subdirectories_ignored(self, tmp_path):
        _touch(tmp_path, "foo.txt")
        (tmp_path / "foo.d").mkdir()  # directory matching the pattern must be skipped
        result = [p.name for p in Benchmark.get_files_by_basename(tmp_path, "foo", group=True)]
        assert result == ["foo.txt"]


def _answer(**usage_kwargs):
    return SimpleNamespace(usage=Usage(**usage_kwargs))


class TestCalculateCost:
    def test_sums_tokens_and_costs(self):
        answers = [
            _answer(input_tokens=10, output_tokens=5, cached_tokens=2,
                    input_cost_usd=0.1, output_cost_usd=0.2, estimated_cost_usd=0.3),
            _answer(input_tokens=20, output_tokens=10, cached_tokens=3,
                    input_cost_usd=0.4, output_cost_usd=0.5, estimated_cost_usd=0.9),
        ]
        result = Benchmark.calculate_cost(answers)
        assert result["total_input_tokens"] == 30
        assert result["total_output_tokens"] == 15
        assert result["total_tokens"] == 45
        assert result["input_cost_usd"] == pytest.approx(0.5)
        assert result["output_cost_usd"] == pytest.approx(0.7)
        assert result["total_cost_usd"] == pytest.approx(1.2)

    def test_skips_none_answers(self):
        answers = [
            None,
            _answer(input_tokens=5, output_tokens=5, estimated_cost_usd=0.1),
        ]
        result = Benchmark.calculate_cost(answers)
        assert result["total_input_tokens"] == 5
        assert result["total_cost_usd"] == pytest.approx(0.1)

    def test_none_cost_fields_contribute_zero(self):
        # Usage defaults leave cost fields None; tokens still sum.
        answers = [_answer(input_tokens=7, output_tokens=3)]
        result = Benchmark.calculate_cost(answers)
        assert result["total_tokens"] == 10
        assert result["input_cost_usd"] == 0.0
        assert result["output_cost_usd"] == 0.0
        assert result["total_cost_usd"] == 0.0

    def test_empty_list_all_zeros(self):
        result = Benchmark.calculate_cost([])
        assert result == {
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_tokens": 0,
            "input_cost_usd": 0.0,
            "output_cost_usd": 0.0,
            "total_cost_usd": 0.0,
        }


class TestCalculateCostReasoning:
    def test_reasoning_is_totalled_beside_the_existing_keys(self):
        answers = [
            _answer(input_tokens=10, output_tokens=5, reasoning_tokens=100,
                    reasoning_cost_usd=0.01, estimated_cost_usd=0.02),
            _answer(input_tokens=10, output_tokens=5, reasoning_tokens=0,
                    reasoning_cost_usd=0.0, estimated_cost_usd=0.01),
        ]
        result = Benchmark.calculate_cost(answers)
        assert result["total_reasoning_tokens"] == 100
        assert result["reasoning_cost_usd"] == pytest.approx(0.01)
        assert result["total_tokens"] == 30, "total_tokens stays input + output"
        assert result["total_cost_usd"] == pytest.approx(0.03)

    def test_unpriced_reasoning_is_null_not_free(self):
        result = Benchmark.calculate_cost([_answer(input_tokens=1, reasoning_tokens=50)])
        assert result["total_reasoning_tokens"] == 50
        assert result["reasoning_cost_usd"] is None

    def test_no_reasoning_adds_no_keys(self):
        result = Benchmark.calculate_cost([_answer(input_tokens=1, reasoning_tokens=0)])
        assert "total_reasoning_tokens" not in result and "reasoning_cost_usd" not in result


class _Stored(Benchmark):
    """Enough of a Benchmark to reload an answer file."""

    def score_request_answer(self, object_basename, response, ground_truth):
        return {}

    def score_benchmark(self, all_scores):
        return {}


@pytest.fixture
def stored(tmp_path, monkeypatch):
    """Write a request file as save_request_answer would, and reload it."""
    table = tmp_path / "pricing.json"
    table.write_text('{"pricing": {"2026-09-01": {"huggingface": {"org/Model:prov": '
                     '{"input_price": 1.0, "output_price": 2.0}}}}}', encoding="utf-8")
    monkeypatch.setattr(ai_pricing, "_pricing_manager", ai_pricing.PricingManager(str(table)))

    benchmark = _Stored.__new__(_Stored)
    benchmark.provider, benchmark.model = "huggingface", "org/Model:prov"
    path = tmp_path / "request.json"
    monkeypatch.setattr(benchmark, "get_request_answer_file_name", lambda name: str(path))

    def _reload(usage, model="org/model-echoed"):
        answer = LLMResponse(text="{}", model=model, provider="huggingface",
                             finish_reason="stop", usage=usage, raw_response={})
        path.write_text(__import__("json").dumps(dict(answer.to_dict(), score={"f1": 1})),
                        encoding="utf-8")
        reloaded, score = benchmark.load_saved_answer("object")
        assert score == {"f1": 1}
        return reloaded.usage
    return _reload


class TestLoadSavedAnswer:
    def test_every_recorded_field_survives_a_resume(self, stored):
        original = Usage(input_tokens=10, output_tokens=5, total_tokens=115, reasoning_tokens=100,
                         cache_creation_tokens=7, cache_read_tokens=3, input_cost_usd=0.1,
                         output_cost_usd=0.2, reasoning_cost_usd=0.3, estimated_cost_usd=0.6,
                         attempts=2, discarded_input_tokens=9, discarded_output_tokens=4,
                         discarded_cost_usd=0.05)
        assert stored(original) == original

    def test_a_billed_total_without_components_is_not_repriced(self, stored):
        usage = stored(Usage(input_tokens=1000, output_tokens=1000, total_tokens=2000,
                             estimated_cost_usd=0.1234), model="org/Model:prov")
        assert usage.estimated_cost_usd == 0.1234
        assert usage.input_cost_usd is None and usage.output_cost_usd is None

    def test_a_stored_total_is_what_the_run_observed(self, stored):
        usage = stored(Usage(input_tokens=1000, output_tokens=1000, total_tokens=2000,
                             input_cost_usd=0.5, output_cost_usd=0.5, estimated_cost_usd=1.0))
        assert usage.estimated_cost_usd == 1.0

    def test_a_missing_total_is_priced_on_the_configured_model(self, stored):
        usage = stored(Usage(input_tokens=1000, output_tokens=1000, total_tokens=3000,
                             reasoning_tokens=1000))
        assert usage.estimated_cost_usd == pytest.approx((1000 * 1 + 1000 * 2 + 1000 * 2) / 1e6)
        assert usage.reasoning_cost_usd == pytest.approx(0.002)

    def test_a_pre_0_5_record_still_loads(self, stored):
        usage = stored(Usage(input_tokens=1000, output_tokens=1000, total_tokens=2000))
        assert usage.reasoning_tokens is None
        assert usage.estimated_cost_usd == pytest.approx(0.003)
