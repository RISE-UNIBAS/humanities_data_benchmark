"""Import supplementary field evaluations from comparison-detail artifacts.

The comparison pipeline re-scores stored responses that lack original field
detail. This module reads those artifacts into rescored_fields and payload
records without executing scorers or modifying the original results.

Keep supplementary evaluations separate from scores_long and preserve the
recorded scoring date, scorer and ground-truth revisions, dirty-state indicator,
and agreement with stored metrics where available. Inventory includes these
artifacts as hashed inputs.

Missing artifacts yield no supplementary rows. Coverage diagnostics distinguish
absent detail from potentially stale or incomplete detail at the run level.
"""
import json

from scripts.export_dataset.inventory import relative_path
from scripts.results_index import COLLECTED_RESULTS_PATH, read_json

DETAIL_DIR = COLLECTED_RESULTS_PATH / "compare_detail"


def detail_files(root=None):
    """Return sorted comparison-detail JSON paths, or an empty list if absent."""
    root = DETAIL_DIR if root is None else root
    if not root.is_dir():
        return []
    return sorted(root.glob("*/*.json"))


def extract(root=None, benchmark_of=None):
    """Return ``(rows, payload_records, diagnostics)`` from comparison-detail files.

    Emit one row per field, retaining null scores and available provenance.
    Malformed files or missing run identities produce warnings and no rows.

    If benchmark_of is provided, use its test-to-benchmark mapping to check artifact
    identities. Prefer the mapped benchmark on disagreement and emit a diagnostic.
    """
    rows, payloads, diagnostics = [], [], []

    for path in detail_files(root):
        source = relative_path(path)
        read = read_json(path)
        if read.status != "ok" or not isinstance(read.value, dict):
            diagnostics.append({
                "source_path": source,
                "issue": "unreadable_compare_detail",
                "severity": "warning",
                "handling": "no rescored rows for this run",
            })
            continue

        detail = read.value
        test_id = detail.get("test_id")
        date = detail.get("date")
        if not test_id or not date:
            diagnostics.append({
                "source_path": source,
                "issue": "compare_detail_without_identity",
                "severity": "warning",
                "handling": "no rescored rows; the file names neither a test id nor a date",
            })
            continue

        run_id = "%s@%s" % (test_id, date)
        benchmark = detail.get("benchmark")
        if benchmark_of is not None:
            expected = benchmark_of.get(test_id)
            if expected and benchmark and expected != benchmark:
                diagnostics.append({
                    "source_path": source,
                    "issue": "compare_detail_benchmark_mismatch",
                    "severity": "warning",
                    "handling": "rows keep the configuration's benchmark (%s), not the "
                                "detail file's (%s)" % (expected, benchmark),
                })
            benchmark = expected or benchmark

        dirty = detail.get("uncommitted_changes")
        provenance = {
            "rescored_date": detail.get("rescored"),
            "scorer_revision": detail.get("scorer_revision"),
            "ground_truth_revision": detail.get("ground_truth_revision"),
            "scorer_dirty": None if dirty is None else bool(dirty),
        }

        for object_id, entry in sorted((detail.get("inputs") or {}).items()):
            if not isinstance(entry, dict):
                continue
            reproduces = entry.get("reproduces_stored_score")
            fields = entry.get("field_scores")
            if not isinstance(fields, dict):
                continue

            payloads.append({
                "run_id": run_id,
                "object_id": object_id,
                "source_path": source,
                "source_record": entry,
            })

            for field_path, compared in sorted(fields.items()):
                score = compared.get("score") if isinstance(compared, dict) else None
                if isinstance(score, bool) or not isinstance(score, (int, float)):
                    score = None
                rows.append(dict(provenance, **{
                    "run_id": run_id,
                    "object_id": object_id,
                    "benchmark": benchmark,
                    "field_path": str(field_path),
                    "score": None if score is None else float(score),
                    "reproduces_stored_score": (None if reproduces is None
                                                else bool(reproduces)),
                }))

    return rows, payloads, diagnostics


def coverage_diagnostics(rows, runs, stored_field_run_ids):
    """Return run-level diagnostics for absent, stale, or incomplete field detail.

    A run is covered when either stored or supplementary data contains a field
    observation for it. With no supplementary rows, return an absence warning.
    Otherwise, uncovered runs dated after the latest recorded re-scoring date produce
    a blocking stale-detail diagnostic; other uncovered runs produce a warning.
    Missing re-scoring dates also produce a warning.

    This date-based check cannot establish that every older run was processed or
    that all requests within a covered run have field detail.
    """
    detail_dir = relative_path(DETAIL_DIR)
    if not rows:
        return [{
            "source_path": detail_dir,
            "issue": "rescored_detail_absent",
            "severity": "warning",
            "handling": "rescored_fields is empty; field-level detail covers only the "
                        "benchmarks that recorded it at run time",
        }]

    covered = set(row["run_id"] for row in rows) | set(stored_field_run_ids)
    uncovered = [run for run in runs if run["run_id"] not in covered]
    dates = [row["rescored_date"] for row in rows if row.get("rescored_date")]
    last = max(dates) if dates else None

    stale = [run for run in uncovered if last and run["date"] > last]
    stale_ids = set(run["run_id"] for run in stale)
    seen = [run for run in uncovered if run["run_id"] not in stale_ids]

    diagnostics = []
    if stale:
        diagnostics.append({
            "source_path": detail_dir,
            "issue": "rescored_detail_stale",
            "severity": "blocking",
            "handling": "%d run(s) dated after the last regeneration (%s) have no "
                        "field-level detail from either source, the newest dated %s. "
                        "Regenerate with python -m scripts.ndr_export.generate_compare_detail "
                        "and rebuild." % (len(stale), last,
                                          max(run["date"] for run in stale)),
        })
    if seen:
        diagnostics.append({
            "source_path": detail_dir,
            "issue": "rescored_detail_incomplete",
            "severity": "warning",
            "handling": "%d run(s) carry no field-level detail from either source (%s). "
                        "All predate the last regeneration (%s), so the scorer saw them "
                        "and produced none: a run without an answer, or a scorer that "
                        "reports no per-field similarity."
                        % (len(seen), _by_benchmark(seen), last),
        })
    if last is None:
        diagnostics.append({
            "source_path": detail_dir,
            "issue": "rescored_detail_undated",
            "severity": "warning",
            "handling": "no detail file records the day it was generated, so the export "
                        "cannot tell whether it covers the whole corpus",
        })
    return diagnostics


def _by_benchmark(runs):
    counts = {}
    for run in runs:
        counts[run["benchmark"]] = counts.get(run["benchmark"], 0) + 1
    return ", ".join("%s %d" % (name, counts[name]) for name in sorted(counts))
