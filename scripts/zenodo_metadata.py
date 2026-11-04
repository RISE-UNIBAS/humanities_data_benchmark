"""Write `.zenodo.json`, the software's Zenodo metadata, from `CITATION.cff`.

Zenodo reads `.zenodo.json` in preference to `CITATION.cff`, so the file is generated rather
than kept by hand: authors, title, keywords and the articles come from `CITATION.cff`, the
dataset's concept DOI from `scripts/data/dataset_releases.json`. It adds what Zenodo does not
take from `CITATION.cff`: a description that stands on its own and the related identifiers
(the dataset, the articles). The version is left out: Zenodo takes the tag.

    python -m scripts.zenodo_metadata           # rewrite .zenodo.json
    python -m scripts.zenodo_metadata --check   # exit 1 if it is out of date
"""
import argparse
import json
import sys
from pathlib import Path

import yaml

from scripts.export_dataset import docs
from scripts.package_dataset import zenodo_creators

ROOT = Path(__file__).resolve().parent.parent
CITATION = ROOT / "CITATION.cff"
RELEASES = ROOT / "scripts" / "data" / "dataset_releases.json"
OUTPUT = ROOT / ".zenodo.json"
WEBSITE = "https://rise-services.rise.unibas.ch/benchmarks/"


def metadata(citation, dataset_concept_doi):
    return {
        "upload_type": "software",
        "title": citation["title"],
        "description": (
            "<p>" + docs.BENCHMARK_SUMMARY + "</p>"
            "<p>The software contains the benchmarks (images and texts, prompts, answer schemas, "
            "ground truths and scorers, each described in a benchmark card with its version "
            "history), the test configurations, the runner that queries the models through one "
            "interface for all providers and scores their answers, and every stored result.</p>"
            "<p>The stored results are also published as a dataset of joinable tables, one "
            "release per software release: <a href=\"https://doi.org/%s\">doi:%s</a>. The "
            "results are compared on <a href=\"%s\">%s</a>.</p>"
            % (dataset_concept_doi, dataset_concept_doi, WEBSITE, WEBSITE)),
        "creators": zenodo_creators(citation),
        "access_right": "open",
        "license": "gpl-3.0",
        "keywords": citation.get("keywords") or [],
        "related_identifiers": [{"identifier": dataset_concept_doi,
                                 "relation": "isSupplementedBy", "resource_type": "dataset",
                                 "scheme": "doi"}]
        + [{"identifier": ref["doi"], "relation": "isDescribedBy",
            "resource_type": "publication-article", "scheme": "doi"}
           for ref in citation.get("references") or []
           if ref.get("type") == "article" and ref.get("doi")],
    }


def render():
    citation = yaml.safe_load(CITATION.read_text(encoding="utf-8"))
    concept_doi = json.loads(RELEASES.read_text(encoding="utf-8"))["concept_doi"]
    return json.dumps(metadata(citation, concept_doi), indent=2, ensure_ascii=False) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="exit 1 if .zenodo.json is out of date")
    args = parser.parse_args(argv)
    text = render()
    if args.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else None
        if current != text:
            print(".zenodo.json is out of date: run python -m scripts.zenodo_metadata")
            return 1
        return 0
    OUTPUT.write_text(text, encoding="utf-8", newline="\n")
    print("wrote", OUTPUT.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
