"""How many stored runs each benchmark version was used for, for the Versions on the website's cards.

A run is made with the version in force at its first request, as the dataset export assigns
`benchmark_version` (scripts/results_index.py `version_at`); a run without a request time counts
from the start of its date folder. A run made earlier on the day a later version took effect is
ambiguous: it may have used either. Every run directory of a test in the CSV counts, as on the
website.

Output: collected_results/benchmark_versions.json

    {"personnel_cards": {"0.1.0": {"runs": 12, "ambiguous": 0}, "3.0.0": {...}}}

Versions without runs are left out.
"""
import json

from scripts.compare import EXPORT_PATH
from scripts.results_index import (TestCatalog, iter_request_records, iter_run_dirs, known_tests,
                                   local_time, version_at, version_history)

OUTPUT = EXPORT_PATH / "benchmark_versions.json"


def first_request_time(run):
    """The local time of the run's first request, else the start of its date folder."""
    times = [local_time(read.value.get("timestamp")) for _, read in iter_request_records(run)
             if isinstance(read.value, dict) and read.value.get("timestamp")]
    times = [t for t in times if t]
    return min(times) if times else run.date + "T00:00:00"


def version_runs(run_dirs, catalog, history_of=version_history):
    """{benchmark: {version: {"runs": n, "ambiguous": k}}}, versions oldest first."""
    histories, counts = {}, {}
    for run, benchmark in known_tests(run_dirs, catalog):
        if benchmark not in histories:
            histories[benchmark] = history_of(benchmark)
        version, ambiguous = version_at(histories[benchmark], first_request_time(run))
        if version is None:
            continue
        entry = counts.setdefault(benchmark, {}).setdefault(version, {"runs": 0, "ambiguous": 0})
        entry["runs"] += 1
        entry["ambiguous"] += bool(ambiguous)
    order = {b: [v.version for v in h] for b, h in histories.items()}
    return {b: dict(sorted(vs.items(), key=lambda kv: order[b].index(kv[0]))) for b, vs in sorted(counts.items())}


def generate_version_runs():
    counts = version_runs(iter_run_dirs(), TestCatalog.load())
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(counts, indent=1) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT}: {sum(e['runs'] for vs in counts.values() for e in vs.values())} runs "
          f"in {len(counts)} benchmarks")


if __name__ == "__main__":
    generate_version_runs()
