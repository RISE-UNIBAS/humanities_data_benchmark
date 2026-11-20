"""`generate_compare_detail` against stubbed runs and scorers, without a corpus."""
import json
from pathlib import Path

import pytest

from scripts.compare import generate_compare_detail as g


@pytest.fixture
def detail(tmp_path, monkeypatch):
    run_dir = tmp_path / "results" / "2025-03-01" / "T0001"
    run_dir.mkdir(parents=True)
    detail_dir = tmp_path / "compare_detail"
    produced = {}

    class Scorer:
        rules = None

    monkeypatch.setattr(g, "DETAIL_DIR", detail_dir)
    monkeypatch.setattr(g, "REGENERATED_PATH", tmp_path / "compare_detail_regenerated.json")
    monkeypatch.setattr(g, "read_tests", lambda: {})
    monkeypatch.setattr(g, "rules_of_test", lambda test_id, tests: None)
    monkeypatch.setattr(g, "iter_runs",
                        lambda benchmark: [(run_dir, "T0001", "test_benchmark")])
    monkeypatch.setattr(g, "load_scorer", lambda name: Scorer())
    monkeypatch.setattr(g, "revisions_for",
                        lambda name, cache: {"uncommitted_changes": None})
    monkeypatch.setattr(g, "detail_for_run",
                        lambda *args: (produced.get("inputs", {}),
                                       produced.get("diagnostics", {})))
    return detail_dir / "2025-03-01" / "T0001.json", produced


def test_a_run_that_no_longer_needs_detail_loses_its_file(detail):
    path, produced = detail
    produced["diagnostics"] = {"jaccuse": "TypeError"}
    g.generate_compare_detail()
    assert json.loads(path.read_text(encoding="utf-8"))["diagnostics"]

    produced.clear()
    g.generate_compare_detail()
    assert not path.exists(), "a detail file recording a since-fixed scorer error survived"


def test_measure_never_deletes(detail):
    path, produced = detail
    produced["diagnostics"] = {"jaccuse": "TypeError"}
    g.generate_compare_detail()

    produced.clear()
    g.generate_compare_detail(measure=True)
    assert path.exists()


def test_a_full_pass_records_its_day_even_when_it_writes_nothing(detail):
    """The export judges staleness by this day: a run the scorer saw and found no
    detail for leaves no file, so the files' own dates never move past it."""
    g.generate_compare_detail()
    stamps = json.loads(g.REGENERATED_PATH.read_text(encoding="utf-8"))
    assert stamps == {"test_benchmark": g.date_type.today().isoformat()}


@pytest.mark.parametrize("partial", [{"measure": True}, {"limit": 1}, {"only_missing": True}])
def test_a_partial_pass_records_nothing(detail, partial):
    g.generate_compare_detail(**partial)
    assert not g.REGENERATED_PATH.exists()


def test_an_edit_to_the_shared_scoring_code_is_recorded(monkeypatch):
    """Audit 2026-11-19 F06: only benchmark.py and ground_truths/ were checked."""
    monkeypatch.setattr(g, "is_dirty", lambda path: Path(path).name == "scoring_helper.py")
    monkeypatch.setattr(g, "git_revision", lambda *paths: "a" * 40)
    assert g.revisions_for("library_cards", {})["uncommitted_changes"] == ["shared_scoring"]


def test_the_scorer_revision_covers_helpers_and_shared_scoring_code(monkeypatch):
    """A committed change to scoring_helper.py must move scorer_revision, not only benchmark.py."""
    asked = []
    monkeypatch.setattr(g, "is_dirty", lambda path: False)
    monkeypatch.setattr(g, "git_revision", lambda *paths: asked.append(
        sorted(Path(p).name for p in paths)) or "a" * 40)
    g.revisions_for("business_letters", {})
    assert {"benchmark.py", "letter.py", "benchmark_base.py", "scoring_helper.py"} <= set(asked[0])
