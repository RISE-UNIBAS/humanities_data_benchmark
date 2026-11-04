"""`.zenodo.json` is generated from CITATION.cff; Zenodo reads it instead of CITATION.cff."""
import json

import yaml

from scripts import zenodo_metadata as zm


def test_zenodo_json_is_up_to_date():
    assert zm.OUTPUT.exists(), "run python -m scripts.zenodo_metadata"
    assert zm.OUTPUT.read_text(encoding="utf-8") == zm.render(), \
        ".zenodo.json is out of date: run python -m scripts.zenodo_metadata"


def test_zenodo_json_matches_the_citation():
    record = json.loads(zm.OUTPUT.read_text(encoding="utf-8"))
    citation = yaml.safe_load(zm.CITATION.read_text(encoding="utf-8"))
    assert record["upload_type"] == "software"
    assert record["title"] == citation["title"]
    assert "version" not in record
    assert [c["name"] for c in record["creators"]] == [
        "%s, %s" % (a["family-names"], a["given-names"]) for a in citation["authors"]]
    related = {(r["identifier"], r["relation"]) for r in record["related_identifiers"]}
    concept = json.loads(zm.RELEASES.read_text(encoding="utf-8"))["concept_doi"]
    assert (concept, "isSupplementedBy") in related
    for ref in citation.get("references") or []:
        if ref.get("type") == "article":
            assert (ref["doi"], "isDescribedBy") in related
