#!/usr/bin/env python3
"""Report the reasoning tokens providers bill for but do not put in `output_tokens`.

Some providers return reasoning/thinking usage inside `total_tokens` only. The cost path
multiplies `output_tokens` by the output rate, so those tokens are billed and never
recorded. This script measures the gap. It writes nothing.

    python scripts/analyse_reasoning_gap.py --by provider
    python scripts/analyse_reasoning_gap.py --by model --provider genai --markdown

The gap is priced at the model's *output* rate for the bucket in force on the run date,
via the same `pricing_resolver.resolve_pricing` the NDR export uses, so a figure here and
a figure in the export cannot drift. That pricing assumption is the weak link and is what
step 1 of `dev/REASONING_TOKEN_COST_PLAN.md` exists to validate against a provider bill --
until then, treat the money column as an estimate, not a measurement.
"""
import argparse
import json
import os
import sys
from collections import defaultdict

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from scripts.ndr_export.pricing_resolver import resolve_pricing  # noqa: E402


class Bucket:
    """Running totals for one group of requests."""

    def __init__(self):
        self.requests = 0
        self.gapped = 0
        self.gap_tokens = 0
        self.unknown = 0          # no usable total_tokens: reasoning unknown, not zero
        self.negative = 0         # total < input + output, i.e. the provider disagrees
        self.recorded_cost = 0.0
        self.gap_cost = 0.0
        self.unpriced_gap_tokens = 0
        self.stale_price_days = 0

    def add(self, cost, gap, gap_cost, age_days):
        self.requests += 1
        self.recorded_cost += cost
        if gap is None:
            self.unknown += 1
            return
        if gap < 0:
            self.negative += 1
            return
        if gap == 0:
            return
        self.gapped += 1
        self.gap_tokens += gap
        if gap_cost is None:
            self.unpriced_gap_tokens += gap
        else:
            self.gap_cost += gap_cost
            self.stale_price_days = max(self.stale_price_days, age_days or 0)


def iter_requests(results_dir):
    """Yield (date, path, payload) for every stored request, oldest date first."""
    for date in sorted(os.listdir(results_dir)):
        date_dir = os.path.join(results_dir, date)
        if not os.path.isdir(date_dir) or len(date) != 10:
            continue
        for test_id in sorted(os.listdir(date_dir)):
            test_dir = os.path.join(date_dir, test_id)
            if not os.path.isdir(test_dir):
                continue
            for name in sorted(os.listdir(test_dir)):
                if not (name.startswith("request_") and name.endswith(".json")):
                    continue
                path = os.path.join(test_dir, name)
                try:
                    with open(path, encoding="utf-8") as fh:
                        yield date, path, json.load(fh)
                except (OSError, ValueError):
                    continue


def gap_of(usage):
    """Reasoning tokens implied by the usage block, or None when unknowable.

    A missing or zero `total_tokens` means the provider told us nothing, which is not the
    same as telling us zero -- see principle 3 of the plan.
    """
    total = usage.get("total_tokens") or 0
    if not total:
        return None
    return total - (usage.get("input_tokens") or 0) - (usage.get("output_tokens") or 0)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--results", default=os.path.join(PROJECT_ROOT, "results"))
    parser.add_argument("--by", choices=("provider", "model", "month"), default="provider")
    parser.add_argument("--provider", action="append",
                        help="restrict to these providers (repeatable)")
    parser.add_argument("--markdown", action="store_true",
                        help="emit a markdown table, for pasting into the plan")
    args = parser.parse_args()

    groups = defaultdict(Bucket)
    overall = Bucket()
    price_cache = {}

    for date, _path, data in iter_requests(args.results):
        provider = data.get("provider") or "?"
        model = data.get("model") or "?"
        if args.provider and provider not in args.provider:
            continue
        usage = data.get("usage") or {}
        cost = usage.get("estimated_cost_usd") or 0.0
        gap = gap_of(usage)

        gap_cost, age_days = None, None
        if gap and gap > 0:
            key = (provider, model, date)
            if key not in price_cache:
                price_cache[key] = resolve_pricing(provider, model, date, max_age_days=None)
            priced = price_cache[key]
            if priced:
                gap_cost = gap / 1e6 * priced.output_price
                age_days = priced.age_days

        if args.by == "provider":
            label = provider
        elif args.by == "model":
            label = "%s/%s" % (provider, model)
        else:
            label = "%s %s" % (provider, date[:7])
        groups[label].add(cost, gap, gap_cost, age_days)
        overall.add(cost, gap, gap_cost, age_days)

    rows = sorted(groups.items(), key=lambda kv: -kv[1].gap_tokens)
    header = ("group", "requests", "gapped", "gap tokens", "recorded $", "gap $", "note")

    def note(b):
        bits = []
        if b.unpriced_gap_tokens:
            bits.append("%s tok unpriced" % f"{b.unpriced_gap_tokens:,}")
        if b.unknown:
            bits.append("%d unknown" % b.unknown)
        if b.negative:
            bits.append("%d negative" % b.negative)
        if b.stale_price_days > 30:
            bits.append("price %dd stale" % b.stale_price_days)
        return "; ".join(bits)

    def cells(label, b):
        pct = " (%.0f%%)" % (100.0 * b.gapped / b.requests) if b.requests else ""
        return (label, f"{b.requests:,}", f"{b.gapped:,}{pct}", f"{b.gap_tokens:,}",
                "$%.2f" % b.recorded_cost, "$%.2f" % b.gap_cost, note(b))

    table = [cells(label, b) for label, b in rows if b.requests]
    table.append(cells("**total**", overall))

    if args.markdown:
        print("| " + " | ".join(header) + " |")
        print("|" + "---|" * len(header))
        for row in table:
            print("| " + " | ".join(row) + " |")
    else:
        widths = [max(len(r[i]) for r in [header] + table) for i in range(len(header))]
        for row in [header] + table:
            print("  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)).rstrip())

    if overall.requests:
        print("\n%s requests, %s with a gap, %s gap tokens; recorded $%.2f, gap $%.2f "
              "-> $%.2f true (%.1fx)"
              % (f"{overall.requests:,}", f"{overall.gapped:,}",
                 f"{overall.gap_tokens:,}", overall.recorded_cost, overall.gap_cost,
                 overall.recorded_cost + overall.gap_cost,
                 (overall.recorded_cost + overall.gap_cost) / overall.recorded_cost
                 if overall.recorded_cost else 0))


if __name__ == "__main__":
    main()
