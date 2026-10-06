"""Inventory source files and compute hashes for dataset provenance.

Include files immediately within recognized run directories, benchmark metadata,
shared configuration and pricing files, citation metadata, and comparison-detail
artifacts. Record source paths, file sizes, SHA-256 hashes, counts, and date bounds.

Each row records ``committed``: whether the file is tracked at the source commit with
its contents unchanged, as Git reports it, or null where Git could not say. Separately,
``origin`` is ``generated`` for comparison-detail artifacts, which a pipeline step writes
rather than a benchmark run, with the scorer and ground-truth revisions each file records,
and ``source`` for everything else.

Report unexpected run contents as blocking diagnostics. Hashing records file
contents at read time; it does not lock inputs or create an immutable snapshot.
"""
import hashlib
import json
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
    """Return a POSIX path relative to the repository or an additional root.

    Try the repository root first, then supplied roots in order. If none contains
    the path, return its POSIX representation without removing the leading path.
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
    """Return existing inventoried input files, deduplicated and sorted by path."""
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
    paths.extend(_detail_files())
    return sorted(set(p for p in paths if p.is_file()), key=_relative)


def _detail_files():
    from scripts.export_dataset import rescored
    return rescored.detail_files()


def _generated_provenance(path):
    """Provenance a comparison-detail file records about itself."""
    try:
        with open(path, encoding="utf-8") as handle:
            detail = json.load(handle)
    except (OSError, ValueError):
        detail = {}
    if not isinstance(detail, dict):
        detail = {}
    return {
        "origin": "generated",
        "scorer_revision": detail.get("scorer_revision"),
        "ground_truth_revision": detail.get("ground_truth_revision"),
        "uncommitted_changes": detail.get("uncommitted_changes"),
    }


def build(results_path=RESULTS_PATH, committed_paths=None):
    """Return ``(manifest_rows, summary, diagnostics)`` for the source archive.

    committed_paths is the set of repository-relative paths Git holds unchanged at
    the source commit; None when Git could not be asked, which records ``committed``
    as null rather than guessing.

    Count run directories and their immediate contents, compute date bounds, and
    hash inventoried files. Nested directories and unexpected filenames within a
    run produce blocking diagnostics because they are not supported export inputs.
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

    generated = set(_detail_files())
    for path in consumed_files(results_path):
        row = {
            "path": _relative(path),
            "sha256": sha256_of(path),
            "size_bytes": path.stat().st_size,
            "committed": (None if committed_paths is None
                          else _relative(path) in committed_paths),
            "origin": "source",
        }
        if path in generated:
            row.update(_generated_provenance(path))
        rows.append(row)

    summary = dict(counts)
    summary["dates"] = len(dates)
    summary["data_cutoff"] = max(dates) if dates else None
    summary["first_date"] = min(dates) if dates else None
    summary["files_hashed"] = len(rows)
    return rows, summary, diagnostics
