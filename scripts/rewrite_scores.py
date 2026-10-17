"""Re-score a benchmark's stored runs with its current scorer and write the scores back.

Used after a MAJOR version (a scorer change or a ground-truth correction) whose new scores
apply to old responses too, so stored and new runs stay comparable. A run whose stored
`scoring.json` lacks the metrics is left alone and reported.

Per run, a request counts as scored if its file records a score, or if it was skipped as
unparseable and the benchmark now scores such answers as misses. A file without a `score`
key comes from a run that predates per-request scores: that runner scored every request and
read the answer from the response text (a ```json block or the whole text) when nothing was
parsed, so all of them count and the text is parsed the same way. The rewritten
`scoring.json` keeps `cost_summary` and every key the scorer does not produce, and records
the rewrite in `rescored`. Only files whose numbers change are written; a stored score that
lacks the field detail of today's scorer is not rewritten for that alone.

`--verify` first: with an unchanged scorer it must reproduce the stored aggregates. Runs
scored before a later scorer change cannot reproduce exactly; the report lists them.

Usage:
    python scripts/rewrite_scores.py --benchmark company_lists --verify
    python scripts/rewrite_scores.py --benchmark company_lists --write --label "company_lists 2.0.0"
"""
import argparse
import json
import logging
import math
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from scripts.offline_scoring import (iter_run_inputs, iter_runs, load_scorer, numeric_metrics,
                                     read_tests, rules_of_test)


def _legacy_parse(text):
    """The answer as the runner read it before responses were parsed at request time."""
    if not isinstance(text, str):
        return None
    block = re.search(r"```json\s*([\[{].*?[]}])\s*```", text, re.DOTALL)
    try:
        return json.loads(block.group(1) if block else text)
    except ValueError:
        return None


def rescore_run(run_dir, test_id, scorer):
    """({request file: fresh score or None}, aggregate) for one run."""
    request_scores, counted = {}, []
    for object_id, record, answer, truth in iter_run_inputs(run_dir, test_id):
        if "score" in record:
            # A skipped unparseable answer counts once the benchmark scores it as a miss.
            scored = record["score"] is not None or (
                record.get("parsed") is None and getattr(scorer, "score_unparseable_as_miss", False))
        else:
            scored = True
        if "score" not in record and answer.parsed is None:
            answer.parsed = _legacy_parse(record.get("text"))
        fresh = scorer.score_request_answer(object_id, answer, truth) if scored else None
        request_scores[object_id] = fresh
        if fresh is not None:
            counted.append(fresh)
    return request_scores, scorer.score_benchmark(counted)


def _same(a, b):
    if isinstance(a, float) or isinstance(b, float):
        return isinstance(a, (int, float)) and isinstance(b, (int, float)) and math.isclose(a, b, abs_tol=1e-9)
    return a == b


def _write_json(path, content):
    # The runner's format: json.dumps(indent=4), text mode.
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(json.dumps(content, indent=4))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--benchmark", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--verify", action="store_true", help="compare re-computed aggregates with the stored ones")
    mode.add_argument("--write", action="store_true", help="write re-computed scores back into results/")
    parser.add_argument("--label", help="recorded in scoring.json `rescored`, e.g. 'company_lists 2.0.0'")
    args = parser.parse_args(argv)
    if args.write and not args.label:
        parser.error("--write needs --label")
    logging.disable(logging.CRITICAL)

    tests = read_tests()
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

        if finished and any(stored.get(k) is None for k in aggregate):
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
            record["score"] = request_scores[object_id]
            _write_json(path, record)
        if not finished:
            unfinished += 1
        elif any(not _same(stored.get(k), v) for k, v in aggregate.items()):
            _write_json(scoring_path, {**stored, **aggregate,
                                       "rescored": "%s on %s" % (args.label, date.today().isoformat())})
            written += 1

    if args.verify:
        print("%d runs, %d aggregates differ" % (runs, mismatched))
        return 1 if mismatched else 0
    print("%d of %d runs with changed aggregates rewritten; %d unfinished runs (no scoring.json) got request scores only" % (written, runs, unfinished))
    if skipped:
        print("not rewritten, stored scoring.json has no metrics: %s" % ", ".join(skipped))
    return 0


if __name__ == "__main__":
    sys.exit(main())
