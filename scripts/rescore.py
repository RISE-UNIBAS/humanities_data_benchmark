"""Re-run a benchmark's own scorer over already-stored results.

Used to prove a change to a scorer leaves its numbers untouched: no model call is
needed, since the response and the ground truth are both on disk. The offline setup
lives in `scripts/offline_scoring.py`.

A stored score that does not reproduce is usually not a scorer bug. Ground truths are
revised -- `personnel_cards` had a correction landed one day after a run that used the
previous version -- so a divergence normally means the truth moved, not the code. Use
`--dump` twice, before and after a change, to compare the change against itself instead.

Usage:
    python scripts/rescore.py --check                  # stored vs re-scored, all runs
    python scripts/rescore.py --check --benchmark magazine_pages
    python scripts/rescore.py --run 2026-08-18/T1597   # one run, verbose
    python scripts/rescore.py --check --dump after.json
"""
import argparse
import json
import logging
import sys
from collections import Counter
from pathlib import Path

# Run directly (`python scripts/rescore.py`) and sys.path[0] is scripts/, not the project
# root, so the `scripts` package itself would not import. `python -m scripts.rescore`
# does not need this.
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from scripts.offline_scoring import (RESULTS_PATH, benchmark_of_test, iter_run_inputs,
                                     iter_runs, load_scorer, numeric_metrics, read_tests,
                                     rules_of_test)


def rescore_run(run_dir, benchmark, scorer, test_id=None):
    """Re-scores every stored response of a run. Yields (object_id, stored, fresh)."""
    for object_id, record, answer, truth in iter_run_inputs(run_dir, test_id):
        try:
            fresh = scorer.score_request_answer(object_id, answer, truth)
        except Exception as error:              # a scorer that cannot run is the finding
            fresh = {"__error": "%s: %s" % (type(error).__name__, error)}
        yield object_id, record.get("score"), fresh


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true",
                        help="compare stored scores against freshly computed ones")
    parser.add_argument("--benchmark", help="limit to one benchmark")
    parser.add_argument("--run", help="a single run as <date>/<test_id>")
    parser.add_argument("--limit", type=int, default=0, help="use only the newest N runs")
    parser.add_argument("--dump", help="write the re-scored numbers to this file, for "
                                       "before/after comparison of a scorer change")
    args = parser.parse_args()

    logging.disable(logging.CRITICAL)  # the scorers log per field at INFO

    tests = read_tests()
    if args.run:
        date, test_id = args.run.split("/")
        targets = [(RESULTS_PATH / date / test_id, test_id,
                    benchmark_of_test(tests).get(test_id))]
    else:
        targets = [t for t in iter_runs(args.benchmark)]
        if args.limit:
            # The newest runs, not the oldest: the earliest runs predate per-request
            # scoring, so sampling from the front reports "no stored score" and tests
            # nothing.
            targets = targets[-args.limit:]

    scorers, tally, mismatches, failures = {}, Counter(), [], Counter()
    dump = {}

    for run_dir, test_id, benchmark in targets:
        if not benchmark or not Path(run_dir).is_dir():
            continue
        if benchmark not in scorers:
            try:
                scorers[benchmark] = load_scorer(benchmark)
            except Exception as error:
                failures[benchmark + ": " + str(error)] += 1
                continue
        scorer = scorers[benchmark]
        # Per run, not per benchmark: personnel_cards selects which fields it scores
        # from the run's rules, so a cached scorer must be re-pointed at this run's.
        scorer.rules = rules_of_test(test_id, tests)

        for object_id, stored, fresh in rescore_run(run_dir, benchmark, scorer, test_id):
            if isinstance(fresh, dict) and "__error" in fresh:
                failures[benchmark + " " + fresh["__error"][:70]] += 1
                tally["error"] += 1
                continue
            if stored is None:
                tally["no stored score"] += 1
                continue
            key = "%s/%s/%s" % (Path(run_dir).parent.name, test_id, object_id)
            dump[key] = numeric_metrics(fresh)
            if numeric_metrics(stored) == numeric_metrics(fresh):
                tally["identical"] += 1
            else:
                tally["differs"] += 1
                if len(mismatches) < 12:
                    mismatches.append((benchmark, Path(run_dir).parent.name, test_id,
                                       object_id, numeric_metrics(stored),
                                       numeric_metrics(fresh)))
            if args.run:
                print("  %-34s stored=%s" % (object_id, json.dumps(numeric_metrics(stored))))
                print("  %-34s fresh =%s" % ("", json.dumps(numeric_metrics(fresh))))

    print("\n--- re-scored %d run(s) ---" % len(targets))
    if args.dump:
        with open(args.dump, "w", encoding="utf-8") as handle:
            json.dump(dump, handle, indent=1, sort_keys=True)
        print("wrote %d re-scored results to %s" % (len(dump), args.dump))
    for key in ("identical", "differs", "error", "no stored score"):
        if tally[key]:
            print("  %-16s %d" % (key, tally[key]))
    for row in mismatches:
        print("  DIFFERS %s %s/%s %s\n    stored %s\n    fresh  %s" % row)
    if failures:
        print("\n  scorer failures:")
        for key, count in failures.most_common(10):
            print("    %5dx %s" % (count, key))

    return 1 if tally["differs"] else 0


if __name__ == "__main__":
    sys.exit(main())
