"""Build the dataset: `python -m scripts.export_dataset`.

Writes into a staging directory and moves it into place only after every table has been
written, checked for duplicate keys and read back from CSV. A build that fails leaves the
previous one exactly as it was, which matters because the alternative -- a half-written
`dataset/` that still looks like a release -- is worse than no build at all.

`--date`, `--benchmark` and `--limit` exist for development. Any of them stamps
`partial: true` in the manifest, because a subset must never be mistaken for a release.
"""
import argparse
import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from scripts.export_dataset import (DATASET_PATH, SCHEMA_VERSION, STAGING_SUFFIX,
                                    default_dataset_version)
from scripts.export_dataset import columns, coverage, docs, inventory, metrics, writers
from scripts.export_dataset.extract import Extractor
from scripts.export_dataset.paths import check as check_paths
from scripts.export_dataset.schema import SCHEMAS_FOR_DOCS, SORT_KEYS, TABLES, UNIQUE_KEYS
from scripts.ndr_export.pricing_resolver import pricing_table_version
from scripts.results_index import PROJECT_ROOT, RESULTS_PATH, TestCatalog, iter_run_dirs


def _git(*args):
    """(output, error). `output` is None whenever the command did not succeed.

    The previous version returned `out.stdout.strip() or None` and ignored the exit code,
    so `bool(_git("status", "--porcelain"))` read a *failed* git as a clean worktree. The
    audit hit exactly that: git refused the checkout on ownership grounds, the commit came
    back null, and the artifact recorded `source_worktree_dirty: false` -- a provenance
    claim manufactured out of an error. Unknown has to stay unknown.
    """
    try:
        out = subprocess.run(("git",) + args, cwd=str(PROJECT_ROOT),
                             capture_output=True, text=True, timeout=30)
    except FileNotFoundError:
        return None, "git executable not found"
    except subprocess.TimeoutExpired:
        return None, "git timed out"
    except (OSError, subprocess.SubprocessError) as error:
        return None, str(error)
    if out.returncode != 0:
        return None, (out.stderr or "").strip() or "git exited %d" % out.returncode
    return out.stdout.strip(), None


def _selected_runs(results_path, date, benchmark, limit, catalog):
    runs = list(iter_run_dirs(results_path))
    if date:
        runs = [r for r in runs if r.date == date]
    if benchmark:
        runs = [r for r in runs if catalog.benchmark_of(r.test_id) == benchmark]
    if limit:
        runs = runs[:limit]
    return runs


def build(source=RESULTS_PATH, out=DATASET_PATH, date=None, benchmark=None, limit=None,
          dataset_version=None, serial=1):
    started = datetime.now(timezone.utc)
    partial = bool(date or benchmark or limit)
    catalog = TestCatalog.load()

    staging = out.with_name(out.name + STAGING_SUFFIX)
    previous = out.with_name(out.name + ".previous")
    # Before any mkdir or rmtree: a refusal must leave the filesystem untouched.
    check_paths(source=source, out=out, staging=staging, previous=previous)

    if staging.exists():
        shutil.rmtree(staging)
    (staging / "payloads").mkdir(parents=True)

    columns.check_complete(SCHEMAS_FOR_DOCS)

    print("Inventory ...")
    manifest_rows, summary, inv_diagnostics = inventory.build(source)
    print("  %d files hashed, %d run directories, %d request files, %d scoring files"
          % (summary["files_hashed"], summary["run_dirs"], summary["request_files"],
             summary["scoring_files"]))

    print("Extract ...")
    extractor = Extractor(results_path=source, catalog=catalog)
    if partial:
        selected = _selected_runs(source, date, benchmark, limit, catalog)
        print("  partial build: %d run directories selected" % len(selected))
        for run in selected:
            extractor._one_run(run)
        if extractor._unknown_metrics:
            raise ValueError("undefined metrics: %s"
                             % sorted(set(extractor._unknown_metrics)))
    else:
        extractor.run()
    print("  %d runs, %d requests, %d score observations"
          % (len(extractor.runs), len(extractor.requests), len(extractor.scores)))

    print("Write tables ...")
    counts = {}
    for name, rows in (("runs", extractor.runs),
                       ("requests", extractor.requests),
                       ("scores_long", extractor.scores),
                       ("metrics", metrics.DICTIONARY)):
        counts[name] = writers.write_table(staging, name, rows, TABLES[name],
                                           SORT_KEYS[name], UNIQUE_KEYS[name])
        print("  %-12s %8d rows" % (name, counts[name]))

    print("Write payloads ...")
    payload_counts = {}
    for bench in sorted(extractor.payloads):
        sidecar = writers.JsonlGz(staging / "payloads" / ("%s.jsonl.gz" % bench))
        for record in sorted(extractor.payloads[bench],
                             key=lambda r: (r["run_id"], r["object_id"] or "")):
            sidecar.write(record)
        sidecar.close()
        payload_counts[bench] = sidecar.count

    run_sidecar = writers.JsonlGz(staging / "payloads" / "run_scoring.jsonl.gz")
    for record in sorted(extractor.run_payloads, key=lambda r: r["run_id"]):
        run_sidecar.write(record)
    run_sidecar.close()
    payload_counts["run_scoring"] = run_sidecar.count

    for path in extractor.invalid_sources:
        # The same namespace the tables and manifests use. relative_to(PROJECT_ROOT)
        # raised outright for a build whose --source lies outside the repository.
        relative = inventory.relative_path(path, source)
        target = staging / "payloads" / "invalid" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)

    print("Coverage ...")
    coverage_rows = coverage.build({
        "runs": (extractor.runs, TABLES["runs"]),
        "requests": (extractor.requests, TABLES["requests"]),
        "scores_long": (extractor.scores, TABLES["scores_long"]),
    })
    writers.write_coverage(staging / "coverage.csv", coverage_rows)
    print("  %d rows" % len(coverage_rows))

    print("Copy examples ...")
    examples_src = Path(__file__).parent / "examples"
    if examples_src.is_dir():
        examples_dst = staging / "examples"
        examples_dst.mkdir(parents=True, exist_ok=True)
        for script in sorted(examples_src.glob("*.py")):
            shutil.copyfile(script, examples_dst / script.name)
            print("  %s" % script.name)

    print("Write manifests ...")
    with open(staging / "source_manifest.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for row in manifest_rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")

    diagnostics = inv_diagnostics + extractor.diagnostics
    with open(staging / "diagnostics.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for row in sorted(diagnostics, key=lambda d: (d["source_path"], d["issue"])):
            f.write(json.dumps(row, sort_keys=True) + "\n")

    outputs = {}
    for path in sorted(staging.rglob("*")):
        if path.is_file() and path.name != "manifest.json":
            outputs[path.relative_to(staging).as_posix()] = inventory.sha256_of(path)

    commit, commit_error = _git("rev-parse", "HEAD")
    status, status_error = _git("status", "--porcelain")
    dirty = None if status_error is not None else bool(status)
    provenance = "verified" if commit and status_error is None else "unknown"
    if provenance == "unknown":
        print("  WARNING: git provenance unavailable (%s); source_worktree_dirty is null"
              % (commit_error or status_error))

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "dataset_version": dataset_version or default_dataset_version(
            summary["data_cutoff"], serial),
        "partial": partial,
        "build_filters": {"date": date, "benchmark": benchmark, "limit": limit},
        "data_cutoff": summary["data_cutoff"],
        "first_date": summary["first_date"],
        "source_commit": commit,
        # Nullable: false means git said so, not that git failed to say otherwise.
        "source_worktree_dirty": dirty,
        "source_provenance": provenance,
        "pricing_table_version": pricing_table_version(),
        "python": platform.python_version(),
        "pyarrow": __import__("pyarrow").__version__,
        "parquet_version": writers.PARQUET_VERSION,
        "parquet_compression": writers.PARQUET_COMPRESSION,
        "inventory": summary,
        "row_counts": counts,
        "payload_counts": payload_counts,
        "diagnostic_counts": _tally(diagnostics),
        "output_sha256": outputs,
        "build_started_utc": started.isoformat(),
    }
    with open(staging / "manifest.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
        f.write("\n")

    print("Documentation ...")
    software_citation = _software_citation()
    written = {
        "datapackage.json": json.dumps(docs.datapackage(manifest), indent=2,
                                       sort_keys=True) + "\n",
        "README.md": docs.readme(manifest),
        "CHANGELOG.md": docs.changelog(manifest),
        "CITATION.cff": docs.citation(manifest, software_citation),
    }
    for name, text in written.items():
        (staging / name).write_text(text, encoding="utf-8", newline="\n")
        print("  %s" % name)

    # These are written after the manifest, so hash them into it separately rather than
    # leaving five release files outside the integrity record.
    for name in ["coverage.csv"] + list(written):
        manifest["output_sha256"][name] = inventory.sha256_of(staging / name)
    with open(staging / "manifest.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
        f.write("\n")

    writers.publish(staging, out)
    print("\nPublished %s" % out)
    if diagnostics:
        print("Diagnostics: %s" % manifest["diagnostic_counts"])
    return manifest


def _software_citation():
    """The repository's CITATION.cff authors, so the dataset credits the same people.

    Parsed with PyYAML when it is available and skipped otherwise: the dataset should
    still build without it, with the authors simply absent rather than the build failing.
    """
    path = PROJECT_ROOT / "CITATION.cff"
    if not path.is_file():
        return None
    try:
        import yaml
    except ImportError:
        print("  (PyYAML not installed: dataset CITATION.cff will list no authors)")
        return None
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as error:
        print("  (could not read CITATION.cff: %s)" % error)
        return None


def _tally(diagnostics):
    counts = {}
    for row in diagnostics:
        counts[row["issue"]] = counts.get(row["issue"], 0) + 1
    return counts


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m scripts.export_dataset",
                                     description=__doc__.split("\n")[0])
    parser.add_argument("--source", default=str(RESULTS_PATH))
    parser.add_argument("--out", default=str(DATASET_PATH))
    parser.add_argument("--date", help="one date folder (development only)")
    parser.add_argument("--benchmark", help="one benchmark (development only)")
    parser.add_argument("--limit", type=int, help="first N runs (development only)")
    parser.add_argument("--dataset-version",
                        help="release identifier; defaults to <data_cutoff>.<serial>")
    parser.add_argument("--serial", type=int, default=1,
                        help="bump when re-releasing corrected data at the same cutoff")
    args = parser.parse_args(argv)

    build(source=Path(args.source), out=Path(args.out), date=args.date,
          benchmark=args.benchmark, limit=args.limit,
          dataset_version=args.dataset_version, serial=args.serial)
    return 0


if __name__ == "__main__":
    sys.exit(main())
