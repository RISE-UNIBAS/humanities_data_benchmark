"""Cost per correct extraction on `business_letters`, by provider and over time.

This is the question the dataset was built to answer, and it is here because answering it
takes more care than it looks. Four traps, in the order an analyst hits them:

**The denominator is not F1.** A correct extraction is one true positive in one of the three
categories this benchmark scores -- `send_date`, `sender_persons`, `receiver_persons`. The
unit is a category-level extraction, not a fully correct letter, and an F1 score is not a
count of anything. The per-category counts live only on request rows: `scoring.json` for
this benchmark records `f1_macro` and `f1_micro` and nothing else, so a run-level analysis
cannot answer this at all.

**An unscored request is not a wrong one.** Roughly two in five saved requests carry no TP
counts -- the scorer returns nothing when a ground truth is unusable, and the older runs
predate the current scorer. Treating those as zero correct extractions would inflate every
ratio. They are excluded from the ratio and counted in the coverage figure instead.

**Observed spend is not total spend.** The runner does not save a request when the answer
is `None`, and a same-day re-run overwrites the earlier one, so the stored requests are
observations rather than a complete attempt log. What this reports is spend over the
requests that were saved, failures included, and it says so.

**A ratio over a subset is not a ratio over the cohort.** Where some saved requests lack a
cost or a TP count, numerator and denominator are both taken from exactly the requests that
have both, and the result is labelled a matched subset with its coverage beside it. A
complete-cohort ratio is reported only when every saved request in the cell qualifies.

Run it against a built dataset:

    python business_letters_cost.py --dataset ../  --format text
    python business_letters_cost.py --dataset ../  --format json --by-model

Reads Parquet, so it needs `pyarrow` and nothing else. Costs are the `derived_*` column
family by default -- recomputed from recorded tokens and the price in force on the run's
date -- because it covers more requests than the stored figures and is uniform across the
corpus. `--cost stored` uses what each run actually recorded instead.
"""
import argparse
import collections
import json
import os
import sys
from pathlib import Path

import pyarrow.parquet as pq

BENCHMARK = "business_letters"

CATEGORIES = ("send_date", "sender_persons", "receiver_persons")
"""The only categories this benchmark scores. Hard-coded in its scorer, not configurable."""

TP_METRICS = frozenset("%s.request.%s_tp" % (BENCHMARK, c) for c in CATEGORIES)

COST_COLUMNS = {
    "derived": "derived_total_cost_usd",
    "stored": "stored_estimated_cost_usd",
}

DEFAULT_MIN_COVERAGE = 0.5
"""Below this share of saved requests carrying both a cost and TP counts, no ratio is
reported. This is an analyst's threshold, not a property of the data: the coverage figure
is always shown so a different choice can be made."""


TABLES = ("runs.parquet", "requests.parquet", "scores_long.parquet")


def resolve_dataset_dir(dataset_dir):
    """The directory holding the parquet files, or a message saying where to look.

    Worth the lines: the natural mistake is to run this from inside `examples/` and pass
    the dataset's own name, and pyarrow answers that with a dozen frames of internals
    ending in a bare FileNotFoundError. Whoever reads this has the data but not the
    repository, so the error has to carry the fix.
    """
    path = Path(dataset_dir)
    missing = [name for name in TABLES if not (path / name).is_file()]
    if not missing:
        return path

    hints = []
    for candidate in (Path.cwd(), Path.cwd().parent, Path(__file__).resolve().parent.parent):
        if all((candidate / name).is_file() for name in TABLES):
            hints.append(candidate)
    hint = ""
    if hints:
        try:
            shown = Path(os.path.relpath(hints[0], Path.cwd()))
        except ValueError:
            shown = hints[0]
        hint = "\n\nTry:  --dataset %s" % (shown if str(shown) != "." else ".")

    raise SystemExit(
        "No dataset at %s: %s not found there.\n"
        "--dataset must point at the directory holding the parquet files, which is the "
        "dataset root, not the examples/ folder beside it.%s"
        % (path.resolve(), ", ".join(missing), hint))


def load(dataset_dir, cost_column):
    """runs, requests, per-request TP totals, and how many requests were partly scored."""
    dataset_dir = resolve_dataset_dir(dataset_dir)
    runs = [r for r in pq.read_table(dataset_dir / "runs.parquet").to_pylist()
            if r["benchmark"] == BENCHMARK]
    run_ids = set(r["run_id"] for r in runs)

    requests = [r for r in pq.read_table(dataset_dir / "requests.parquet").to_pylist()
                if r["run_id"] in run_ids]

    # All three categories, or none. A request with only `send_date_tp` has been partly
    # scored, and summing what happens to be present would put a partial numerator over a
    # whole request's cost -- overstating how much that money bought. The dataset applies
    # the same rule in `requests.is_scored`.
    seen = collections.defaultdict(dict)
    for row in pq.read_table(dataset_dir / "scores_long.parquet").to_pylist():
        if row["run_id"] in run_ids and row["metric_id"] in TP_METRICS:
            seen[(row["run_id"], row["object_id"])][row["metric_id"]] = row["value"]

    tp_totals = dict((key, sum(values.values()))
                     for key, values in seen.items() if len(values) == len(TP_METRICS))
    partial = len(seen) - len(tp_totals)

    return runs, requests, tp_totals, partial


def analyse(runs, requests, tp_totals, cost_column, by_model=False,
            include_hidden=False, min_coverage=DEFAULT_MIN_COVERAGE):
    runs_by_id = dict((r["run_id"], r) for r in runs)

    visible = {}
    excluded_hidden = 0
    for run_id, run in runs_by_id.items():
        if not include_hidden and run["hidden"] is not False:
            # `is not False` and not `is True`: an unresolved visibility is not a licence
            # to include the run silently.
            excluded_hidden += 1
            continue
        visible[run_id] = run

    cells = collections.defaultdict(lambda: {
        "requests": [], "response_models": collections.Counter()})

    for request in requests:
        run = visible.get(request["run_id"])
        if run is None:
            continue
        key = (run["configured_provider"], run["configured_model"] if by_model else None,
               run["date"])
        cell = cells[key]
        cell["requests"].append(request)
        if request["response_model"]:
            cell["response_models"][request["response_model"]] += 1

    results = []
    for (provider, model, date), cell in cells.items():
        saved = cell["requests"]
        costs = [r[cost_column] for r in saved if r[cost_column] is not None]

        eligible = [r for r in saved
                    if r[cost_column] is not None
                    and (r["run_id"], r["object_id"]) in tp_totals]
        eligible_tp = sum(tp_totals[(r["run_id"], r["object_id"])] for r in eligible)
        eligible_spend = sum(r[cost_column] for r in eligible)

        n_scored = sum(1 for r in saved if (r["run_id"], r["object_id"]) in tp_totals)
        coverage = len(eligible) / len(saved) if saved else 0.0

        ratio, basis, reason, code, flag = None, None, None, None, None
        if not eligible:
            code = "no_eligible"
            reason = "no saved request has both a cost and TP counts"
        elif eligible_tp == 0:
            code = "no_true_positives"
            reason = "no true positives among the eligible requests"
        elif coverage < min_coverage:
            code = "low_coverage"
            reason = ("eligible coverage %.1f%% is below the %.0f%% threshold"
                      % (100 * coverage, 100 * min_coverage))
        else:
            ratio = eligible_spend / eligible_tp
            basis = "complete_cohort" if len(eligible) == len(saved) else "matched_subset"
            if eligible_spend == 0:
                # A zero price in the table is a data defect, not a free model: at least
                # one entry resolves to $0.00/$0.00 from a bad scrape. Reporting
                # "$0.000000 per extraction" without saying so would be a false finding.
                flag = "zero_priced"

        results.append({
            "provider": provider,
            "model": model,
            "date": date,
            "n_saved_requests": len(saved),
            "observed_spend_usd": sum(costs) if costs else None,
            "n_requests_with_cost": len(costs),
            "n_requests_scored": n_scored,
            "scored_coverage": n_scored / len(saved) if saved else None,
            "cost_coverage": len(costs) / len(saved) if saved else None,
            "eligible_requests": len(eligible),
            "eligible_coverage": coverage,
            "eligible_spend_usd": eligible_spend if eligible else None,
            "true_positives": int(eligible_tp),
            "usd_per_correct_extraction": ratio,
            "ratio_basis": basis,
            "ratio_unavailable_code": code,
            "ratio_unavailable_because": reason,
            "flag": flag,
            "response_models": sorted(cell["response_models"]),
        })

    results.sort(key=lambda r: (r["provider"] or "", r["model"] or "", r["date"]))
    return results, {"runs_excluded_as_hidden": excluded_hidden,
                     "cost_column": cost_column,
                     "by_model": by_model,
                     "min_coverage": min_coverage}


CAVEATS = """
How to read this
  * One correct extraction is one true positive in send_date, sender_persons or
    receiver_persons. It is not a fully correct letter, and it is not an F1 score.
  * Observed spend covers the requests that were saved, failures included. The runner
    saves no request when an answer is None and a same-day re-run overwrites the earlier
    one, so this is not a complete record of what was spent.
  * A matched-subset ratio uses exactly the requests that have both a cost and TP counts
    for its numerator and its denominator. It is not the cell's total spend per extraction.
  * Unscored requests are excluded, never counted as zero correct extractions. A
    request scored in only some of the three categories counts as unscored: a partial
    numerator over a whole request's cost would overstate what the money bought.
  * Moving along the date axis changes more than the date: which models were run, the
    prompts, the documents, the scorer and the price table all changed over this span.
    These records show what happened; they do not isolate a cause.
"""


def render_text(results, meta, handle=sys.stdout):
    """A fixed-width table. The label column is sized to the data rather than clipped:
    truncating `qwen3.5-plus` and `qwen3.5-max` to the same string would silently merge
    two models into one apparent row."""
    labels = []
    for row in results:
        label = row["provider"] or "<none>"
        if row["model"]:
            label = "%s / %s" % (label, row["model"])
        labels.append(label)
    width = max([len(l) for l in labels] + [8])

    cols = [("provider" + (" / model" if meta["by_model"] else ""), width, "<"),
            ("date", 10, "<"), ("saved", 6, ">"), ("scored", 7, ">"),
            ("cost", 6, ">"), ("TP", 6, ">"), ("spend $", 10, ">"),
            ("$/extraction", 13, ">"), ("basis", 17, "<")]
    header = "  ".join(("%-*s" if a == "<" else "%*s") % (w, h) for h, w, a in cols)
    print(header, file=handle)
    print("-" * len(header), file=handle)

    for label, row in zip(labels, results):
        if row["usd_per_correct_extraction"] is None:
            ratio = "-"
        else:
            ratio = "%.6f" % row["usd_per_correct_extraction"]
        basis = row["ratio_basis"] or row["ratio_unavailable_code"] or ""
        if row["flag"]:
            basis = "%s !%s" % (basis, row["flag"])
        values = (label, row["date"] or "", str(row["n_saved_requests"]),
                  "%.0f%%" % (100 * row["scored_coverage"]),
                  "%.0f%%" % (100 * row["cost_coverage"]),
                  str(row["true_positives"]),
                  "%.4f" % row["observed_spend_usd"]
                  if row["observed_spend_usd"] is not None else "-",
                  ratio, basis)
        print("  ".join(("%-*s" if a == "<" else "%*s") % (w, v)
                        for v, (_h, w, a) in zip(values, cols)), file=handle)

    counts = collections.Counter(r["ratio_basis"] or r["ratio_unavailable_code"]
                                 for r in results)
    flagged = [r for r in results if r["flag"]]
    print("", file=handle)
    print("%d cells: %s" % (len(results), ", ".join(
        "%d %s" % (n, k) for k, n in sorted(counts.items()))), file=handle)
    print("cost column: %s | hidden runs excluded: %d | coverage threshold: %.0f%%"
          % (meta["cost_column"], meta["runs_excluded_as_hidden"],
             100 * meta["min_coverage"]), file=handle)
    if meta.get("requests_with_incomplete_tp_categories"):
        print("%d request(s) carried some but not all three TP categories and are counted "
              "as unscored" % meta["requests_with_incomplete_tp_categories"], file=handle)
    if flagged:
        print("", file=handle)
        print("!zero_priced (%d cells): every eligible request cost $0.00, which means the"
              % len(flagged), file=handle)
        print("  pricing table has no real price for this model rather than that the model"
              , file=handle)
        print("  is free. Do not read these as the cheapest option.", file=handle)
    print(CAVEATS, file=handle)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--dataset", default=".", help="directory holding the parquet files")
    parser.add_argument("--cost", choices=sorted(COST_COLUMNS), default="derived")
    parser.add_argument("--by-model", action="store_true",
                        help="group by configured model as well as provider")
    parser.add_argument("--include-hidden", action="store_true",
                        help="include legacy tests and benchmarks marked display:false")
    parser.add_argument("--min-coverage", type=float, default=DEFAULT_MIN_COVERAGE)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    cost_column = COST_COLUMNS[args.cost]
    runs, requests, tp_totals, partial = load(args.dataset, cost_column)
    results, meta = analyse(runs, requests, tp_totals, cost_column,
                            by_model=args.by_model,
                            include_hidden=args.include_hidden,
                            min_coverage=args.min_coverage)

    meta["requests_with_incomplete_tp_categories"] = partial

    if args.format == "json":
        json.dump({"meta": meta, "cells": results, "caveats": CAVEATS.strip().split("\n")},
                  sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    else:
        render_text(results, meta)
    return 0


if __name__ == "__main__":
    sys.exit(main())
