"""Every benchmark's scorer has tests.

A benchmark counts as tested when a module under tests/ (outside tests/integrity/) imports
its benchmark module, `benchmarks.<name>.benchmark`. The framework fixtures test_benchmark
and test_benchmark2 are exempt.
"""
import os
import re

import pytest

pytestmark = pytest.mark.integrity

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TESTS_DIR = os.path.join(REPO_ROOT, "tests")
EXEMPT = {"test_benchmark", "test_benchmark2"}


def _benchmarks():
    root = os.path.join(REPO_ROOT, "benchmarks")
    return sorted(name for name in os.listdir(root)
                  if os.path.isfile(os.path.join(root, name, "benchmark.py")) and name not in EXEMPT)


def _tested():
    found = set()
    for file in os.listdir(TESTS_DIR):
        if file.startswith("test_") and file.endswith(".py"):
            with open(os.path.join(TESTS_DIR, file), encoding="utf-8") as f:
                found.update(re.findall(r"benchmarks\.(\w+)\.benchmark", f.read()))
    return found


def test_every_scorer_has_tests():
    missing = [name for name in _benchmarks() if name not in _tested()]
    assert not missing, f"no scorer tests for {missing}; add tests/test_<name>_scoring.py"
