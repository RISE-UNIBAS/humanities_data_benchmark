#!/usr/bin/env python3
"""Complete the cost record on stored results. Makes no API calls.

Fills two gaps in `results/*/*/request_*.json`: `reasoning_tokens` and
`reasoning_cost_usd` for reasoning a provider billed outside `output_tokens`, and
`input_cost_usd` / `output_cost_usd` where a run recorded no cost. `estimated_cost_usd`
is then input + output + reasoning throughout, and `--summaries` rolls the totals into
each run's `scoring.json`.

Two rules govern what may be written:

- A price counts only if its `pricing.json` bucket falls within `--max-price-age` days
  *before* the run. Otherwise the cost is unknown rather than zero: the token count is
  recorded and the cost is left null.
- A cost the provider reported is never replaced by a derived one. An
  `estimated_cost_usd` with no component fields is a provider-billed total.

    python scripts/backfill_costs.py                     # dry run, whole corpus
    python scripts/backfill_costs.py --provider genai    # narrow it
    python scripts/backfill_costs.py --apply             # write
    python scripts/backfill_costs.py --summaries --apply # and roll up per run
    python scripts/backfill_costs.py --verify            # check what landed

Dry run is the default. Before any write the unmodified document is re-serialised and
compared with the bytes on disk; a file that cannot be reproduced exactly is skipped, so
stored files keep their own JSON encoding and line endings.
"""
import argparse
import json
import logging
import os
import sys
from typing import NamedTuple, Optional

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.ndr_export.pricing_resolver import resolve_pricing  # noqa: E402
from scripts.reasoning_tokens import (  # noqa: E402
    gap_of,
    reported_reasoning,
    uncounted_reasoning,
)

DEFAULT_MAX_AGE_DAYS = 30
"""The window `update_pricing.py` maintains."""

logging.getLogger("scripts.ndr_export.pricing_resolver").setLevel(logging.ERROR)

TOKENS_KEY = "reasoning_tokens"
COST_KEY = "reasoning_cost_usd"
EST_KEY = "estimated_cost_usd"


_price_cache = {}


def price_for(provider, model, run_date, max_age_days=None):
    """The price for this run, or None when nothing is in range. None means any age."""
    key = (provider, model, run_date, max_age_days)
    if key not in _price_cache:
        _price_cache[key] = resolve_pricing(provider, model, run_date,
                                            max_age_days=max_age_days)
    return _price_cache[key]


def clear_price_cache():
    """For tests that swap the pricing table underneath."""
    _price_cache.clear()


def detect_style(raw_bytes, document):
    """How this file was written, proved by reproducing it, or None if it cannot be.

    Returns (ensure_ascii, newline, trailing) for a byte-exact round trip.
    """
    newline = "\r\n" if b"\r\n" in raw_bytes else "\n"
    trailing = newline if raw_bytes.endswith(newline.encode("utf-8")) else ""
    # Pure-ASCII bytes almost always mean ensure_ascii=True; try that first, then the other.
    guess = not any(byte >= 0x80 for byte in raw_bytes)
    for ensure_ascii in (guess, not guess):
        text = json.dumps(document, indent=4, ensure_ascii=ensure_ascii)
        if newline != "\n":
            text = text.replace("\n", newline)
        if (text + trailing).encode("utf-8") == raw_bytes:
            return ensure_ascii, newline, trailing
    return None


def render(document, style):
    ensure_ascii, newline, trailing = style
    text = json.dumps(document, indent=4, ensure_ascii=ensure_ascii)
    if newline != "\n":
        text = text.replace("\n", newline)
    return (text + trailing).encode("utf-8")


def iter_request_files(results_dir, dates=None, test_ids=None):
    """Yield (date, test_id, path) for every stored request, oldest date first."""
    for date in sorted(os.listdir(results_dir)):
        date_dir = os.path.join(results_dir, date)
        if not os.path.isdir(date_dir) or len(date) != 10:
            continue
        if dates and date not in dates:
            continue
        for test_id in sorted(os.listdir(date_dir)):
            test_dir = os.path.join(date_dir, test_id)
            if not os.path.isdir(test_dir):
                continue
            if test_ids and test_id not in test_ids:
                continue
            for name in sorted(os.listdir(test_dir)):
                if name.startswith("request_") and name.endswith(".json"):
                    yield date, test_id, os.path.join(test_dir, name)


class Stats:
    def __init__(self):
        self.seen = 0
        self.gapped = 0
        self.gap_tokens = 0
        self.from_provider = 0
        self.from_arithmetic = 0
        self.unknown = 0
        self.negative = 0
        self.unpriced = 0
        self.cost = 0.0
        self.written = 0
        self.already = 0
        self.unreproducible = []
        self.cost_filled = 0
        self.cost_filled_usd = 0.0
        self.cost_unpriced = 0
        self.stale_reasoning = 0


class Desired(NamedTuple):
    """What one request's cost fields should be. Decided once, used to write and to sum."""

    input_cost: Optional[float]
    output_cost: Optional[float]
    reasoning_tokens: Optional[int]
    reasoning_cost: Optional[float]
    total: float
    """This request's contribution to its run's total, whatever the components are."""

    total_known: bool
    """False when the contribution is unknown rather than zero, so a run containing it
    cannot be totalled."""

    components_known: bool
    filled: bool
    unpriced_fill: bool
    """Tokens to cost, no cost recorded, and no price inside the window."""

    gap: Optional[int]
    reported: Optional[int]
    changes: dict


def desired(document, date, max_age_days, all_files=False):
    """Decide this request's cost fields. Pure: no I/O, no stats, no writes.

    The writer and the rollup both go through here, so a dry run cannot preview something
    an --apply would not do.
    """
    usage = document.get("usage")
    if not isinstance(usage, dict):
        return None
    provider = (document.get("provider") or "").lower()
    model = document.get("model")
    # `or 0`, not a default: some files carry these keys with a null value.
    input_tokens = usage.get("input_tokens") or 0
    output_tokens = usage.get("output_tokens") or 0

    gap = gap_of(usage)
    reported = reported_reasoning(document.get("raw_response"))
    tokens = uncounted_reasoning(usage, document.get("raw_response")) if (
        gap is not None and gap >= 0) else None

    priced = price_for(provider, model, date, max_age_days)

    # Out of window: unknown, not zero. Keep the count, withhold the money.
    reasoning = round(tokens / 1e6 * priced.output_price, 10) if (tokens and priced) else None

    stored_est = usage.get(EST_KEY)
    input_cost = usage.get("input_cost_usd")
    output_cost = usage.get("output_cost_usd")

    # Only where no cost is recorded at all: an estimated_cost_usd without components is
    # the provider's own billed figure, which list prices must not overwrite.
    filled = unpriced_fill = False
    if ((input_cost is None or output_cost is None) and stored_est is None
            and (input_tokens or output_tokens)):
        if priced:
            input_cost = input_tokens / 1e6 * priced.input_price
            output_cost = output_tokens / 1e6 * priced.output_price
            filled = True
        else:
            unpriced_fill = True

    components_known = input_cost is not None and output_cost is not None
    estimated = None
    if components_known and (filled or tokens or stored_est is None):
        estimated = input_cost + output_cost + (reasoning or 0)

    if estimated is not None:
        total = estimated
    elif stored_est is not None:
        total = stored_est
    elif components_known:
        total = input_cost + output_cost + (reasoning or 0)
    else:
        # Tokens but no cost and no price in the window: the contribution is unknown, and
        # 0.0 is only a placeholder. A request with no tokens at all really did cost 0.
        total = 0.0

    # Order sets where new keys land; existing keys keep their position.
    changes = {}
    if filled:
        changes["input_cost_usd"] = input_cost
        changes["output_cost_usd"] = output_cost
    if estimated is not None:
        changes[EST_KEY] = estimated
    if tokens or (all_files and tokens is not None):
        changes[TOKENS_KEY] = tokens
        changes[COST_KEY] = reasoning

    return Desired(input_cost, output_cost, tokens, reasoning, total,
                   not unpriced_fill, components_known, filled, unpriced_fill,
                   gap, reported, changes)


def load(path):
    """(raw bytes, document) or None when the file is not usable JSON."""
    with open(path, "rb") as handle:
        raw = handle.read()
    try:
        document = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return None
    return (raw, document) if isinstance(document, dict) else None


def in_scope(document, args):
    return not args.provider or (document.get("provider") or "").lower() in args.provider


def find_mismatches(args):
    """Requests whose provider-reported reasoning contradicts the arithmetic gap.

    Read-only, and run to completion before any write.
    """
    found = []
    for date, _test_id, path in iter_request_files(args.results, set(args.date or []),
                                                   set(args.test_id or [])):
        loaded = load(path)
        if loaded is None:
            continue
        _raw, document = loaded
        if not in_scope(document, args):
            continue
        usage = document.get("usage")
        if not isinstance(usage, dict):
            continue
        gap = gap_of(usage)
        reported = reported_reasoning(document.get("raw_response"))
        # A provider reporting reasoning inside output_tokens gives reported > 0 against
        # gap == 0, which is correct, not a disagreement.
        if gap is not None and gap > 0 and reported is not None and reported != gap:
            found.append((path, reported, gap))
    return found


def backfill(args, stats):
    dates, test_ids = set(args.date or []), set(args.test_id or [])
    for date, _test_id, path in iter_request_files(args.results, dates, test_ids):
        loaded = load(path)
        if loaded is None:
            continue
        raw, document = loaded
        if not in_scope(document, args):
            continue
        stats.seen += 1
        d = desired(document, date, args.max_price_age, args.all_files)
        if d is None:
            continue

        if d.gap is None:
            stats.unknown += 1
        elif d.gap < 0:
            stats.negative += 1
        if d.reasoning_tokens:
            stats.gapped += 1
            stats.gap_tokens += d.reasoning_tokens
            if d.reported is not None:
                stats.from_provider += 1
            else:
                stats.from_arithmetic += 1
            if d.reasoning_cost is None:
                stats.unpriced += d.reasoning_tokens
                stats.stale_reasoning += 1
            else:
                stats.cost += d.reasoning_cost
        if d.filled:
            stats.cost_filled += 1
            stats.cost_filled_usd += (d.input_cost or 0) + (d.output_cost or 0)
        elif d.unpriced_fill:
            stats.cost_unpriced += 1

        usage = document["usage"]
        if not d.changes or all(usage.get(k) == v for k, v in d.changes.items()):
            if d.changes:
                stats.already += 1
            continue

        style = detect_style(raw, document)
        if style is None:
            stats.unreproducible.append(path)
            continue
        usage.update(d.changes)
        stats.written += 1
        if args.apply:
            with open(path, "wb") as handle:
                handle.write(render(document, style))


_MISSING = object()


def _differs(stored, want):
    """True when the stored value needs replacing. A stored null equals a wanted null."""
    if stored is _MISSING:
        return True
    if stored is None or want is None:
        return stored is not want
    if isinstance(stored, (int, float)) and isinstance(want, (int, float)):
        return abs(stored - want) > max(1e-9, 1e-9 * abs(want))
    return stored != want


def roll_up_summaries(args, apply_changes):
    """Merge per-run totals into scoring.json cost_summary. Never replaces the dict.

    Only keys whose value moved are written, so a run that merely gained reasoning keeps
    its token totals and pricing provenance.
    """
    changed, runs, unreproducible, retotalled, skipped = 0, 0, [], 0, 0
    dates, test_ids = set(args.date or []), set(args.test_id or [])

    for date in sorted(os.listdir(args.results)):
        date_dir = os.path.join(args.results, date)
        if not os.path.isdir(date_dir) or len(date) != 10:
            continue
        if dates and date not in dates:
            continue
        for test_id in sorted(os.listdir(date_dir)):
            test_dir = os.path.join(date_dir, test_id)
            scoring_path = os.path.join(test_dir, "scoring.json")
            if not os.path.isfile(scoring_path):
                continue
            if test_ids and test_id not in test_ids:
                continue

            # A total is only meaningful over every request in the run. Anything that
            # cannot be read, is filtered out, or would not be written leaves the
            # summary alone -- a partial sum silently reports the rest as free.
            requests, excluded = [], 0
            for name in sorted(os.listdir(test_dir)):
                if not (name.startswith("request_") and name.endswith(".json")):
                    continue
                loaded = load(os.path.join(test_dir, name))
                if loaded is None or not in_scope(loaded[1], args):
                    excluded += 1
                    continue
                requests.append(loaded)
            if excluded:
                skipped += 1
                continue
            if not requests:
                continue
            runs += 1

            in_tok = out_tok = r_tok = 0
            in_cost = out_cost = r_cost = total = 0.0
            r_priced = unknown_components = 0
            unusable = total_unknown = False
            for raw_request, request in requests:
                d = desired(request, date, args.max_price_age, args.all_files)
                # No usage block at all: the request recorded no tokens and no cost, so it
                # contributes nothing. That is known, unlike a file that will not parse.
                if d is None:
                    continue
                # A request the writer would skip must not be counted as if it had been
                # corrected.
                if d.changes and detect_style(raw_request, request) is None:
                    unusable = True
                    break
                usage = request.get("usage") or {}
                in_tok += usage.get("input_tokens") or 0
                out_tok += usage.get("output_tokens") or 0
                total += d.total
                if not d.total_known:
                    total_unknown = True
                if d.components_known:
                    in_cost += d.input_cost or 0.0
                    out_cost += d.output_cost or 0.0
                else:
                    unknown_components += 1
                r_tok += d.reasoning_tokens or 0
                if d.reasoning_cost is not None:
                    r_cost += d.reasoning_cost
                    r_priced += 1

            if unusable:
                skipped += 1
                continue

            loaded = load(scoring_path)
            if loaded is None:
                continue
            raw, document = loaded
            summary = document.get("cost_summary")
            if not isinstance(summary, dict):
                continue

            want = {}
            if r_tok:
                want["total_reasoning_tokens"] = r_tok
                # None, not 0.0: 0.0 would claim the reasoning was free.
                want[COST_KEY] = round(r_cost, 10) if r_priced else None
            # Only when every request has components; a partial sum understates.
            if not unknown_components:
                components = (("total_input_tokens", in_tok),
                              ("total_output_tokens", out_tok),
                              ("total_tokens", in_tok + out_tok),
                              ("input_cost_usd", round(in_cost, 10)),
                              ("output_cost_usd", round(out_cost, 10)))
                moved = [(k, v) for k, v in components
                         if _differs(summary.get(k, _MISSING), v)]
                if moved:
                    retotalled += 1
                    want.update(moved)
            # Checked even when nothing else moved, since a stale total is wrong on its
            # own -- but only when every request's contribution is known. One unpriceable
            # request makes the sum an understatement, not a correction.
            if not total_unknown:
                want["total_cost_usd"] = round(total, 10)

            if not want or all(not _differs(summary.get(k, _MISSING), v)
                               for k, v in want.items()):
                continue

            # Style proved against the bytes on disk, before anything is mutated.
            style = detect_style(raw, document)
            if style is None:
                unreproducible.append(scoring_path)
                continue
            summary.update(want)
            changed += 1
            if apply_changes:
                with open(scoring_path, "wb") as handle:
                    handle.write(render(document, style))

    return runs, changed, unreproducible, retotalled, skipped


def verify(args):
    """Re-read what landed and check the invariant, honouring the same filters."""
    carried = bad = 0
    for date, _test_id, path in iter_request_files(args.results, set(args.date or []),
                                                   set(args.test_id or [])):
        loaded = load(path)
        if loaded is None or not in_scope(loaded[1], args):
            continue
        usage = loaded[1].get("usage") or {}
        if TOKENS_KEY not in usage:
            continue
        carried += 1
        total = usage.get("total_tokens") or 0
        parts = ((usage.get("input_tokens") or 0) + (usage.get("output_tokens") or 0)
                 + (usage.get(TOKENS_KEY) or 0))
        if total != parts:
            bad += 1
            if bad <= 10:
                print("  INVARIANT %s: %d != %d" % (path, parts, total))
    print("%s files carry %s; invariant input+output+reasoning == total holds on %s"
          % (f"{carried:,}", TOKENS_KEY, f"{carried - bad:,}"))
    if bad:
        print("FAILED on %s files" % f"{bad:,}")
    return 1 if bad else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--results", default=os.path.join(PROJECT_ROOT, "results"))
    parser.add_argument("--provider", action="append", help="restrict to these (repeatable)")
    parser.add_argument("--date", action="append", help="restrict to these (repeatable)")
    parser.add_argument("--test-id", action="append", help="restrict to these (repeatable)")
    parser.add_argument("--apply", action="store_true", help="write; default is a dry run")
    parser.add_argument("--all-files", action="store_true",
                        help="also write reasoning_tokens=0 to files with no gap")
    parser.add_argument("--summaries", action="store_true",
                        help="roll the totals into each run's scoring.json")
    parser.add_argument("--max-price-age", type=int, default=DEFAULT_MAX_AGE_DAYS,
                        help="how many days before the run a pricing bucket may be and "
                             "still be written as that run's rate (default %d); 0 means "
                             "the run's own bucket only" % DEFAULT_MAX_AGE_DAYS)
    parser.add_argument("--verify", action="store_true", help="check stored files, write nothing")
    return main_with_args(parser.parse_args())


def main_with_args(args):
    """The body of `main`, callable with an args object so it can be tested."""
    if args.verify:
        return verify(args)

    # Validation first, as its own read-only pass: a stop that fires mid-rewrite is not one.
    mismatches = find_mismatches(args)
    if mismatches:
        print("STOP: the provider's reasoning count disagrees with the arithmetic gap "
              "on %s files. Nothing was written." % f"{len(mismatches):,}")
        for path, reported, gap in mismatches[:10]:
            print("  %s reported=%d gap=%d" % (path, reported, gap))
        return 2

    stats = Stats()
    backfill(args, stats)

    print("%s requests inspected" % f"{stats.seen:,}")
    print("  %s with reasoning outside output_tokens, %s tokens"
          % (f"{stats.gapped:,}", f"{stats.gap_tokens:,}"))
    print("    %s from the provider's own field, %s from arithmetic"
          % (f"{stats.from_provider:,}", f"{stats.from_arithmetic:,}"))
    print("  reasoning cost $%.2f" % stats.cost)
    if stats.unpriced:
        print("  %s tokens unpriced (no pricing.json entry in range)"
              % f"{stats.unpriced:,}")
    if stats.unknown:
        print("  %s skipped: no total_tokens, so reasoning is unknown not zero"
              % f"{stats.unknown:,}")
    if stats.negative:
        print("  %s skipped: total < input + output" % f"{stats.negative:,}")
    if stats.cost_filled:
        print("  %s requests had no recorded input/output cost; filled at the rate in "
              "force on the run date, $%.2f"
              % (f"{stats.cost_filled:,}", stats.cost_filled_usd))
    if stats.cost_unpriced:
        print("  %s requests left uncosted: no price within %d days of the run date"
              % (f"{stats.cost_unpriced:,}", args.max_price_age))
    if stats.stale_reasoning:
        print("  %s carry reasoning_tokens with a null cost for the same reason"
              % f"{stats.stale_reasoning:,}")
    print("  %s files already correct" % f"{stats.already:,}")

    if stats.unreproducible:
        print("\n%s files could not be reproduced byte-for-byte and were SKIPPED:"
              % f"{len(stats.unreproducible):,}")
        for path in stats.unreproducible[:10]:
            print("  %s" % path)

    verb = "written" if args.apply else "would change"
    print("\n%s: %s request files" % (verb, f"{stats.written:,}"))

    if args.summaries:
        runs, changed, unreproducible, retotalled, skipped = roll_up_summaries(
            args, args.apply)
        print("%s: %s of %s scoring.json cost_summary blocks"
              % (verb, f"{changed:,}", f"{runs:,}"))
        if retotalled:
            print("  %s of those also had component totals re-summed"
                  % f"{retotalled:,}")
        if skipped:
            print("  %s runs left alone: a request could not be read, was filtered out, "
                  "or could not be written, so any total would be partial" % f"{skipped:,}")
        if unreproducible:
            print("  %s scoring.json files could not be reproduced and were SKIPPED"
                  % f"{len(unreproducible):,}")

    if not args.apply:
        print("\nDry run. Re-run with --apply to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
