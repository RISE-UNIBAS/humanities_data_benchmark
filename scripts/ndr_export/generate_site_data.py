"""Collect everything the website's widgets read into one folder, collected_results/site/.

The deploy copies this folder to the site's media (`/benchmarks/media/site/`), and the HumBen
widgets (viz-modules: humben-card, humben-results, humben-runs, humben-site) read only from there.
The repositories stay the source; the site shows the deployed state, and a change in the layout
of a repository only changes this script, not the widgets.

Layout of collected_results/site/:

  benchmark_export.json        copy of the benchmark export (written earlier in generate_all)
  tests.csv                    benchmarks/benchmarks_tests.csv
  scoring/<benchmark>.json     {"<date>/<test_id>": scoring.json} for every run of the benchmark
  cards/<benchmark>/           README.md, meta.json, benchmark_card.json and the example image,
                               downscaled for the web, for every benchmark with a card
  CHANGELOG.md, CITATION.cff, VERSION, CONTRIBUTING.md, contributors.json   from this repository
  news.md, about.md            from the benchmark-frontend repository, a sibling checkout of this
                               one (or --frontend); missing files are reported, not fatal

The news.md headings are checked here: a post whose heading is not `## YYYY-MM-DD — Title` would
silently be left off the page.

Run (from the project root):
    python -m scripts.ndr_export.generate_site_data [--frontend PATH]
"""
import argparse
import csv
import datetime
import json
import re
import shutil
import sys
from pathlib import Path

from scripts.ndr_export import BENCHMARKS_PATH, CONTRIBUTORS_PATH, EXPORT_PATH, RESULTS_PATH, TESTS_CSV

PROJECT_ROOT = BENCHMARKS_PATH.parent
SITE_PATH = EXPORT_PATH / "site"
DEFAULT_FRONTEND = PROJECT_ROOT.parent / "benchmark-frontend"
CARD_MARKER = "This README is a BenchmarkCard"
REPO_FILES = ["CHANGELOG.md", "CITATION.cff", "VERSION", "CONTRIBUTING.md"]
FRONTEND_FILES = ["news.md", "about.md"]
IMAGE_MAX_SIDE = 1400   # px; the card shows the example image at up to ~18rem, opened full size on click
NEWS_HEADING = re.compile(r"(\d{4}-\d{2}-\d{2}) — (.+)")


def _copy(src, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def _write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))


def _web_image(src, dest):
    """Downscale an image to IMAGE_MAX_SIDE as a JPEG; copy unchanged if Pillow cannot read it."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image
        with Image.open(src) as im:
            im.thumbnail((IMAGE_MAX_SIDE, IMAGE_MAX_SIDE))
            im.convert("RGB").save(dest.with_suffix(".jpg"), "JPEG", quality=82, optimize=True)
        return dest.with_suffix(".jpg").name
    except Exception as e:  # unreadable or unsupported: ship the original
        print(f"Warning: could not downscale {src.name} ({e}); copying it unchanged")
        shutil.copy2(src, dest)
        return dest.name


def collect_cards():
    count = 0
    for directory in sorted(p for p in BENCHMARKS_PATH.iterdir() if p.is_dir()):
        readme = directory / "README.md"
        if not readme.is_file() or CARD_MARKER not in readme.read_text(encoding="utf-8"):
            continue
        dest = SITE_PATH / "cards" / directory.name
        for name in ("README.md", "meta.json", "benchmark_card.json"):
            if (directory / name).is_file():
                _copy(directory / name, dest / name)
        meta = json.loads((directory / "meta.json").read_text(encoding="utf-8"))
        example = meta.get("example_image")
        if example and (directory / "images" / example).is_file():
            web_name = _web_image(directory / "images" / example, dest / "images" / example)
            if web_name != example:
                # The card widget reads the image name from meta.json; point it at the web copy.
                meta["example_image"] = web_name
                _write_json(dest / "meta.json", meta)
        count += 1
    print(f"Cards: {count}")


def collect_scoring():
    """{"<date>/<test_id>": scoring} per benchmark, so a run card needs one small fetch per benchmark."""
    tests = {}
    with open(TESTS_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            tests[row["id"]] = row["name"]
    by_benchmark = {}
    for path in sorted(RESULTS_PATH.glob("*/*/scoring.json")):
        test_id, date = path.parent.name, path.parent.parent.name
        benchmark = tests.get(test_id)
        if not benchmark:
            continue
        try:
            scoring = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            print(f"Warning: unreadable {path} ({e})")
            continue
        by_benchmark.setdefault(benchmark, {})[f"{date}/{test_id}"] = scoring
    for benchmark, runs in by_benchmark.items():
        _write_json(SITE_PATH / "scoring" / f"{benchmark}.json", runs)
    print(f"Scoring: {sum(len(r) for r in by_benchmark.values())} runs in {len(by_benchmark)} files")


def check_news(text):
    """Problems with news.md headings, as a list of messages."""
    problems, dates, fence = [], [], False
    for line in text.splitlines():
        if line.strip().startswith(("```", "~~~")):
            fence = not fence
        if fence or not line.startswith("## "):
            continue
        m = NEWS_HEADING.fullmatch(line[3:].strip())
        if not m:
            problems.append(f"heading '{line.strip()}' must read '## YYYY-MM-DD — Title' (em dash)")
            continue
        try:
            dates.append(datetime.date.fromisoformat(m.group(1)))
        except ValueError:
            problems.append(f"heading '{line.strip()}' has an invalid date")
    if dates != sorted(dates, reverse=True):
        problems.append("posts must be newest first")
    return problems


def collect_texts(frontend):
    for name in REPO_FILES:
        if (PROJECT_ROOT / name).is_file():
            _copy(PROJECT_ROOT / name, SITE_PATH / name)
        else:
            print(f"Warning: {name} not found in the data repository")
    _copy(CONTRIBUTORS_PATH, SITE_PATH / "contributors.json")
    for name in FRONTEND_FILES:
        src = frontend / name
        if not src.is_file():
            print(f"Warning: {src} not found; the site's {name[:-3]} page will show an error")
            continue
        _copy(src, SITE_PATH / name)
        if name == "news.md":
            for problem in check_news(src.read_text(encoding="utf-8")):
                print(f"Warning: news.md: {problem}")


def generate_site_data(frontend=None):
    frontend = Path(frontend) if frontend else DEFAULT_FRONTEND
    if SITE_PATH.exists():
        shutil.rmtree(SITE_PATH)
    SITE_PATH.mkdir(parents=True)
    export = EXPORT_PATH / "benchmark_export.json"
    if export.is_file():
        _copy(export, SITE_PATH / "benchmark_export.json")
    else:
        print("Warning: benchmark_export.json not generated yet; run generate_benchmark_export first")
    _copy(TESTS_CSV, SITE_PATH / "tests.csv")
    collect_cards()
    collect_scoring()
    collect_texts(frontend)
    size = sum(p.stat().st_size for p in SITE_PATH.rglob("*") if p.is_file())
    print(f"Site data: {size / 1e6:.1f} MB in {SITE_PATH}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--frontend", help=f"benchmark-frontend checkout (default: {DEFAULT_FRONTEND})")
    args = parser.parse_args(argv)
    generate_site_data(args.frontend)
    return 0


if __name__ == "__main__":
    sys.exit(main())
