"""The benchmark version of every stored run, for the website: the counts per version on the cards
and the versions on each run's page.

A run is made with the version the runner recorded in its scoring.json, else the version in force
at its first request, and scored with the latest re-scoring since, as the dataset export assigns
`benchmark_version` and `benchmark_version_scored` (scripts/results_index.py `run_version`,
`scored_version`). A run without a request time counts from the start of its date folder. A run is
ambiguous when it may have been made with the next version: made earlier on the day that version
took effect, or recorded while the benchmark's files had uncommitted changes. Every run directory
of a test in the CSV counts, as on the website.

Output, in collected_results/:

    benchmark_versions.json  {"personnel_cards": {"0.1.0": {"runs": 12, "ambiguous": 0}, ...}}
                             versions oldest first, those without runs left out
    run_versions.json        {"2026-10-18/T0001": {"made": "2.0.0", "scored": "3.0.0",
                                                   "basis": "inferred"}, ...}
                             basis: recorded, inferred or ambiguous, as in the dataset export;
                             an ambiguous run also names the next version, `or`, if there is one
"""
import json

from scripts.compare import EXPORT_PATH
from scripts.results_index import (TestCatalog, iter_request_records, iter_run_dirs, known_tests,
                                   local_time, read_scoring, rescoring, run_version, scored_version,
                                   version_history)

COUNTS = EXPORT_PATH / "benchmark_versions.json"
RUNS = EXPORT_PATH / "run_versions.json"


def first_request_time(run):
    """The local time of the run's first request, else the start of its date folder."""
    times = [local_time(read.value.get("timestamp")) for _, read in iter_request_records(run)
             if isinstance(read.value, dict) and read.value.get("timestamp")]
    times = [t for t in times if t]
    return min(times) if times else run.date + "T00:00:00"


def run_versions(run_dirs, catalog, history_of=version_history):
    """({benchmark: {version: {"runs", "ambiguous"}}}, {"<date>/<test id>": {"made", "scored",
    "basis", and "or" when ambiguous}}), versions oldest first."""
    histories, made, rescorings = {}, [], {}
    for run, benchmark in known_tests(run_dirs, catalog):
        if benchmark not in histories:
            histories[benchmark] = history_of(benchmark)
        history = histories[benchmark]
        if not history:
            continue
        scoring = read_scoring(run)
        stored = scoring.value if scoring.status == "ok" and isinstance(scoring.value, dict) else {}
        first = first_request_time(run)
        version, basis = run_version(history, first, stored.get("benchmark_version"))
        made.append((run, benchmark, version, basis, first[:10]))
        named = rescoring(history, stored["rescored"], first[:10]) if stored.get("rescored") else None
        if named:
            rescorings.setdefault(benchmark, set()).add(named)
    counts, runs = {}, {}
    for run, benchmark, version, basis, day in made:
        entry = counts.setdefault(benchmark, {}).setdefault(version, {"runs": 0, "ambiguous": 0})
        entry["runs"] += 1
        entry["ambiguous"] += basis == "ambiguous"
        history = histories[benchmark]
        entry = {"made": version, "basis": basis,
                 "scored": scored_version(history, version, day, rescorings.get(benchmark, ()))}
        order = [v.version for v in history]
        if basis == "ambiguous" and order.index(version) + 1 < len(order):
            entry["or"] = order[order.index(version) + 1]
        runs["%s/%s" % (run.date, run.test_id)] = entry
    order = {b: [v.version for v in h] for b, h in histories.items()}
    counts = {b: dict(sorted(vs.items(), key=lambda kv: order[b].index(kv[0]))) for b, vs in sorted(counts.items())}
    return counts, runs


def generate_version_runs():
    counts, runs = run_versions(iter_run_dirs(), TestCatalog.load())
    COUNTS.parent.mkdir(parents=True, exist_ok=True)
    COUNTS.write_text(json.dumps(counts, indent=1) + "\n", encoding="utf-8")
    RUNS.write_text(json.dumps(runs, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {COUNTS.name} and {RUNS.name}: {len(runs)} runs in {len(counts)} benchmarks")


if __name__ == "__main__":
    generate_version_runs()
