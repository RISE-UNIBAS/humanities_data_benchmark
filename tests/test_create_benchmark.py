"""Tests for scripts/create_benchmark.py: what it scaffolds loads, scores and builds a card."""
import ast
import builtins
import importlib.util
import json

import pytest

import benchmark_cards as bc
import create_benchmark as cb


def _info(**overrides):
    info = {
        "name": "letters_19c", "title": "Letters", "title_short": "Letters",
        "description": "Nineteenth-century letters.", "tags": {"language": ["de", "ar"]},
        "contributors": [{"role": "Engineer", "contributors": ["maximilian_hindermann"]}],
        "ranking_metric": "fuzzy", "ranking_order": "desc",
        "use_dataclass": True, "dataclass_name": "Letter", "use_images": False, "use_texts": True,
        "use_shared_context": False, "shared_context_prompt": "", "default_prompt": "Extract the sender.",
    }
    info.update(overrides)
    info["class_name"] = cb.to_camel_case(info["name"])
    return info


@pytest.fixture
def scaffold(tmp_path, monkeypatch):
    """Scaffold into a temporary benchmarks/ and tests/, with the card builder pointed there."""
    benchmarks, tests = tmp_path / "benchmarks", tmp_path / "tests"
    benchmarks.mkdir()
    tests.mkdir()
    monkeypatch.setattr(cb, "BENCHMARKS_PATH", benchmarks)
    monkeypatch.setattr(cb, "TESTS_PATH", tests)
    monkeypatch.setattr(bc, "BENCHMARKS_DIR", str(benchmarks))

    def _make(info):
        assert cb.create_benchmark_structure(info)
        return benchmarks / info["name"]
    return _make


def _load_runner_class(directory, name):
    spec = importlib.util.spec_from_file_location("_scaffolded", directory / "benchmark.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # The rule run_benchmarks.load_benchmark and benchmark_cards use to find the class.
    return getattr(module, "".join(part.capitalize() for part in name.split("_")))


def test_class_is_found_under_the_runners_name_when_the_name_has_digits(scaffold):
    directory = scaffold(_info(name="letters_19c"))
    assert _load_runner_class(directory, "letters_19c").__name__ == "Letters19c"


def test_scaffold_builds_a_card_once_data_and_metrics_are_added(scaffold):
    directory = scaffold(_info())
    (directory / "texts" / "l1.txt").write_text("Lieber Freund", encoding="utf-8")
    (directory / "ground_truths" / "l1.json").write_text('{"sender": "A"}', encoding="utf-8")
    readme = directory / "README.md"
    readme.write_text(readme.read_text(encoding="utf-8").replace(
        "**Metrics:** Not specified", "**Metrics:**\n\n- fuzzy: mean field similarity"), encoding="utf-8")
    text, card = bc.build("letters_19c")
    card = json.loads(card)["benchmark_card"]
    assert card["benchmark_details"]["languages"] == ["German", "Arabic"]
    assert card["methodology"]["judge_uses_llm"] is False


@pytest.mark.parametrize("text", ['C:\\Names\\u00e9 and \\x', 'He said """no""" and """"', 'ends with "', 'a\\'])
def test_titles_and_descriptions_are_kept_verbatim_in_docstrings(scaffold, text):
    directory = scaffold(_info(title=text, description=text, use_shared_context=True))
    for filename in ("benchmark.py", "dataclass.py"):
        tree = ast.parse((directory / filename).read_text(encoding="utf-8"))
        assert text in ast.get_docstring(tree, clean=False)
    cls = _load_runner_class(directory, "letters_19c")
    assert text in cls.__doc__


def test_scaffolded_scorer_scores_a_match_and_a_miss(scaffold, make_scorer, response):
    scorer = make_scorer(_load_runner_class(scaffold(_info()), "letters_19c"))
    truth = {"sender": "A", "year": 1850}
    assert scorer.score_request_answer("l1", response(parsed=dict(truth)), truth)["fuzzy"] == 1.0
    assert scorer.score_request_answer("l1", response(parsed=None, text="prose"), truth)["fuzzy"] == 0.0


def test_end_of_input_on_a_required_answer_stops_instead_of_looping(monkeypatch):
    def eof(_prompt=""):
        raise EOFError
    monkeypatch.setattr(builtins, "input", eof)
    with pytest.raises(EOFError):
        cb.get_input("Benchmark directory name")
    assert cb.get_input("Short title", default="x") == "x"


def test_paths_do_not_depend_on_the_working_directory():
    assert cb.BENCHMARKS_PATH.is_absolute() and (cb.BENCHMARKS_PATH / "README_TEMPLATE.md").is_file()
    assert cb.TESTS_PATH == cb.REPO_ROOT / "tests"


def test_every_offered_language_has_a_card_name():
    with open(cb.VOCABULARIES_PATH / "language.json", encoding="utf-8") as f:
        codes = json.load(f)["values"]
    assert not [c for c in codes if c not in bc.LANGUAGES]
