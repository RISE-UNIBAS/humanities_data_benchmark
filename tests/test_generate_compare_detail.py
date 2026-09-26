"""`generate_compare_detail` against stubbed runs and scorers, without a corpus."""
import json

import pytest

from scripts.ndr_export import generate_compare_detail as g


@pytest.fixture
def detail(tmp_path, monkeypatch):
    run_dir = tmp_path / "results" / "2025-03-01" / "T0001"
    run_dir.mkdir(parents=True)
    detail_dir = tmp_path / "compare_detail"
    produced = {}

    class Scorer:
        rules = None

    monkeypatch.setattr(g, "DETAIL_DIR", detail_dir)
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
