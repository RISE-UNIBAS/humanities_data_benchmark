"""The files that let the dataset be read without the repository.

`coverage.csv`, `datapackage.json`, the README and `CITATION.cff` are generated rather than
written, which removes one failure mode and introduces another: they cannot drift from the
schema, but they can silently omit something. These tests are mostly about omission.

The licence assertions look odd until you know why they are there. The software is GPL-3.0
and the temptation is to stamp that on the dataset too, but a dataset is not software and
the terms covering stored model responses and ground truths have not been decided. The
build must therefore ship *no* licence and say so, and a future change that quietly fills
one in should fail here rather than reach a deposit.

Run with the rest of the logic-only suite: pytest -m "not integrity".
"""
import json

import pytest

from scripts.export_dataset import columns as C
from scripts.export_dataset import coverage, docs
from scripts.export_dataset.schema import SCHEMAS_FOR_DOCS, TABLES


@pytest.fixture
def manifest():
    return {
        "schema_version": "1.0.0",
        "partial": False,
        "data_cutoff": "2026-09-09",
        "source_commit": "0a74b1592cd65fa34c31d24e26db5eeff9aa8e01",
        "build_started_utc": "2026-09-14T10:00:00+00:00",
        "row_counts": {"runs": 2371, "requests": 104395, "scores_long": 1977761,
                       "metrics": 114},
        "inventory": {"files_hashed": 106775},
    }


# --- the data dictionary --------------------------------------------------------

def test_every_column_has_a_description():
    """A column added to the schema without one fails the build, not the reader."""
    C.check_complete(SCHEMAS_FOR_DOCS)


def test_a_column_without_a_description_is_caught():
    import pyarrow as pa
    with pytest.raises(ValueError, match="no description"):
        C.check_complete({"runs": pa.schema([("invented_column", pa.string())])})


def test_a_description_without_a_column_is_caught():
    import pyarrow as pa
    with pytest.raises(ValueError, match="described but not in the schema"):
        C.check_complete({"runs": pa.schema([("run_id", pa.string())])})


# --- coverage -------------------------------------------------------------------

def _rows():
    return [
        {"benchmark": "business_letters", "configured_provider": "openai",
         "date": "2026-01-01", "value": 1.0},
        {"benchmark": "business_letters", "configured_provider": "openai",
         "date": "2026-01-01", "value": None},
        {"benchmark": None, "configured_provider": "genai",
         "date": "2026-01-02", "value": 2.0},
    ]


def _schema():
    import pyarrow as pa
    return pa.schema([("benchmark", pa.string()), ("configured_provider", pa.string()),
                      ("date", pa.string()), ("value", pa.float64())])


def test_coverage_counts_nulls_against_the_right_denominator():
    rows = coverage.build({"t": (_rows(), _schema())})
    glob = [r for r in rows if r["group_dimension"] == "global" and r["column"] == "value"]
    assert len(glob) == 1
    assert glob[0]["n_rows"] == 3 and glob[0]["n_non_null"] == 2 and glob[0]["n_null"] == 1
    assert glob[0]["fraction_non_null"] == pytest.approx(2 / 3)


def test_coverage_keeps_a_group_whose_own_value_is_null():
    """A column unpopulated exactly where the benchmark is unknown is the pattern to see."""
    rows = coverage.build({"t": (_rows(), _schema())})
    groups = set(r["group_value"] for r in rows
                 if r["group_dimension"] == "benchmark")
    assert coverage.NULL_LABEL in groups


def test_coverage_groups_by_the_documented_dimensions():
    rows = coverage.build({"t": (_rows(), _schema())})
    assert set(r["group_dimension"] for r in rows) == set(coverage.GROUPINGS)


def test_coverage_skips_a_dimension_the_table_does_not_have():
    """scores_long has no benchmark column; grouping it that way says nothing."""
    rows = coverage.build({"scores_long": (
        [{"value": 1.0}], TABLES["scores_long"])})
    assert set(r["group_dimension"] for r in rows) == {"global"}


def test_coverage_counts_a_non_finite_value_as_invalid():
    rows = coverage.build({"t": ([{"benchmark": "b", "configured_provider": "p",
                                   "date": "d", "value": float("nan")}], _schema())})
    value = [r for r in rows
             if r["column"] == "value" and r["group_dimension"] == "global"][0]
    assert value["n_non_null"] == 1 and value["n_invalid"] == 1


# --- datapackage ----------------------------------------------------------------

def test_datapackage_describes_every_table_and_column(manifest):
    package = docs.datapackage(manifest)
    resources = dict((r["name"], r) for r in package["resources"])
    assert set(TABLES) <= set(resources)
    for name, schema in TABLES.items():
        fields = [f["name"] for f in resources[name]["schema"]["fields"]]
        assert fields == list(schema.names)
        assert all(f["description"] for f in resources[name]["schema"]["fields"])


def test_datapackage_declares_the_primary_keys(manifest):
    resources = dict((r["name"], r) for r in docs.datapackage(manifest)["resources"])
    assert resources["requests"]["schema"]["primaryKey"] == ["run_id", "object_id"]
    assert resources["runs"]["schema"]["primaryKey"] == ["run_id"]


def test_datapackage_maps_arrow_types_to_frictionless_ones(manifest):
    resources = dict((r["name"], r) for r in docs.datapackage(manifest)["resources"])
    fields = dict((f["name"], f["type"]) for f in resources["requests"]["schema"]["fields"])
    assert fields["object_id"] == "string"
    assert fields["input_tokens"] == "integer"
    assert fields["duration_s"] == "number"
    assert fields["is_error"] == "boolean"


def test_datapackage_relates_the_dataset_to_the_software(manifest):
    related = docs.datapackage(manifest)["relatedIdentifiers"]
    assert related[0]["relationType"] == "isSupplementTo"
    assert related[0]["relatedIdentifier"] == docs.SOFTWARE_CONCEPT_DOI


def test_datapackage_declares_no_licence(manifest):
    """Undetermined, and an empty list says so where a guess would mislead."""
    assert docs.datapackage(manifest)["licenses"] == []


def test_datapackage_is_json_serialisable(manifest):
    json.loads(json.dumps(docs.datapackage(manifest)))


# --- README ---------------------------------------------------------------------

def test_readme_states_the_things_an_analyst_will_get_wrong(manifest):
    text = docs.readme(manifest)
    for expected in (
        "null means \"not recorded\" and never zero",   # missingness
        "not what was charged",                          # derived cost
        "null for every row in this release",            # timestamp_utc
        "independent replicates",                        # repeated runs
        "hidden = false",                                # default view
        "leading-zero object ids into integers",         # CSV loading
        "Not yet determined",                            # licence
    ):
        assert expected in text, "README no longer explains: %s" % expected


def test_readme_reports_the_actual_row_counts(manifest):
    text = docs.readme(manifest)
    assert "104,395" in text and "1,977,761" in text


def test_a_partial_build_says_so_in_its_readme(manifest):
    manifest["partial"] = True
    assert "not a release" in docs.readme(manifest)
    assert "not a release" not in docs.readme(dict(manifest, partial=False))


# --- citation -------------------------------------------------------------------

def test_citation_reuses_the_software_authors(manifest):
    software = {"authors": [{"family-names": "Hindermann", "given-names": "Maximilian",
                             "orcid": "https://orcid.org/0000-0002-9337-4655"}]}
    text = docs.citation(manifest, software)
    assert "Hindermann" in text and "0000-0002-9337-4655" in text
    assert "type: dataset" in text


def test_citation_survives_a_missing_software_citation(manifest):
    text = docs.citation(manifest, None)
    assert "cff-version: 1.2.0" in text and "authors:" not in text


def test_citation_carries_no_doi_and_no_licence(manifest):
    """A placeholder that looks like an identifier is worse than no identifier."""
    text = docs.citation(manifest, None)
    assert "identifiers: []" in text
    assert "10.5281/zenodo" in text, "the software DOI is still referenced"
    assert "\nlicense:" not in text, "the dataset licence is undetermined; do not stamp one"


def test_citation_parses_as_yaml(manifest):
    yaml = pytest.importorskip("yaml")
    parsed = yaml.safe_load(docs.citation(manifest, {"authors": [
        {"family-names": "Hindermann", "given-names": "Maximilian"}]}))
    assert parsed["cff-version"] == "1.2.0"
    assert parsed["type"] == "dataset"
    assert parsed["identifiers"] == []
    assert "license" not in parsed
