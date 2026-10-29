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


class TestRecordedVersion:
    """What a run records in scoring.json `benchmark_version`."""

    @pytest.fixture
    def repo(self, tmp_path, monkeypatch):
        import subprocess
        import benchmark_base
        folder = tmp_path / "benchmarks" / "letters"
        folder.mkdir(parents=True)
        (folder / "meta.json").write_text('{"versions": [{"version": "2.0.0"}, {"version": "1.0.0"}]}',
                                          encoding="utf-8")
        (tmp_path / "other.txt").write_text("x", encoding="utf-8")
        for args in (["init", "-q"], ["add", "."],
                     ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "c"]):
            subprocess.run(["git", *args], cwd=tmp_path, check=True)
        monkeypatch.setattr(benchmark_base, "_REPO_ROOT", tmp_path)
        return folder

    def test_a_clean_benchmark_records_its_newest_version_and_commit(self, repo):
        from benchmark_base import recorded_version
        (repo.parent.parent / "other.txt").write_text("changed", encoding="utf-8")  # outside the benchmark
        stamp = recorded_version(repo)
        assert stamp["version"] == "2.0.0" and len(stamp["commit"]) == 40 and stamp["uncommitted"] == []

    def test_changed_and_new_files_of_the_benchmark_are_listed(self, repo):
        from benchmark_base import recorded_version
        (repo / "meta.json").write_text('{"versions": [{"version": "3.0.0"}]}', encoding="utf-8")
        (repo / "prompt_new.txt").write_text("p", encoding="utf-8")
        stamp = recorded_version(repo)
        assert stamp["version"] == "3.0.0"
        assert stamp["uncommitted"] == ["benchmarks/letters/meta.json", "benchmarks/letters/prompt_new.txt"]

    def test_without_git_only_the_version_is_known(self, tmp_path, monkeypatch):
        import benchmark_base
        folder = tmp_path / "letters"
        folder.mkdir()
        (folder / "meta.json").write_text('{"versions": [{"version": "1.0.0"}]}', encoding="utf-8")
        monkeypatch.setattr(benchmark_base, "_REPO_ROOT", tmp_path)
        monkeypatch.setattr(benchmark_base.subprocess, "run", lambda *a, **k: (_ for _ in ()).throw(OSError()))
        assert benchmark_base.recorded_version(folder) == {"version": "1.0.0", "commit": None, "uncommitted": None}

    @staticmethod
    def _commit(root, message):
        import subprocess
        for args in (["add", "."], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", message]):
            subprocess.run(["git", *args], cwd=root, check=True)

    def test_a_run_from_one_benchmark_state_keeps_its_earliest_version(self, repo):
        from benchmark_base import recorded_version, resumed_version
        first = recorded_version(repo)
        (repo.parent.parent / "other.txt").write_text("changed", encoding="utf-8")
        self._commit(repo.parent.parent, "outside the benchmark")
        later = recorded_version(repo)
        assert later["commit"] != first["commit"]
        assert resumed_version([("2026-01-02T10:00:00", later), ("2026-01-01T09:00:00", first)], repo) == first

    def test_a_resume_after_a_benchmark_change_keeps_the_original_version_and_is_mixed(self, repo):
        from benchmark_base import recorded_version, resumed_version
        first = recorded_version(repo)
        (repo / "meta.json").write_text('{"versions": [{"version": "3.0.0"}]}', encoding="utf-8")
        self._commit(repo.parent.parent, "3.0.0")
        later = recorded_version(repo)
        assert resumed_version([("2026-01-02T10:00:00", later), ("2026-01-01T09:00:00", first)], repo) == \
            {**first, "mixed": True}

    def test_answers_saved_before_versions_were_recorded_make_a_run_mixed(self, repo):
        from benchmark_base import recorded_version, resumed_version
        now = recorded_version(repo)
        assert resumed_version([("2026-01-01T09:00:00", None), ("2026-01-02T10:00:00", now)], repo) == \
            {"version": None, "commit": None, "uncommitted": None, "mixed": True}
        assert resumed_version([("2026-01-01T09:00:00", None)], repo) is None
        assert resumed_version([], repo) is None

    def test_a_resumed_run_records_the_version_its_reused_answers_were_made_with(self, repo, tmp_path, monkeypatch):
        """Answers saved under 2.0.0, the run resumed after 3.0.0: the run keeps 2.0.0, marked mixed."""
        from benchmark_base import recorded_version, resumed_version
        benchmark = _Stored.__new__(_Stored)
        run_dir = tmp_path / "results" / "T0001"
        monkeypatch.setattr(benchmark, "get_request_answer_path", lambda: str(run_dir))
        monkeypatch.setattr(benchmark, "get_request_name", lambda name: "request_T0001_" + name)

        def save(name, when):
            answer = LLMResponse(text="{}", model="m", provider="openai", finish_reason="stop",
                                 usage=Usage(input_tokens=1, output_tokens=1, total_tokens=2), raw_response={})
            answer.timestamp = when
            benchmark.save_request_answer(name, answer, {})

        benchmark.version = recorded_version(repo)
        save("a", __import__("datetime").datetime(2026, 1, 1, 9))
        (repo / "meta.json").write_text('{"versions": [{"version": "3.0.0"}]}', encoding="utf-8")
        self._commit(repo.parent.parent, "3.0.0")
        benchmark.version = recorded_version(repo)
        save("b", __import__("datetime").datetime(2026, 1, 2, 9))
        stamp = resumed_version(benchmark.saved_versions(["a", "b", "never-saved"]), repo)
        assert stamp["version"] == "2.0.0" and stamp["mixed"] is True
