"""Step 1: freeze the inputs and record exactly what was read.

A dataset release has to be traceable to the bytes it came from. Two builds that disagree
must be explainable by an input that changed or an exporter that changed, and neither is
answerable without a hash of every file consumed.

So this hashes `results/` and every metadata file the export joins against -- the test
CSV, each benchmark's `meta.json`, the pricing table and the alias map -- not just the
results. Pricing now feeds a derived cost column, which makes `pricing.json` part of the
dataset's identity rather than a detail of how it was built.

Counts are measured and recorded, never asserted against a figure written in a plan
document. `dev/DATASET_EXPORT_PLAN.md` §9.1 is explicit about this: the corpus grows, and
a hard-coded expectation turns an ordinary new run into a failed build.
"""
import hashlib
from pathlib import Path

from scripts.results_index import (BENCHMARKS_PATH, PROJECT_ROOT, RESULTS_PATH, TESTS_CSV,
                                   benchmark_names, iter_run_dirs)

METADATA_FILES = (
    TESTS_CSV,
    PROJECT_ROOT / "scripts" / "data" / "pricing.json",
    PROJECT_ROOT / "scripts" / "data" / "model_aliases.json",
    PROJECT_ROOT / "scripts" / "data" / "contributors.json",
    PROJECT_ROOT / "CITATION.cff",
)

CHUNK = 1 << 20


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(CHUNK), b""):
            digest.update(block)
    return digest.hexdigest()


def relative_path(path, *roots):
    """A path as it will appear in the release: relative to a root, posix.

    An absolute path would carry the build machine's username and directory layout into a
    published artifact, and would mean nothing to anyone reading it.

    The repository root is tried first, so an ordinary build keeps `results/<date>/...`.
    Extra roots let a build with `--source` elsewhere still name its files relatively,
    which matters because the same string has to work in the tables, the manifests and the
    invalid-byte sidecars; using different namespaces in different places is how a source
    stops reconciling to its row.
    """
    path = Path(path)
    for root in (PROJECT_ROOT,) + tuple(r for r in roots if r is not None):
        try:
            return path.relative_to(Path(root)).as_posix()
        except ValueError:
            continue
    return path.as_posix()


_relative = relative_path


def consumed_files(results_path=RESULTS_PATH):
    """Every file the export reads, results and metadata alike, sorted by path."""
    paths = []
    for run in iter_run_dirs(results_path):
        paths.extend(sorted(run.path.iterdir()))
    for name in benchmark_names():
        meta = BENCHMARKS_PATH / name / "meta.json"
        if meta.is_file():
            paths.append(meta)
    for path in METADATA_FILES:
        if path.is_file():
            paths.append(path)
    # The frontend's re-scored field detail is an input now, so it is hashed like any
    # other. Absent in a checkout where the frontend pipeline has not run, which is fine.
    paths.extend(sorted((PROJECT_ROOT / "collected_results" / "compare_detail")
                        .glob("*/*.json")))
    return sorted(set(p for p in paths if p.is_file()), key=_relative)


def build(results_path=RESULTS_PATH):
    """Returns (manifest rows, summary, diagnostics).

    A diagnostic here is a shape the extractor was not written for -- a directory nested
    inside a run, a file that is neither a request nor a scoring file. Recording it beats
    skipping it: the release decision is a human's, and it cannot be made about something
    that never appeared in the output.
    """
    rows = []
    diagnostics = []
    counts = {"request_files": 0, "scoring_files": 0, "other_files": 0, "run_dirs": 0}
    dates = set()

    for run in iter_run_dirs(results_path):
        counts["run_dirs"] += 1
        dates.add(run.date)
        for entry in sorted(run.path.iterdir()):
            if entry.is_dir():
                diagnostics.append({
                    "source_path": _relative(entry),
                    "issue": "directory_inside_run",
                    "severity": "blocking",
                    "handling": "not exported; results/ is expected to be two levels deep",
                })
                continue
            if entry.name == "scoring.json":
                counts["scoring_files"] += 1
            elif entry.name.startswith("request_") and entry.name.endswith(".json"):
                counts["request_files"] += 1
            else:
                counts["other_files"] += 1
                diagnostics.append({
                    "source_path": _relative(entry),
                    "issue": "unexpected_file_in_run",
                    "severity": "blocking",
                    "handling": "not exported; expected request_*.json or scoring.json",
                })

    for path in consumed_files(results_path):
        rows.append({
            "path": _relative(path),
            "sha256": sha256_of(path),
            "size_bytes": path.stat().st_size,
        })

    summary = dict(counts)
    summary["dates"] = len(dates)
    summary["data_cutoff"] = max(dates) if dates else None
    summary["first_date"] = min(dates) if dates else None
    summary["files_hashed"] = len(rows)
    return rows, summary, diagnostics
