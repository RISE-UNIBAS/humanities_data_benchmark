"""Field-level comparison detail for runs whose scorer did not record any.

The comparison view shows what a benchmark's scorer compared, field by field, taken from
`score.field_scores` in the stored answer. Scorers record that themselves -- but only
four of twelve did so historically, and those four gained it on different dates, so the
detail is missing for most stored runs. This step fills the gap by re-running each
scorer offline (see `scripts/offline_scoring.py`); no model call is involved.

Two rules keep the result honest.

**The archive is not rewritten.** `results/` is the source archive, and a recomputed
value written back into a request file would sit in the same object as metrics computed at
run time, with nothing marking the seam. The detail goes here instead.

**Run-time detail wins.** Where the stored answer already carries `field_scores`, it was
computed against the ground truth as it stood that day, so it is strictly more faithful
than anything recomputed now. Those inputs are skipped and the view reads them from the
request file. Only what is genuinely absent is computed here, and it is labelled: ground
truths are revised (568 stored scores no longer reproduce), so re-scored detail reflects
today's truth, not the run's. `reproduces_stored_score` records that per input, and where
it is false both metric sets are kept -- that divergence is a measurement of ground-truth
revision, and the dataset's README explains it to anyone reading the exported table.

Output: collected_results/compare_detail/<date>/<test_id>.json, one file per run that
needs any, so the view fetches only the run it is showing.

    {
      "test_id": "T1597", "date": "2026-08-18", "benchmark": "magazine_pages",
      "source": "rescored",
      "rescored": "2026-09-10",
      "scorer_revision": "<commit that last touched the benchmark>",
      "ground_truth_revision": "<commit that last touched its ground truths>",
      "inputs": {
        "0002_p002": {
          "field_scores": {"box 0": {"response": ..., "ground_truth": ..., "score": 0.97}},
          "reproduces_stored_score": true
        }
      },
      "diagnostics": {"<object_id>": "AttributeError: ..."}
    }
"""
import argparse
import gzip
import json
import logging
import subprocess
import sys
from collections import Counter
from datetime import date as date_type
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.resolve()))

from scripts.ndr_export import BENCHMARKS_PATH, EXPORT_PATH
from scripts.offline_scoring import (iter_run_inputs, iter_runs, load_scorer,
                                     numeric_metrics, read_tests, rules_of_test)

DETAIL_DIR = EXPORT_PATH / "compare_detail"

logger = logging.getLogger(__name__)


def git_revision(path):
    """The commit that last touched `path`, or None outside a checkout."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%H", "--", str(path)],
            cwd=str(BENCHMARKS_PATH.parent), capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    revision = result.stdout.strip()
    return revision or None


def is_dirty(path):
    """Whether `path` has uncommitted changes, so a commit hash does not describe it."""
    try:
        result = subprocess.run(["git", "status", "--porcelain", "--", str(path)],
                                cwd=str(BENCHMARKS_PATH.parent), capture_output=True,
                                text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return bool(result.stdout.strip())


def revisions_for(benchmark, cache):
    """Provenance for one benchmark, resolved once.

    The commit that last touched the scorer does not describe the scorer that ran if the
    working tree is dirty, so a commit-only provenance claim from a dirty tree is not one.
    The dirty state is recorded rather than silently implied. A deploy builds from a clean
    checkout, which clears it.
    """
    if benchmark not in cache:
        scorer_path = BENCHMARKS_PATH / benchmark / "benchmark.py"
        truth_path = BENCHMARKS_PATH / benchmark / "ground_truths"
        cache[benchmark] = {
            "scorer_revision": git_revision(scorer_path),
            "ground_truth_revision": git_revision(truth_path),
            "uncommitted_changes": sorted(
                name for name, path in (("scorer", scorer_path),
                                        ("ground_truths", truth_path))
                if is_dirty(path)) or None,
        }
    return cache[benchmark]


def detail_for_run(run_dir, test_id, benchmark, scorer, tally):
    """The inputs of one run that need re-scored detail, plus any scorer diagnostics."""
    inputs, diagnostics = {}, {}

    for object_id, record, answer, truth in iter_run_inputs(run_dir, test_id):
        stored = record.get("score")
        if isinstance(stored, dict) and "field_scores" in stored:
            # Recorded at run time, against that day's ground truth. Leave it there.
            tally["kept run-time detail"] += 1
            continue

        try:
            fresh = scorer.score_request_answer(object_id, answer, truth)
        except Exception as error:
            # A scorer that cannot run is a finding, not something to drop silently:
            # an absent entry would read as "the scorer recorded nothing".
            diagnostics[object_id] = "%s: %s" % (type(error).__name__, error)
            tally["scorer raised"] += 1
            continue

        fields = (fresh or {}).get("field_scores")
        if not fields:
            tally["no detail produced"] += 1
            continue

        entry = {"field_scores": fields}
        if isinstance(stored, dict):
            stored_metrics = numeric_metrics(stored)
            fresh_metrics = numeric_metrics(fresh)
            reproduces = stored_metrics == fresh_metrics
            entry["reproduces_stored_score"] = reproduces
            if not reproduces:
                # Keep both: the divergence is the record of a ground-truth revision.
                entry["stored_metrics"] = stored_metrics
                entry["rescored_metrics"] = fresh_metrics
                tally["differs from stored"] += 1
            else:
                tally["reproduces stored"] += 1
        else:
            entry["reproduces_stored_score"] = None
            tally["no stored score"] += 1

        inputs[object_id] = entry

    return inputs, diagnostics


def generate_compare_detail(benchmark=None, limit=0, measure=False, only_missing=False):
    """Writes collected_results/compare_detail/<date>/<test_id>.json."""
    tests = read_tests()
    today = date_type.today().isoformat()
    scorers, revisions, tally = {}, {}, Counter()
    written, raw_bytes, gzip_bytes = 0, 0, 0
    per_benchmark = Counter()

    targets = list(iter_runs(benchmark))
    if limit:
        targets = targets[-limit:]

    for run_dir, test_id, name in targets:
        out_path = DETAIL_DIR / run_dir.parent.name / (test_id + ".json")
        if only_missing and out_path.is_file():
            tally["already present"] += 1
            continue

        if name not in scorers:
            try:
                scorers[name] = load_scorer(name)
            except Exception as error:
                logger.warning("Cannot load %s: %s", name, error)
                tally["scorer unavailable"] += 1
                continue
        scorer = scorers[name]
        # Per run: personnel_cards selects which fields it scores from the run's rules.
        scorer.rules = rules_of_test(test_id, tests)

        inputs, diagnostics = detail_for_run(run_dir, test_id, name, scorer, tally)
        if not inputs and not diagnostics:
            tally["nothing to write"] += 1
            continue

        document = {
            "test_id": test_id,
            "date": run_dir.parent.name,
            "benchmark": name,
            "source": "rescored",
            "rescored": today,
            "inputs": inputs,
        }
        document.update(revisions_for(name, revisions))
        if document.get("uncommitted_changes") is None:
            document.pop("uncommitted_changes")
        if diagnostics:
            document["diagnostics"] = diagnostics

        blob = json.dumps(document, ensure_ascii=False, sort_keys=True).encode("utf-8")
        raw_bytes += len(blob)
        # git zlib-compresses every blob it stores, so the compressed size is the honest
        # estimate of what this costs the repository -- not the working-tree size.
        gzip_bytes += len(gzip.compress(blob, 6))
        per_benchmark[name] += len(blob)
        written += 1

        if not measure:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(blob)

    verb = "would write" if measure else "wrote"
    print("  %s %d run file(s) to %s" % (verb, written, DETAIL_DIR))
    print("  %-22s %.1f MB" % ("working tree", raw_bytes / 1024 / 1024))
    print("  %-22s %.1f MB  (what git stores)" % ("compressed",
                                                  gzip_bytes / 1024 / 1024))
    if raw_bytes:
        print("  %-22s %.1fx" % ("compression", raw_bytes / max(gzip_bytes, 1)))
    for key in ("reproduces stored", "differs from stored", "no stored score",
                "kept run-time detail", "no detail produced", "scorer raised",
                "nothing to write", "already present", "scorer unavailable"):
        if tally[key]:
            print("  %-22s %d" % (key, tally[key]))
    if per_benchmark:
        print("\n  %-26s %10s" % ("benchmark", "MB"))
        for name, size in per_benchmark.most_common():
            print("  %-26s %10.1f" % (name, size / 1024 / 1024))

    return written


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--benchmark", help="limit to one benchmark")
    parser.add_argument("--limit", type=int, default=0, help="use only the newest N runs")
    parser.add_argument("--measure", action="store_true",
                        help="report sizes without writing anything")
    parser.add_argument("--only-missing", action="store_true",
                        help="skip runs whose detail file already exists")
    args = parser.parse_args()

    logging.disable(logging.CRITICAL)  # the scorers log per field at INFO
    generate_compare_detail(benchmark=args.benchmark, limit=args.limit,
                            measure=args.measure, only_missing=args.only_missing)


if __name__ == "__main__":
    main()
