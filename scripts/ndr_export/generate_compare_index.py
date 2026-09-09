"""Index for the response-vs-ground-truth comparison widget.

The widget shows one run at a time: the model's response for each scored input, beside
the ground truth, with the differences marked. It fetches those per-input files straight
from the public repo at raw.githubusercontent.com, so it needs no bulk export -- but a
browser cannot list a directory, so it has to be told two things up front:

  * which inputs a benchmark has, and which source file(s) make up each one
  * which (date, provider, model) runs exist for a given test_id

Both are small. This index is a few hundred KB, against 52 MB for
test_runs_export.json, which is why the widget does not simply reuse that file.

Note that `test_id` is *not* a key on its own: the same test is re-run on later dates,
and roughly a third of test ids have more than one run. Every entry therefore carries a
list of runs, and the widget needs a date as well as a test id to identify one.

Output: collected_results/compare_index.json

    {
      "generated": "2026-09-09",
      "repo_raw_base": "https://raw.githubusercontent.com/.../refs/heads/main",
      "benchmarks": {
        "magazine_pages": {
          "title": "Magazine Pages",
          "ranking": {"metric": "f1", "order": "desc"},
          "inputs": [{"basename": "0002_p002", "kind": "images",
                      "files": ["0002_p002.jpg"]}]
        }
      },
      "runs": {
        "T1597": {"benchmark": "magazine_pages",
                  "runs": [{"date": "2026-08-18", "provider": "genai",
                            "model": "gemini-3.7-flash"}]}
      }
    }
"""
import json
import re
from datetime import datetime

from scripts.ndr_export import BENCHMARKS_PATH, EXPORT_PATH, RESULTS_PATH
from scripts.ndr_export.meta_utils import get_benchmarks, get_meta, load_json

REPO_RAW_BASE = ("https://raw.githubusercontent.com/RISE-UNIBAS/"
                 "humanities_data_benchmark/refs/heads/main")

PAGE_SUFFIX = re.compile(r"_p\d+$")
"""Benchmarks with multi_image_support collapse `<basename>_p1..pN` into one scored
object, so the source files of an object are not always named after it exactly."""


def natural_key(text):
    """Sort key that orders line_2 before line_10 rather than after it."""
    return [int(part) if part.isdigit() else part.lower()
            for part in re.split(r"(\d+)", text)]


def get_inputs(benchmark_name):
    """The scored objects of a benchmark, each with the source file(s) it is made of.

    Ground truth defines the object set: `Benchmark.load_ground_truth` reads
    `ground_truths/<basename>.json`, so one file there is exactly one scored object.
    Source files are then matched by stem, or by `<basename>_p<N>` for the benchmarks
    that collapse a multi-page object into one request.

    Returns (inputs, orphans). An orphan is a ground truth with no source file; there
    are a handful in the corpus, and emitting them would hand the widget entries it can
    never render.
    """
    benchmark_dir = BENCHMARKS_PATH / benchmark_name
    truth_dir = benchmark_dir / "ground_truths"
    if not truth_dir.is_dir():
        return [], []

    source_dir = kind = None
    for candidate in ("images", "texts"):
        if (benchmark_dir / candidate).is_dir():
            source_dir, kind = benchmark_dir / candidate, candidate
            break
    if source_dir is None:
        return [], []

    by_stem = {}
    for entry in source_dir.iterdir():
        if entry.is_file():
            by_stem.setdefault(entry.stem, []).append(entry.name)

    inputs, orphans = [], []
    for truth in sorted(truth_dir.glob("*.json"), key=lambda f: natural_key(f.stem)):
        basename = truth.stem
        files = sorted(by_stem.get(basename, []), key=natural_key)
        if not files:
            files = sorted((name
                            for stem, names in by_stem.items()
                            if PAGE_SUFFIX.sub("", stem) == basename
                            for name in names),
                           key=natural_key)
        if not files:
            orphans.append(basename)
            continue
        inputs.append({"basename": basename, "kind": kind, "files": files})

    return inputs, orphans


def get_runs():
    """test_id -> benchmark plus every (date, provider, model) run of it.

    Read from the result tree rather than from test_runs_export.json, so this step does
    not depend on the order the generators run in.
    """
    runs = {}
    for date_dir in sorted(p for p in RESULTS_PATH.iterdir() if p.is_dir()):
        for run_dir in sorted(p for p in date_dir.iterdir() if p.is_dir()):
            request_files = sorted(run_dir.glob("request_*.json"))
            provider = model = None
            for request_file in request_files:
                data = load_json(request_file)
                if isinstance(data, dict) and data.get("provider") and data.get("model"):
                    provider, model = data["provider"], data["model"]
                    break

            scoring = load_json(run_dir / "scoring.json")
            record = {
                "date": date_dir.name,
                "provider": provider,
                "model": model,
                "has_scoring": isinstance(scoring, dict),
            }

            # A response file is `request_<prefix>_<basename>.json`, and for 188 older
            # run directories the prefix is not the directory name: the ids were
            # re-padded (T17 -> T0017, T02 -> T0002) without renaming the files, and the
            # two padding widths in use make it unsafe to derive. Test ids contain no
            # underscore, so the first token of the stem is the prefix. Recorded only
            # when it differs, so the index does not carry 2000 redundant strings.
            if request_files:
                stem = request_files[0].name[len("request_"):-len(".json")]
                prefix = stem.split("_")[0]
                if prefix != run_dir.name:
                    record["prefix"] = prefix

            runs.setdefault(run_dir.name, {"benchmark": None, "runs": []})["runs"].append(record)

    return runs


def attach_benchmarks(runs, benchmarks):
    """Fills in each test id's benchmark, which the result tree does not record.

    A run directory holds no benchmark name, so it is taken from the benchmark whose
    test list contains this id.
    """
    for name, entry in benchmarks.items():
        for test_id in entry.pop("_test_ids", []):
            if test_id in runs:
                runs[test_id]["benchmark"] = name


def generate_compare_index():
    """Writes collected_results/compare_index.json."""
    from scripts.ndr_export.test_utils import get_all_tests

    all_tests = get_all_tests()

    benchmarks = {}
    for benchmark in get_benchmarks():
        meta = get_meta(benchmark) or {}
        inputs, orphans = get_inputs(benchmark)
        if orphans:
            print(f"  {benchmark}: {len(orphans)} ground truth(s) with no source file, "
                  f"skipped: {orphans}")
        benchmarks[benchmark] = {
            "title": meta.get("title", benchmark),
            "ranking": meta.get("ranking"),
            "inputs": inputs,
            "_test_ids": [t.get("id") for t in all_tests
                          if t.get("name") == benchmark and t.get("id")],
        }

    runs = get_runs()
    attach_benchmarks(runs, benchmarks)

    unattached = [test_id for test_id, entry in runs.items() if not entry["benchmark"]]
    if unattached:
        print(f"  {len(unattached)} test id(s) in results/ are absent from "
              f"benchmarks_tests.csv, so their benchmark is unknown: "
              f"{sorted(unattached)[:6]}{' ...' if len(unattached) > 6 else ''}")

    index = {
        "generated": datetime.now().strftime("%Y-%m-%d"),
        "repo_raw_base": REPO_RAW_BASE,
        "benchmarks": benchmarks,
        "runs": runs,
    }

    target = EXPORT_PATH / "compare_index.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(index, handle, separators=(",", ":"), ensure_ascii=False)

    objects = sum(len(b["inputs"]) for b in benchmarks.values())
    total_runs = sum(len(e["runs"]) for e in runs.values())
    print(f"Wrote {target} - {len(benchmarks)} benchmarks, {objects} scored objects, "
          f"{len(runs)} test ids, {total_runs} runs "
          f"({target.stat().st_size / 1024:.0f} KB)")
