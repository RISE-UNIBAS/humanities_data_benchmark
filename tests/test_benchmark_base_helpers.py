"""Unit tests for the pure/static helpers on Benchmark."""
import re
from types import SimpleNamespace

import pytest

from ai_client import Usage
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
