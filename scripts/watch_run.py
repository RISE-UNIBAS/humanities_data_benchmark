#!/usr/bin/env python3
"""Watch a benchmark run and print one line per sign that money is being wasted.

Usage:
    python scripts/watch_run.py --runfile scripts/run_benchmarks_x_ai.py \
                               --log scripts/logs/20260916-171452.log

Silence means requests are landing cleanly. Every line printed is worth acting on, so the
output can drive a Monitor. Pin --log: concurrent runs each write their own.
"""
import argparse
import collections
import glob
import json
import os
import re
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# A finish_reason outside this tuple paid for an unusable answer. Lowercased: each API
# words it differently, and `tool_use` is a success -- the Claude client does structured
# output as a tool call.
CLEAN_FINISH = ("stop", "end_turn", "completed", "complete", "tool_use", "")

# Waste that shows up in the log rather than in a result file.
LOG_WASTE = re.compile(
    r"No parseable JSON|LLM returned None|Fatal provider error|Stopping run|"
    # An object whose processing raised: its answer, billed or not, is neither saved nor scored.
    r"Failed with exception|"
    # A scorer that raised: the answer is saved and scored as a miss, but the scorer has a bug.
    r"Scorer raised|"
    # (?-i:CRITICAL:) matches the log level, case-sensitively and with its colon: the
    # runner logs whole prompts, and a prompt saying "CRITICAL RULES" is not an incident.
    r"falling back to JSON mode|(?-i:CRITICAL:)|HTTP/1\.1 (?:5\d\d|429)", re.I)

# A provider 5xx mid-generation is retried and usually succeeds, so one is noise; a steady
# stream of them is generation billed and thrown away. Report those by volume, the rest at once.
NOISY = re.compile(r"HTTP/1\.1 (?:5\d\d|429)", re.I)
REPORT_AT = (1, 5, 25)
REPORT_AT_NOISY = (25, 100, 250)

# Catches a request that is paid for, finishes cleanly and still yields nothing scoreable,
# which every other check here reads as healthy.
UNSCORED_MIN = 8
"""Objects a test must have saved before its ratio means anything."""

UNSCORED_FRACTION = 0.5
"""Report a test once more than this share of its saved objects have no score."""


def test_ids(runfile):
    """Return the test ids a runfile's __main__ block passes to limit_to."""
    with open(runfile, encoding="utf-8") as fh:
        source = fh.read()
    return set(re.findall(r'"(T\d{4})"', source.rsplit("main(limit_to=", 1)[-1]))


def newest_log():
    logs = sorted(glob.glob(os.path.join(PROJECT_ROOT, "scripts", "logs", "*.log")))
    return logs[-1] if logs else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runfile", required=True,
                        help="the run_benchmarks_*.py being watched; its ids scope the watch")
    parser.add_argument("--log", help="that run's log file (default: the newest one)")
    parser.add_argument("--date", default=time.strftime("%Y-%m-%d"),
                        help="results date directory to watch")
    parser.add_argument("--max-request-cost", type=float, default=0.50,
                        help="report a single request costing more than this (USD)")
    parser.add_argument("--near-cap-tokens", type=int, default=30000,
                        help="report an answer whose output tokens crowd the max_tokens cap")
    parser.add_argument("--stall-minutes", type=float, default=12.0,
                        help="report when no new result file appears for this long")
    parser.add_argument("--cost-step", type=float, default=2.00,
                        help="report cumulative spend each time it crosses this (USD)")
    parser.add_argument("--unscored-fraction", type=float, default=UNSCORED_FRACTION,
                        help="report a test once this share of its saved objects have no score")
    parser.add_argument("--unscored-min", type=int, default=UNSCORED_MIN,
                        help="objects a test must have saved before its ratio is judged")
    parser.add_argument("--interval", type=float, default=20.0, help="seconds between polls")
    parser.add_argument("--since", choices=("start", "all"), default="start",
                        help="'start' ignores results written before the watch began; "
                             "'all' counts everything on disk for these tests")
    args = parser.parse_args()

    tests = test_ids(args.runfile)
    results = os.path.join(PROJECT_ROOT, "results", args.date)
    log = args.log or newest_log()
    log_position = os.path.getsize(log) if log and os.path.exists(log) else 0
    print("watching %d tests from %s" % (len(tests), os.path.basename(args.runfile)), flush=True)

    seen, spend, step, last_new = set(), 0.0, 0.0, time.time()
    log_hits = {}
    # per test id: [saved, scored, objects at the last report]
    tally = collections.defaultdict(lambda: [0, 0, 0])
    if args.since == "start":
        # Adopt what is on disk without reporting it; replaying history buries the live signal.
        for path in glob.glob(os.path.join(results, "*", "request_*.json")):
            test = os.path.basename(os.path.dirname(path))
            if test not in tests:
                continue
            seen.add(path)
            # Seed the tally even so: a counter reset on every re-arm never reaches
            # --unscored-min on a test whose objects straddle one.
            counts = tally[test]
            counts[0] += 1
            try:
                with open(path, encoding="utf-8") as fh:
                    if (json.load(fh) or {}).get("score"):
                        counts[1] += 1
            except (OSError, ValueError):
                counts[1] += 1  # unreadable: assume fine rather than cry wolf
        print("ignoring %d result files written before this watch" % len(seen), flush=True)
        # Report a test already past the threshold at arm time, once, then set the baseline.
        for test, counts in sorted(tally.items()):
            unscored = counts[0] - counts[1]
            if counts[0] >= args.unscored_min and unscored > counts[0] * args.unscored_fraction:
                print("WASTE %s scored %d of %d saved -- %d paid objects with no score "
                      "(already true when this watch started)"
                      % (test, counts[1], counts[0], unscored), flush=True)
            counts[2] = counts[0]

    while True:
        for path in glob.glob(os.path.join(results, "*", "request_*.json")):
            if path in seen or os.path.basename(os.path.dirname(path)) not in tests:
                continue
            try:
                with open(path, encoding="utf-8") as fh:
                    data = json.load(fh)
            except (OSError, ValueError):
                continue  # still being written; not yet seen, so the next pass reads it again
            # Only a file that parsed counts as seen and as progress: one left half-written
            # would otherwise escape every check below and hide a stall.
            seen.add(path)
            last_new = time.time()

            usage = data.get("usage") or {}
            cost = usage.get("estimated_cost_usd") or 0.0
            output_tokens = usage.get("output_tokens") or 0
            finish = data.get("finish_reason")
            spend += cost
            name = "%s/%s" % (os.path.basename(os.path.dirname(path)), os.path.basename(path))

            if finish is not None and str(finish).lower() not in CLEAN_FINISH:
                print("WASTE finish_reason=%s %s out=%s $%.3f"
                      % (finish, name, output_tokens, cost), flush=True)
            elif output_tokens >= args.near_cap_tokens:
                print("WASTE near output cap %s out=%s $%.3f"
                      % (name, output_tokens, cost), flush=True)
            if cost > args.max_request_cost:
                print("WASTE expensive request %s $%.2f out=%s"
                      % (name, cost, output_tokens), flush=True)

            test = os.path.basename(os.path.dirname(path))
            counts = tally[test]
            counts[0] += 1
            if data.get("score"):
                counts[1] += 1
            unscored = counts[0] - counts[1]
            # Re-report only once the sample has doubled, not once per object.
            if (counts[0] >= args.unscored_min
                    and unscored > counts[0] * args.unscored_fraction
                    and counts[0] >= max(args.unscored_min, counts[2] * 2)):
                counts[2] = counts[0]
                print("WASTE %s scored %d of %d saved -- %d paid objects with no score"
                      % (test, counts[1], counts[0], unscored), flush=True)
            if spend >= step + args.cost_step:
                step = spend - (spend % args.cost_step)
                print("SPEND $%.2f over %d requests" % (spend, len(seen)), flush=True)

        if log and os.path.exists(log):
            try:
                with open(log, encoding="utf-8", errors="replace") as fh:
                    fh.seek(log_position)
                    for line in fh:
                        found = LOG_WASTE.search(line)
                        if not found:
                            continue
                        # One line per distinct problem, then sparingly.
                        key = found.group(0).lower()
                        log_hits[key] = log_hits.get(key, 0) + 1
                        count = log_hits[key]
                        noisy = NOISY.search(key)
                        tiers = REPORT_AT_NOISY if noisy else REPORT_AT
                        every = 250 if noisy else 50
                        if count in tiers or count % every == 0:
                            print("LOG x%d %s" % (count, line.strip()[:220]), flush=True)
                    log_position = fh.tell()
            except OSError:
                pass

        if time.time() - last_new > args.stall_minutes * 60:
            print("STALL no new result for %.0f min (%d requests, $%.2f)"
                  % ((time.time() - last_new) / 60, len(seen), spend), flush=True)
            last_new = time.time()

        time.sleep(args.interval)


if __name__ == "__main__":
    main()
