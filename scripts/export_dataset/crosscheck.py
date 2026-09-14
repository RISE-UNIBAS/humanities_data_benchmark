"""Reconcile the dataset export against the frontend export.

Two pipelines read the same result tree and disagree about what to do with it. The frontend
may skip what it cannot chart, keeps one request per run, and normalises scores onto a
common scale; the dataset export keeps everything, flattens every request, and refuses to
normalise. Those are design differences, not defects, and this compares the two anyway --
because a difference that is *not* on that list is a defect, and there is no other way to
find it.

Plan §9 step 7. It is a diagnostic, not a gate: the frontend export is not an independent
oracle, since both pipelines now read the corpus through `scripts/results_index.py`. What
it can still catch is the two of them disagreeing about a run's identity, its visibility,
its recorded scores or its prices -- places where one of them has misread a file the other
read correctly.

    python -m scripts.export_dataset.crosscheck [--dataset dataset]

Exits non-zero when a difference falls outside the expected set.
"""
import argparse
import json
import sys
from pathlib import Path

import pyarrow.parquet as pq

from scripts.results_index import COLLECTED_RESULTS_PATH

FRONTEND_EXPORT = COLLECTED_RESULTS_PATH / "test_runs_export.json"

EXPECTED_DIFFERENCES = """Expected, by design:
  * normalized_score        frontend only -- a value-based scale heuristic, deliberately
                            not a metric definition (plan §8), so the dataset keeps raw
                            metrics and exports no normalised view.
  * prompt, results, timing frontend only -- the prompt text, one selected request, and
                            run-level timing. The dataset exports every request instead,
                            and the payload sidecars carry the full records.
  * derived_* costs         dataset only -- recomputed per request. The frontend records
                            the price in force but does not apply it.
  * per-request rows        dataset only -- the frontend keeps one arbitrary request per
                            run, so it cannot express per-request cost or score.
"""


def load_frontend():
    if not FRONTEND_EXPORT.is_file():
        raise SystemExit("No frontend export at %s. Run "
                         "`python -m scripts.ndr_export.generate_all` first."
                         % FRONTEND_EXPORT)
    records = json.loads(FRONTEND_EXPORT.read_bytes().decode("utf-8"))
    return dict(("%s@%s" % (r["test_id"], r["date"]), r) for r in records)


def load_dataset(dataset_dir):
    dataset_dir = Path(dataset_dir)
    runs = pq.read_table(dataset_dir / "runs.parquet").to_pylist()
    requests = pq.read_table(dataset_dir / "requests.parquet").to_pylist()
    scores = pq.read_table(dataset_dir / "scores_long.parquet").to_pylist()
    return runs, requests, scores


def compare(runs, requests, scores, frontend):
    findings = []

    def note(kind, detail):
        findings.append({"check": kind, "detail": detail})

    by_id = dict((r["run_id"], r) for r in runs)

    # --- 1. the same set of runs ------------------------------------------------
    only_dataset = sorted(set(by_id) - set(frontend))
    only_frontend = sorted(set(frontend) - set(by_id))
    if only_dataset:
        note("run_set", "%d runs in the dataset but not the frontend export: %s"
             % (len(only_dataset), only_dataset[:5]))
    if only_frontend:
        note("run_set", "%d runs in the frontend export but not the dataset: %s"
             % (len(only_frontend), only_frontend[:5]))

    shared = sorted(set(by_id) & set(frontend))

    # --- 2. identity and visibility ---------------------------------------------
    for run_id in shared:
        ours, theirs = by_id[run_id], frontend[run_id]
        if ours["benchmark"] != theirs.get("benchmark"):
            note("benchmark", "%s: %r vs %r"
                 % (run_id, ours["benchmark"], theirs.get("benchmark")))
        if bool(ours["hidden"]) != bool(theirs.get("hidden")):
            note("hidden", "%s: %r vs %r" % (run_id, ours["hidden"], theirs.get("hidden")))
        config = theirs.get("config") or {}
        if ours["configured_provider"] != config.get("provider"):
            note("provider", "%s: %r vs %r"
                 % (run_id, ours["configured_provider"], config.get("provider")))
        if ours["configured_model"] != config.get("model"):
            note("model", "%s: %r vs %r"
                 % (run_id, ours["configured_model"], config.get("model")))

    # --- 3. recorded scores -------------------------------------------------------
    # The frontend copies scoring.json verbatim; the dataset splits it into numeric
    # observations and a cost summary. Every numeric metric there should appear here.
    run_scores = {}
    for row in scores:
        if row["level"] == "run":
            run_scores.setdefault(row["run_id"], {})[row["metric_id"]] = row["value"]

    for run_id in shared:
        theirs = frontend[run_id].get("scoring") or {}
        ours = run_scores.get(run_id, {})
        benchmark = by_id[run_id]["benchmark"]
        for key, value in theirs.items():
            if key == "cost_summary" or isinstance(value, (dict, list, str)):
                continue
            if isinstance(value, bool):
                continue
            metric_id = "%s.run.%s" % (benchmark, key)
            if metric_id not in ours:
                note("score_missing", "%s: %s is in scoring.json but not scores_long"
                     % (run_id, metric_id))
            elif abs(ours[metric_id] - float(value)) > 1e-12:
                note("score_value", "%s %s: %r vs %r"
                     % (run_id, metric_id, ours[metric_id], value))

    # --- 4. recorded cost summaries ----------------------------------------------
    for run_id in shared:
        summary = (frontend[run_id].get("scoring") or {}).get("cost_summary") or {}
        ours = by_id[run_id]
        for key, column in (("total_cost_usd", "recorded_total_cost_usd"),
                            ("total_input_tokens", "recorded_total_input_tokens"),
                            ("total_output_tokens", "recorded_total_output_tokens")):
            theirs = summary.get(key)
            mine = ours[column]
            if theirs is None and mine is None:
                continue
            if theirs is None or mine is None or abs(float(theirs) - float(mine)) > 1e-9:
                note("recorded_cost", "%s %s: %r vs %r" % (run_id, key, mine, theirs))

    # --- 5. the price each pipeline resolved --------------------------------------
    # Both call the same resolver, so a disagreement means they fed it different
    # provider/model identities -- which is exactly the aliasing question the dataset
    # exports two columns for.
    prices = {}
    for row in requests:
        if row["pricing_bucket_date"]:
            prices.setdefault(row["run_id"], set()).add(
                (row["pricing_bucket_date"], row["pricing_input_price_per_million"]))

    for run_id in shared:
        theirs = frontend[run_id].get("pricing")
        mine = prices.get(run_id)
        if not theirs or not mine:
            continue
        expected = (theirs["bucket_date"], theirs["input_price_per_million"])
        if expected not in mine:
            note("pricing", "%s: frontend resolved %r, dataset resolved %s"
                 % (run_id, expected, sorted(mine)[:2]))

    return findings, len(shared)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--dataset", default="dataset")
    parser.add_argument("--max-report", type=int, default=10)
    args = parser.parse_args(argv)

    frontend = load_frontend()
    runs, requests, scores = load_dataset(args.dataset)

    print("dataset : %d runs, %d requests, %d score observations"
          % (len(runs), len(requests), len(scores)))
    print("frontend: %d runs\n" % len(frontend))

    findings, shared = compare(runs, requests, scores, frontend)
    print("compared %d runs present in both\n" % shared)

    if not findings:
        print("No unexpected differences.\n")
        print(EXPECTED_DIFFERENCES)
        return 0

    by_check = {}
    for finding in findings:
        by_check.setdefault(finding["check"], []).append(finding["detail"])
    for check in sorted(by_check):
        details = by_check[check]
        print("%-16s %d" % (check, len(details)))
        for detail in details[:args.max_report]:
            print("    %s" % detail)
        if len(details) > args.max_report:
            print("    ... and %d more" % (len(details) - args.max_report))
    print()
    print(EXPECTED_DIFFERENCES)
    return 1


if __name__ == "__main__":
    sys.exit(main())
