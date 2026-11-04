"""Re-run a benchmark's own scorer over already-stored results, and write the scores back.

No model call is needed, since the response and the ground truth are both on disk. The
offline setup lives in `scripts/offline_scoring.py`. Three modes:

`--check` (default) compares each stored request score with a fresh one. A stored score
that does not reproduce is usually not a scorer bug: ground truths are revised, so a
divergence normally means the truth moved, not the code. To prove a scorer change
score-neutral, `--dump` before and after the change and compare the two files.

`--verify` compares re-computed aggregates with each run's stored `scoring.json`. With an
unchanged scorer it must reproduce them; runs scored before a later scorer change cannot,
and the report lists them.

`--write` is used after a MAJOR version (a scorer change or a ground-truth correction)
whose new scores apply to old responses too, so stored and new runs stay comparable. A run
whose stored `scoring.json` has no numeric metric is left alone and reported. The rewritten
`scoring.json` keeps `cost_summary` and every other non-numeric key, drops numeric metrics
the scorer no longer reports, and records the rewrite in `rescored`. Only files whose
numbers change are written; a stored score that lacks the field detail of today's scorer
is not rewritten for that alone.

Per run, a request counts as scored if its file records a score, or if it was skipped as
unparseable and the benchmark now scores such answers as misses. A file without a `score`
key comes from a run that predates per-request scores: that runner scored every request and
read the answer from the response text (a ```json block or the whole text) when nothing was
parsed, so all of them count and the text is parsed the same way.

Usage:
    python scripts/rescore.py                          # stored vs re-scored, all runs
    python scripts/rescore.py --benchmark magazine_pages
    python scripts/rescore.py --run 2026-08-18/T1597   # one run, verbose
    python scripts/rescore.py --dump after.json
    python scripts/rescore.py --verify --benchmark company_lists
    python scripts/rescore.py --write --benchmark company_lists --label "company_lists 2.0.0"
"""
import argparse
import json
import logging
import math
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

# Run directly (`python scripts/rescore.py`) and sys.path[0] is scripts/, not the project
# root, so the `scripts` package itself would not import. `python -m scripts.rescore`
# does not need this.
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from scripts.offline_scoring import (RESULTS_PATH, benchmark_of_test, iter_run_inputs,
                                     iter_runs, load_scorer, numeric_metrics, read_tests,
                                     rules_of_test)


def _legacy_parse(text):
    """The answer as the runner read it before responses were parsed at request time."""
    if not isinstance(text, str):
        return None
    block = re.search(r"```json\s*([\[{].*?[]}])\s*```", text, re.DOTALL)
    try:
        return json.loads(block.group(1) if block else text)
    except ValueError:
        return None


def rescore_requests(run_dir, test_id, scorer, trap_errors=False):
    """Yields (object_id, record, fresh) per stored request; fresh is None if it does not count.

    With `trap_errors`, a scorer exception becomes `{"__error": ...}` instead of raising.
    """
    for object_id, record, answer, truth in iter_run_inputs(run_dir, test_id):
        if "score" in record:
            # A skipped unparseable answer counts once the benchmark scores it as a miss.
            scored = record["score"] is not None or (
                record.get("parsed") is None and getattr(scorer, "score_unparseable_as_miss", False))
        else:
            scored = True
        if "score" not in record and answer.parsed is None:
            answer.parsed = _legacy_parse(record.get("text"))
        fresh = None
        if scored:
            try:
                fresh = scorer.score_request_answer(object_id, answer, truth)
            except Exception as error:
                if not trap_errors:
                    raise
                fresh = {"__error": "%s: %s" % (type(error).__name__, error)}
        yield object_id, record, fresh


def rescore_run(run_dir, test_id, scorer):
    """({object id: fresh score or None}, aggregate) for one run."""
    request_scores = {object_id: fresh for object_id, _, fresh
                      in rescore_requests(run_dir, test_id, scorer)}
    return request_scores, scorer.score_benchmark([s for s in request_scores.values() if s is not None])


def _same(a, b):
    if isinstance(a, float) or isinstance(b, float):
        return isinstance(a, (int, float)) and isinstance(b, (int, float)) and math.isclose(a, b, abs_tol=1e-9)
    return a == b


def _write_json(path, content):
    # The runner's format: json.dumps(indent=4), text mode.
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(json.dumps(content, indent=4))


def check(args, tests):
    if args.run:
        date_, test_id = args.run.split("/")
        targets = [(RESULTS_PATH / date_ / test_id, test_id,
                    benchmark_of_test(tests).get(test_id))]
    else:
        targets = list(iter_runs(args.benchmark))
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

        for object_id, record, fresh in rescore_requests(run_dir, test_id, scorer, trap_errors=True):
            if isinstance(fresh, dict) and "__error" in fresh:
                failures[benchmark + " " + fresh["__error"][:70]] += 1
                tally["error"] += 1
                continue
            stored = record.get("score")
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


def verify_or_write(args, tests):
    scorer = load_scorer(args.benchmark)
    runs = mismatched = written = unfinished = 0
    skipped = []
    for run_dir, test_id, _ in iter_runs(args.benchmark):
        scoring_path = Path(run_dir) / "scoring.json"
        finished = scoring_path.is_file()
        if args.verify and not finished:
            continue
        runs += 1
        scorer.rules = rules_of_test(test_id, tests)
        request_scores, aggregate = rescore_run(run_dir, test_id, scorer)
        stored = {}
        if finished:
            with scoring_path.open(encoding="utf-8") as handle:
                stored = json.load(handle)

        if args.verify:
            diff = {k: (stored.get(k), v) for k, v in aggregate.items() if not _same(stored.get(k), v)}
            if diff:
                mismatched += 1
                if mismatched <= 10:
                    print("  %s/%s: %s" % (Path(run_dir).parent.name, test_id, diff))
            continue

        stored_metrics = [k for k, v in stored.items() if isinstance(v, (int, float)) and not isinstance(v, bool)]
        if finished and not stored_metrics:
            skipped.append("%s/%s" % (Path(run_dir).parent.name, test_id))
            continue
        for path in Path(run_dir).glob("request_*.json"):
            with path.open(encoding="utf-8") as handle:
                record = json.load(handle)
            object_id = next((o for o in request_scores if path.stem.endswith("_" + o)), None)
            if object_id is None or "score" not in record:
                continue
            fresh = request_scores[object_id]
            if (record["score"] is None) == (fresh is None) and (
                    fresh is None or numeric_metrics(record["score"]) == numeric_metrics(fresh)):
                continue
            record["score"] = fresh
            _write_json(path, record)
        if not finished:
            unfinished += 1
        elif any(not _same(stored.get(k), v) for k, v in aggregate.items()) or set(stored_metrics) - set(aggregate):
            # Metrics the scorer no longer reports are dropped, not left stale.
            kept = {k: v for k, v in stored.items() if k not in stored_metrics}
            _write_json(scoring_path, {**kept, **aggregate,
                                       "rescored": "%s on %s" % (args.label, date.today().isoformat())})
            written += 1

    if args.verify:
        print("%d runs, %d aggregates differ" % (runs, mismatched))
        return 1 if mismatched else 0
    print("%d of %d runs with changed aggregates rewritten; %d unfinished runs (no scoring.json) got request scores only" % (written, runs, unfinished))
    if skipped:
        print("not rewritten, stored scoring.json has no metrics: %s" % ", ".join(skipped))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true",
                      help="compare stored request scores with fresh ones (default)")
    mode.add_argument("--verify", action="store_true",
                      help="compare re-computed aggregates with the stored scoring.json")
    mode.add_argument("--write", action="store_true",
                      help="write re-computed scores back into results/")
    parser.add_argument("--benchmark", help="limit to one benchmark (required for --verify/--write)")
    parser.add_argument("--run", help="--check a single run as <date>/<test_id>, verbose")
    parser.add_argument("--limit", type=int, default=0, help="--check only the newest N runs")
    parser.add_argument("--dump", help="--check: write the re-scored numbers to this file, for "
                                       "before/after comparison of a scorer change")
    parser.add_argument("--label", help="--write: recorded in scoring.json `rescored`, "
                                         "e.g. 'company_lists 2.0.0'")
    args = parser.parse_args(argv)
    if (args.verify or args.write) and not args.benchmark:
        parser.error("--verify and --write need --benchmark")
    if (args.verify or args.write) and (args.run or args.limit or args.dump):
        parser.error("--run, --limit and --dump go with --check")
    if args.write and not args.label:
        parser.error("--write needs --label")

    logging.disable(logging.CRITICAL)  # the scorers log per field at INFO

    tests = read_tests()
    if args.verify or args.write:
        return verify_or_write(args, tests)
    return check(args, tests)


if __name__ == "__main__":
    sys.exit(main())
