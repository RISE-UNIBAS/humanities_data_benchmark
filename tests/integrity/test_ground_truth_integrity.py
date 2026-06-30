"""Ground-truth data integrity guards.

A missing or malformed ground truth fails silently at scoring time
(Benchmark.load_ground_truth returns "" for a missing file and {"error": ...}
for invalid JSON), producing a wrong/zero score with no error. These guards
surface that instead.

Run logic-only with: pytest -m "not integrity".

Rules enforced here:
  1. Every ground_truths/*.json across all benchmarks is valid JSON.
  2. Every logical object (image/text basename, collapsed with the benchmark's
     own basename pattern) has a matching ground_truths/<basename>.json. Harness
     scaffold benchmarks are excluded.
"""
import importlib.util
import json
import os

import pytest

from benchmark_base import Benchmark

pytestmark = pytest.mark.integrity

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BENCHMARKS_DIR = os.path.join(REPO_ROOT, "benchmarks")

# Example/smoke benchmarks used to exercise the harness, not real datasets.
SCAFFOLD_BENCHMARKS = {"test_benchmark", "test_benchmark2"}


def _benchmarks_with_ground_truths():
    for name in sorted(os.listdir(BENCHMARKS_DIR)):
        directory = os.path.join(BENCHMARKS_DIR, name)
        if os.path.isdir(directory) and os.path.isdir(os.path.join(directory, "ground_truths")):
            yield name, directory


def _basename_pattern(name, directory):
    """The benchmark's own page-collapsing pattern (only business_letters overrides
    the default). Falls back to the default pattern if benchmark.py is absent or
    cannot be loaded — import health is not this guard's concern."""
    benchmark_file = os.path.join(directory, "benchmark.py")
    if not os.path.isfile(benchmark_file):
        return None
    try:
        spec = importlib.util.spec_from_file_location(f"_gt_bench_{name}", benchmark_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cls = getattr(module, "".join(p.capitalize() for p in name.split("_")), None)
        if cls is None:
            return None
        return cls.get_basename_pattern(cls.__new__(cls))
    except Exception:
        return None


def test_ground_truths_are_valid_json():
    bad = []
    for name, directory in _benchmarks_with_ground_truths():
        gt_dir = os.path.join(directory, "ground_truths")
        for filename in os.listdir(gt_dir):
            if not filename.endswith(".json"):
                continue
            try:
                with open(os.path.join(gt_dir, filename), encoding="utf-8") as f:
                    json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                bad.append((name, filename, str(e)))
    assert not bad, f"Invalid ground-truth JSON files: {bad}"


def test_every_object_has_ground_truth():
    missing = []
    for name, directory in _benchmarks_with_ground_truths():
        if name in SCAFFOLD_BENCHMARKS:
            continue
        pattern = _basename_pattern(name, directory)
        basenames = Benchmark.get_all_basenames(
            [os.path.join(directory, "images"), os.path.join(directory, "texts")],
            page_pattern=pattern,
        )
        gt_dir = os.path.join(directory, "ground_truths")
        for basename in basenames:
            if not os.path.isfile(os.path.join(gt_dir, basename + ".json")):
                missing.append((name, basename))
    assert not missing, f"Objects with no ground_truths/<basename>.json: {missing}"