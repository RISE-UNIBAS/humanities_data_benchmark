"""Import supplementary field evaluations from comparison-detail artifacts.

The comparison pipeline re-scores stored responses that lack original field
detail. This module reads those artifacts into rescored_fields and payload
records without executing scorers or modifying the original results.

Keep supplementary evaluations separate from scores_long and preserve the
recorded scoring date, scorer and ground-truth revisions, dirty-state indicator,
and agreement with stored metrics where available. Inventory includes these
artifacts as hashed inputs.

Missing artifacts yield no supplementary rows.
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
