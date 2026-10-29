"""Reconcile the dataset export against the frontend export.

Compare run membership, benchmark and configured model identity, visibility,
stored numeric run scores, and resolved prices. Account for representation
differences: the dataset retains request-level records and original score scales,
while the frontend includes normalized scores and selected request metadata.

The frontend export is the website's run export, written by the benchmark-frontend
repository (``python -m generate --data-repo <this repository>``) with its own reader of
this repository's files. Its location is ``BENCHMARK_FRONTEND_EXPORT``, by default the
sibling checkout's ``generated/test_runs_export.json``. The frontend records no price, so
the price it stands for is resolved here: the shared resolver applied to the run's
selected request identity (else its configured one) on the run's date, unbounded in age.
The packager runs the cross-check before release.

Run ``python -m scripts.export_dataset.crosscheck --dataset dataset``.
Return a nonzero exit status when the comparison reports findings.
"""
import argparse
import json
import os
import sys
from pathlib import Path

import pyarrow.parquet as pq

from scripts.pricing_resolver import resolve_pricing
from scripts.results_index import PROJECT_ROOT

FRONTEND_EXPORT = Path(os.environ.get("BENCHMARK_FRONTEND_EXPORT")
                       or PROJECT_ROOT.parent / "benchmark-frontend" / "generated" / "test_runs_export.json")

EXPECTED_DIFFERENCES = """Expected, by design:
  * normalized_score        frontend only -- a value-based scale heuristic, deliberately
                            not a metric definition, so the dataset keeps raw metrics and
                            exports no normalised view.
  * prompt, results, timing frontend only -- the prompt text, one selected request, and
                            run-level timing. The dataset exports every request instead,
                            and the payload sidecars carry the full records.
  * derived_* costs         dataset only -- recomputed per request. The frontend records
                            no price; the one it stands for is resolved here.
  * per-request rows        dataset only -- the frontend keeps one arbitrary request per
                            run, so it cannot express per-request cost or score.
"""


def frontend_price(record):
    """The price in force for a frontend run record, or None.

    The provider/model of its selected request where recorded, as the alias map is keyed
    on those, else the configured ones; the run's date; no age limit, so a stale bucket
    resolves with its age rather than not at all.
    """
    request = record.get("results")
    provider = model = None
    if isinstance(request, dict):
        provider, model = request.get("provider"), request.get("model")
    if not (provider and model):
        config = record.get("config") or {}
        provider, model = config.get("provider"), config.get("model")
    if not (provider and model and record.get("date")):
        return None
    pricing = resolve_pricing(provider, model, record["date"], max_age_days=None)
    if pricing is None:
        return None
    return {"bucket_date": pricing.bucket_date, "age_days": pricing.age_days,
            "input_price_per_million": pricing.input_price,
            "output_price_per_million": pricing.output_price}


def load_frontend():
    if not FRONTEND_EXPORT.is_file():
        raise SystemExit("No frontend export at %s. Run `python -m generate --data-repo %s` in "
                         "benchmark-frontend first, or set BENCHMARK_FRONTEND_EXPORT."
                         % (FRONTEND_EXPORT, PROJECT_ROOT))
    records = json.loads(FRONTEND_EXPORT.read_bytes().decode("utf-8"))
    for record in records:
        record["pricing"] = frontend_price(record)
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
                            ("total_output_tokens", "recorded_total_output_tokens"),
                            ("total_reasoning_tokens", "recorded_total_reasoning_tokens"),
                            ("reasoning_cost_usd", "recorded_reasoning_cost_usd")):
            theirs = summary.get(key)
            mine = ours[column]
            if theirs is None and mine is None:
                continue
            if theirs is None or mine is None or abs(float(theirs) - float(mine)) > 1e-9:
                note("recorded_cost", "%s %s: %r vs %r" % (run_id, key, mine, theirs))

    # --- 5. the price each pipeline resolved --------------------------------------
    # Both sides use the same resolver, so a disagreement means they fed it different
    # provider/model identities -- which is exactly the aliasing question the dataset
    # exports two columns for.
    #
    # This compared only (bucket_date, input_price), which made "same resolved price" a
    # far weaker claim than it read as: adding 999 to every output rate in the dataset
    # produced no finding at all. Both rates are compared now, and a run where only one
    # side resolved a price is reported rather than skipped -- one pipeline finding a
    # price where the other found none is exactly the disagreement worth seeing.
    prices = {}
    for row in requests:
        if row["pricing_bucket_date"]:
            prices.setdefault(row["run_id"], set()).add((
                row["pricing_bucket_date"],
                row["pricing_input_price_per_million"],
                row["pricing_output_price_per_million"],
            ))

    for run_id in shared:
        theirs = frontend[run_id].get("pricing")
        mine = prices.get(run_id)

        if theirs and not mine:
            note("pricing_missing",
                 "%s: the frontend resolved %s/%s at %s, the dataset resolved no price"
                 % (run_id, theirs["input_price_per_million"],
                    theirs["output_price_per_million"], theirs["bucket_date"]))
            continue
        if mine and not theirs:
            note("pricing_missing",
                 "%s: the dataset resolved %s, the frontend resolved no price"
                 % (run_id, sorted(mine)[:1]))
            continue
        if not theirs:
            continue

        expected = (theirs["bucket_date"], theirs["input_price_per_million"],
                    theirs["output_price_per_million"])
        if expected not in mine:
            note("pricing", "%s: frontend resolved %r, dataset resolved %s"
                 % (run_id, expected, sorted(mine)[:2]))
        if len(mine) > 1:
            # The frontend prices one selected request per run; the dataset prices each.
            # More than one resolved price in a run means the requests disagree about who
            # served them, and a single frontend figure cannot represent the run.
            note("pricing_identity_split",
                 "%s: requests in this run resolved %d different prices: %s"
                 % (run_id, len(mine), sorted(mine)[:3]))

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
