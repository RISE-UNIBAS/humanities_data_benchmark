"""BenchmarkCard integrity guards.

Every benchmark's README.md becomes a BenchmarkCard (see scripts/benchmark_cards.py). Until a
benchmark is migrated it is listed in UNMIGRATED, where its card test is an expected failure;
once its README is a card the strict xfail fails, and the name must be removed from the set.

Rules enforced here, for every card:
  1. The README parses: sections and fields present, in schema order.
  2. The card validates against the vendored schema, and data_type/audience use its vocabularies.
  3. Methodology / Metrics names meta.json's ranking metric; Versions is filled in.
  4. README generated fields and benchmark_card.json match what the script produces. Fix: run
     python scripts/benchmark_cards.py <name>.
"""
import os

import pytest

import benchmark_cards

pytestmark = pytest.mark.integrity

BENCHMARKS_DIR = benchmark_cards.BENCHMARKS_DIR

# Example/smoke benchmarks used to exercise the harness, not real datasets.
SCAFFOLD_BENCHMARKS = {"test_benchmark", "test_benchmark2"}

UNMIGRATED = {
    "bibliographic_data", "blacklist_cards", "book_advert_xml", "business_letters",
    "company_lists", "duty_rosters", "fraktur_adverts", "general_meeting_minutes",
    "library_cards", "magazine_pages", "medieval_manuscripts",
}


def _benchmarks():
    return [
        name for name in sorted(os.listdir(BENCHMARKS_DIR))
        if os.path.isfile(os.path.join(BENCHMARKS_DIR, name, "meta.json"))
        and name not in SCAFFOLD_BENCHMARKS
    ]


def _check(name):
    readme = os.path.join(BENCHMARKS_DIR, name, "README.md")
    assert os.path.isfile(readme), f"{name} has no README.md"
    with open(readme, encoding="utf-8") as f:
        assert benchmark_cards.is_card(f.read()), f"{name}/README.md is not a BenchmarkCard"
    stale = benchmark_cards.drift(name)
    assert not stale, (f"{name}: {stale} out of date; "
                       f"run python scripts/benchmark_cards.py {name}")


@pytest.mark.parametrize("name", [
    pytest.param(n, marks=pytest.mark.xfail(strict=True, reason="README not yet a BenchmarkCard"))
    if n in UNMIGRATED else n
    for n in _benchmarks()
])
def test_readme_is_a_valid_current_card(name):
    _check(name)


def test_unmigrated_set_names_real_benchmarks():
    unknown = UNMIGRATED - set(_benchmarks())
    assert not unknown, f"UNMIGRATED names benchmarks that do not exist: {sorted(unknown)}"
