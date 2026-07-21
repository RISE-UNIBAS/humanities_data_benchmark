"""Integrity guards over benchmarks/benchmarks_tests.csv.

These validate the real config file, so they fail when a model is added
incompletely. Run logic-only with: pytest -m "not integrity".
"""
import csv
import importlib
import json
import os
import re

import pytest

from local import is_local_provider

pytestmark = pytest.mark.integrity

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_PATH = os.path.join(REPO_ROOT, "benchmarks", "benchmarks_tests.csv")
BENCHMARKS_DIR = os.path.join(REPO_ROOT, "benchmarks")

EXPECTED_COLUMNS = [
    "id", "name", "provider", "model", "dataclass",
    "temperature", "role_description", "prompt_file", "rules", "legacy_test",
]

# API providers accepted by Benchmark.is_runnable (local providers checked separately).
API_PROVIDERS = {
    "openai", "genai", "anthropic", "mistral", "openrouter",
    "scicore", "cohere", "deepseek", "x-ai", "alibaba",
}

ID_RE = re.compile(r"^T(\d+)$")


def _read_rows():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


@pytest.fixture(scope="module")
def rows():
    _, data = _read_rows()
    return data


@pytest.fixture(scope="module")
def fieldnames():
    names, _ = _read_rows()
    return names


def test_header_columns(fieldnames):
    assert fieldnames == EXPECTED_COLUMNS


def test_rules_empty_or_valid_json(rows):
    bad = []
    for r in rows:
        rules = r["rules"]
        if rules == "":
            continue
        try:
            json.loads(rules)
        except json.JSONDecodeError:
            bad.append((r["id"], rules))
    assert not bad, f"Rows with invalid JSON in 'rules': {bad}"


def test_ids_unique_and_monotonic(rows):
    nums = []
    for r in rows:
        m = ID_RE.match(r["id"])
        assert m, f"Malformed id: {r['id']!r}"
        nums.append(int(m.group(1)))

    dupes = sorted({n for n in nums if nums.count(n) > 1})
    assert not dupes, f"Duplicate test IDs: {['T%04d' % n for n in dupes]}"

    out_of_order = [
        (f"T{prev:04d}", f"T{cur:04d}")
        for prev, cur in zip(nums, nums[1:]) if cur <= prev
    ]
    assert not out_of_order, f"IDs not strictly ascending in file order: {out_of_order}"


def test_provider_allowed(rows):
    bad = sorted({
        r["provider"] for r in rows
        if r["provider"] not in API_PROVIDERS and not is_local_provider(r["provider"])
    })
    assert not bad, f"Unknown providers: {bad}"


def test_benchmark_directory_exists(rows):
    missing = sorted({
        r["name"] for r in rows
        if not os.path.isdir(os.path.join(BENCHMARKS_DIR, r["name"]))
    })
    assert not missing, f"Benchmark directories not found: {missing}"


def test_prompt_file_exists(rows):
    """Each row's prompt_file must exist under benchmarks/<name>/prompts/.

    Mirrors Benchmark.__init__: an empty prompt_file defaults to 'prompt.txt'.
    A missing file makes the benchmark silently non-runnable (is_runnable returns False).
    """
    missing = []
    for r in rows:
        prompt_file = r["prompt_file"] or "prompt.txt"
        path = os.path.join(BENCHMARKS_DIR, r["name"], "prompts", prompt_file)
        if not os.path.isfile(path):
            missing.append((r["id"], r["name"], prompt_file))
    assert not missing, f"Rows whose prompt_file is missing: {missing}"


def test_dataclass_importable(rows):
    pairs = {(r["name"], r["dataclass"]) for r in rows}
    bad = []
    for name, dataclass in sorted(pairs):
        if dataclass in ("", "default"):
            continue
        try:
            module = importlib.import_module(f"benchmarks.{name}.dataclass")
            if not hasattr(module, dataclass):
                bad.append((name, dataclass, "class not found"))
        except ImportError as e:
            bad.append((name, dataclass, str(e)))
    assert not bad, f"Dataclasses not loadable: {bad}"