"""The dataset's release record: every published version, its DOI and what it held.

A version DOI is minted after the bytes are fixed, so it can never be inside the release
it names. `scripts/data/dataset_releases.json` carries it into the next build instead:
after each deposit, record the release from the build that was deposited,

    python -m scripts.export_dataset.releases record --doi <version DOI> [--concept-doi <DOI>]

and every later build lists the earlier releases, their DOIs and the concept DOI in its
CITATION.cff and CHANGELOG.

Benchmark versions come from each benchmark's `meta.json` `versions` as the build finds
them: the newest of each is the version every stored run of it was last scored with, and the
entries added after the version the previous release recorded are what changed between the
two. A MAJOR version re-scores every stored run of its benchmark, so it is what tells a
reader that scores were re-based. Dates of runs play no part: a version added after the last
run still governs the scores a build exports.
"""
import argparse
import json
import sys
from pathlib import Path

from scripts.results_index import PROJECT_ROOT, benchmark_meta, benchmark_names, is_test_benchmark

RELEASES_PATH = PROJECT_ROOT / "scripts" / "data" / "dataset_releases.json"
VERSION_PATH = PROJECT_ROOT / "VERSION"


def load(path=None):
    """Return the release record, ``{"concept_doi": ..., "releases": [...]}``, oldest first.
    An absent file is an empty record: nothing has been released yet."""
    path = Path(path or RELEASES_PATH)
    if not path.is_file():
        return {"concept_doi": None, "releases": []}
    record = json.loads(path.read_text(encoding="utf-8"))
    return {"concept_doi": record.get("concept_doi"), "releases": record.get("releases") or []}


def software_version(path=VERSION_PATH):
    path = Path(path)
    return path.read_text(encoding="utf-8").strip() if path.is_file() else None


def _versions(name):
    """A benchmark's dated `versions` entries, oldest first."""
    read = benchmark_meta(name)
    entries = read.value.get("versions") if isinstance(read.value, dict) else None
    return [e for e in reversed(entries or []) if e.get("version") and e.get("date")]


def _released_benchmarks():
    return [n for n in benchmark_names() if not is_test_benchmark(n)]


def versions_now():
    """``{benchmark: newest version}``: the versions this build's scores come from."""
    current = {}
    for name in _released_benchmarks():
        entries = _versions(name)
        if entries:
            current[name] = entries[-1]["version"]
    return current


def versions_since(previous):
    """The versions added after those in `previous` (``{benchmark: version}``), by benchmark,
    oldest first: ``[{"benchmark", "version", "date", "change", "summary"}]``. A benchmark the
    previous release did not hold contributes its whole history."""
    added = []
    for name in _released_benchmarks():
        entries = _versions(name)
        known = [e["version"] for e in entries]
        start = known.index(previous[name]) + 1 if previous.get(name) in known else 0
        added.extend({"benchmark": name, "version": e["version"], "date": e["date"],
                      "change": e.get("change"), "summary": e.get("summary")}
                     for e in entries[start:])
    return added


def for_manifest(version, path=None):
    """The release facts a build records in its manifest: the releases before this one, the
    concept DOI, the benchmark versions it holds and those added since the previous release
    (None for the first)."""
    record = load(path)
    prior = [r for r in record["releases"] if r.get("version") != version]
    previous = prior[-1] if prior else None
    return {
        "software_version": software_version(),
        "concept_doi": record["concept_doi"],
        "prior_releases": prior,
        "benchmark_versions": versions_now(),
        "benchmark_versions_since_previous": (
            versions_since(previous.get("benchmark_versions") or {}) if previous else None),
    }


def record(manifest, doi, concept_doi=None, released=None, path=None):
    """Add the deposited build to the release record and return the record."""
    path = Path(path or RELEASES_PATH)
    if manifest.get("partial"):
        raise SystemExit("A partial build is not a release.")
    current = load(path)
    version = manifest["dataset_version"]
    if any(r.get("version") == version for r in current["releases"]):
        raise SystemExit("%s is already recorded in %s." % (version, path))
    if concept_doi and current["concept_doi"] and concept_doi != current["concept_doi"]:
        raise SystemExit("The record's concept DOI is %s, not %s."
                         % (current["concept_doi"], concept_doi))
    if not (concept_doi or current["concept_doi"]):
        raise SystemExit("No concept DOI recorded yet: pass --concept-doi with the first "
                         "release.")
    counts = manifest.get("row_counts", {})
    current["concept_doi"] = current["concept_doi"] or concept_doi
    current["releases"].append({
        "version": version,
        "released": released,
        "doi": doi,
        "data_cutoff": manifest["data_cutoff"],
        "schema_version": manifest.get("schema_version"),
        "software_version": manifest.get("software_version"),
        "source_commit": manifest.get("source_commit"),
        "runs": counts.get("runs"),
        "requests": counts.get("requests"),
        "benchmark_versions": manifest.get("benchmark_versions"),
        "benchmark_versions_since_previous": manifest.get("benchmark_versions_since_previous"),
    })
    Path(path).write_text(json.dumps(current, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8", newline="\n")
    return current


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m scripts.export_dataset.releases",
                                     description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    rec = sub.add_parser("record", help="record a deposited release and its DOI")
    rec.add_argument("--dataset", default=str(PROJECT_ROOT / "dataset"),
                     help="the build that was deposited")
    rec.add_argument("--doi", required=True, help="the version DOI Zenodo minted")
    rec.add_argument("--concept-doi", help="the concept DOI; required with the first release")
    rec.add_argument("--released", required=True, help="release date, YYYY-MM-DD")
    args = parser.parse_args(argv)

    manifest = json.loads((Path(args.dataset) / "manifest.json").read_text(encoding="utf-8"))
    record(manifest, args.doi, args.concept_doi, args.released)
    print("Recorded %s (%s) in %s" % (manifest["dataset_version"], args.doi, RELEASES_PATH))
    return 0


if __name__ == "__main__":
    sys.exit(main())
