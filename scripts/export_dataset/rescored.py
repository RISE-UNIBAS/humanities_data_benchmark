"""Field-level detail that today's scorer produces from the stored responses.

The corpus records `field_scores` for only four benchmarks: the other eight gained the key
after their runs had already executed, and this project does not re-score
`results/`. So the dataset's own field-level detail covers four benchmarks and
1,483,079 observations, and there it stops.

`scripts/ndr_export/generate_compare_detail.py` fills that gap for the comparison widget by
running each benchmark's scorer again over the stored responses, and only for inputs whose
stored answer has no `field_scores` -- detail recorded at run time is always preferred. The
result is 619,108 observations across twelve benchmarks with **zero overlap** with the
stored ones. Strictly complementary.

Two reasons this is a separate table rather than more rows in `scores_long`:

  * It is not what the run recorded. It is what the scorer says *now*, against the ground
    truths as they stand now, and 12 inputs already disagree with the score their run
    stored. Mixing the two in one column would let an aggregate silently average a
    historical observation with a present-day re-reading of it.
  * It carries provenance the stored scores cannot have -- which scorer commit, which
    ground-truth commit, which day -- because it was produced by a specific version of code
    that will keep changing.

The exporter still never runs a scorer. It reads the artifact the frontend pipeline
already produced, which becomes a hashed input like `pricing.json`. Where that artifact is
absent the table is simply empty: the dataset must not require the frontend pipeline to
have run.
"""
import json

from scripts.export_dataset.inventory import relative_path
from scripts.results_index import COLLECTED_RESULTS_PATH, read_json

DETAIL_DIR = COLLECTED_RESULTS_PATH / "compare_detail"


def detail_files(root=None):
    """Every `compare_detail/<date>/<test_id>.json`, sorted, or nothing if absent."""
    root = DETAIL_DIR if root is None else root
    if not root.is_dir():
        return []
    return sorted(root.glob("*/*.json"))


def extract(root=None, benchmark_of=None):
    """Returns (rows, payload records, diagnostics).

    `benchmark_of` maps a test id to its benchmark, used only to cross-check the benchmark
    the detail file names for itself. They should agree; a disagreement means one of the
    two pipelines resolved the run differently and is worth a diagnostic rather than a
    silent preference.
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
