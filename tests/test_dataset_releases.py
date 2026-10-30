"""The dataset's release record and what the documentation makes of it.

A version DOI is minted after the release's bytes are fixed, so it reaches the dataset only
through the next build. These tests pin that path: recording a deposit, carrying the DOIs
into CITATION.cff, and a changelog that says per release what changed -- above all which
benchmark versions re-based stored scores.

Run with the rest of the logic-only suite: pytest -m "not integrity".
"""
import json

import pytest

from scripts.export_dataset import SCHEMA_VERSION, docs, releases


def _versions(*entries):
    return {"versions": [{"version": v, "date": d, "change": c, "summary": s}
                         for v, d, c, s in entries]}


COMPANY_LISTS = [("1.1.0", "2026-10-20", "minor", "A prompt variant"),
                 ("1.0.0", "2026-10-16", "major", "Card introduced")]
LATER = ("2.0.0", "2026-11-03", "major", "Ground truth corrected")


@pytest.fixture
def benchmarks(make_benchmarks):
    """Three benchmarks as a first release finds them; call it again to change them."""
    def _make(company_lists=COMPANY_LISTS):
        return make_benchmarks({
            "company_lists": _versions(*company_lists),
            "library_cards": _versions(("1.0.0", "2026-10-16", "major", "Card introduced")),
            "test_benchmark": _versions(("1.0.0", "2026-10-16", "major", "Scaffold")),
        })
    _make()
    return _make


def _manifest(version, cutoff, runs, requests, **extra):
    manifest = {"dataset_version": version, "schema_version": SCHEMA_VERSION,
                "data_cutoff": cutoff, "partial": False, "source_commit": "a" * 40,
                "build_started_utc": "2026-11-01T10:00:00+00:00",
                "row_counts": {"runs": runs, "requests": requests, "scores_long": 10,
                               "metrics": 3},
                "inventory": {"files_hashed": 5}}
    manifest.update(extra)
    return manifest


# --- benchmark versions -----------------------------------------------------------

def test_a_build_holds_the_newest_versions_and_not_the_test_benchmarks(benchmarks):
    assert releases.versions_now() == {"company_lists": "1.1.0", "library_cards": "1.0.0"}


def test_the_versions_since_a_release_are_those_after_the_one_it_recorded(benchmarks):
    benchmarks([LATER] + COMPANY_LISTS)
    added = releases.versions_since({"company_lists": "1.1.0", "library_cards": "1.0.0"})
    assert [(e["benchmark"], e["version"], e["change"]) for e in added] == [
        ("company_lists", "2.0.0", "major")]


def test_a_benchmark_new_since_the_last_release_brings_its_whole_history(benchmarks):
    added = releases.versions_since({"company_lists": "1.1.0"})
    assert [(e["benchmark"], e["version"]) for e in added] == [("library_cards", "1.0.0")]


# --- the record ---------------------------------------------------------------------

def test_without_a_record_a_build_is_the_first_release(benchmarks, tmp_path):
    facts = releases.for_manifest("2026-10-31.1", tmp_path / "none.json")
    assert facts["prior_releases"] == [] and facts["concept_doi"] is None
    assert facts["benchmark_versions_since_previous"] is None
    assert facts["benchmark_versions"]["company_lists"] == "1.1.0"


def test_the_first_record_needs_the_concept_doi(tmp_path):
    with pytest.raises(SystemExit, match="concept DOI"):
        releases.record(_manifest("2026-10-31.1", "2026-10-31", 10, 100), "10.5281/zenodo.2",
                        path=tmp_path / "r.json")
    assert not (tmp_path / "r.json").exists()


def _first_release(path):
    first = _manifest("2026-10-31.1", "2026-10-31", 10, 100,
                      **releases.for_manifest("2026-10-31.1", path))
    releases.record(first, "10.5281/zenodo.2", "10.5281/zenodo.1", "2026-11-01", path=path)


def test_a_recorded_release_feeds_the_next_build(benchmarks, tmp_path):
    path = tmp_path / "r.json"
    _first_release(path)
    benchmarks([LATER] + COMPANY_LISTS)

    facts = releases.for_manifest("2026-11-05.1", path)
    assert facts["concept_doi"] == "10.5281/zenodo.1"
    assert [r["version"] for r in facts["prior_releases"]] == ["2026-10-31.1"]
    assert [e["version"] for e in facts["benchmark_versions_since_previous"]] == ["2.0.0"]

    rebuilt = releases.for_manifest("2026-10-31.1", path)
    assert rebuilt["prior_releases"] == [], "a rebuild of a release is not its own prior"


@pytest.mark.parametrize("change", [{"partial": True}, {}])
def test_a_partial_build_or_a_second_record_is_refused(tmp_path, change):
    path = tmp_path / "r.json"
    manifest = _manifest("2026-10-31.1", "2026-10-31", 10, 100)
    if not change:
        releases.record(manifest, "10.5281/zenodo.2", "10.5281/zenodo.1", path=path)
    with pytest.raises(SystemExit):
        releases.record(dict(manifest, **change), "10.5281/zenodo.3", "10.5281/zenodo.1",
                        path=path)


# --- the documentation --------------------------------------------------------------

@pytest.fixture
def second(benchmarks, tmp_path):
    """A build after one recorded release, with a MAJOR benchmark version in between."""
    path = tmp_path / "r.json"
    _first_release(path)
    benchmarks([LATER] + COMPANY_LISTS)
    manifest = _manifest("2026-11-05.1", "2026-11-05", 12, 130,
                         **releases.for_manifest("2026-11-05.1", path))
    manifest["software_version"] = "0.8.0"
    return manifest


def test_the_first_changelog_entry_describes_the_dataset(benchmarks, tmp_path):
    manifest = _manifest("2026-10-31.1", "2026-10-31", 10, 100,
                         **releases.for_manifest("2026-10-31.1", tmp_path / "none.json"))
    text = docs.changelog(manifest)
    assert "## 2026-10-31.1\n" in text and "Initial release" in text
    assert "`company_lists` 1.1.0" in text and "unreleased" not in text


def test_a_later_changelog_entry_says_what_changed_and_keeps_the_history(second):
    text = docs.changelog(second)
    current, earlier = text.split("## 2026-10-31.1")
    assert "12 runs (+2) and 130 requests (+30) since 2026-10-31.1" in current
    assert "`company_lists` 2.0.0 (major, 2026-11-03)" in current
    assert "re-based" in current, "a MAJOR version re-scores the stored runs"
    assert "software 0.8.0" in current
    assert "released 2026-11-01" in earlier and "10.5281/zenodo.2" in earlier


def test_citation_lists_the_concept_doi_and_the_earlier_versions(second):
    yaml = pytest.importorskip("yaml")
    parsed = yaml.safe_load(docs.citation(second, None))
    assert parsed["identifiers"] == [
        {"type": "doi", "value": "10.5281/zenodo.1", "description": "All versions"},
        {"type": "doi", "value": "10.5281/zenodo.2", "description": "Version 2026-10-31.1"}]


def test_the_readme_explains_the_three_versions_and_cites_the_concept_doi(second):
    text = docs.readme(second)
    assert "## Versions" in text and "benchmark_version_scored" in text
    assert "full snapshot" in text
    assert "https://doi.org/10.5281/zenodo.1" in text
    assert "## Versions" in docs.release_readme(second, set()), "the release README too"


def test_the_record_command_writes_the_deposited_build(tmp_path, monkeypatch):
    dataset = tmp_path / "dataset"
    dataset.mkdir()
    (dataset / "manifest.json").write_text(
        json.dumps(_manifest("2026-10-31.1", "2026-10-31", 10, 100)), encoding="utf-8")
    monkeypatch.setattr(releases, "RELEASES_PATH", tmp_path / "r.json")
    releases.main(["record", "--dataset", str(dataset), "--doi", "10.5281/zenodo.2",
                   "--concept-doi", "10.5281/zenodo.1", "--released", "2026-11-01"])
    record = json.loads((tmp_path / "r.json").read_text(encoding="utf-8"))
    assert record["concept_doi"] == "10.5281/zenodo.1"
    assert record["releases"][0]["released"] == "2026-11-01"
