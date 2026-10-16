"""Point the site's benchmark pages and result page at the HumBen widgets.

The website (rise_benchmarks, NDR Core) keeps its pages as rows of `ndr_core_ndrcorepage`. This
script sets two kinds of page to a single NDR Core UI element, each a viz-modules widget:

- the page of every benchmark whose README is a BenchmarkCard (under the page `benchmarks`)
  holds `benchmark_card` (humben-card), which reads the card from the repo and finds the
  benchmark from the page URL. Pages of benchmarks without a card are never touched.
- the result overview page `benchmark-results` becomes a template page holding
  `benchmark_results` (humben-results), which reads benchmark_export.json and finds the
  benchmark from `?id=`.
- the `leaderboard` page holds only `dashboard` (humben), whose header carries the title and
  introduction.
- the test-run search page `testruns` becomes a template page holding `test_runs`
  (humben-runs), followed by the site's compare widget (the JS module whose configuration
  names the constructor HumbenCompare) so that it attaches to every run card.

The widgets show their own title, so NDR's page title is switched off on these pages. A part
whose UI element does not exist in the site is skipped, so nothing points at a missing
element. Each page is written in its own transaction; a second run changes nothing.

Run (the deploy does this after pulling, as the user that owns the database):
    python scripts/sync_benchmark_pages.py --db /srv/rise_benchmarks/db.sqlite3 [--only name ...] [--dry-run]
"""
import argparse
import difflib
import os
import sqlite3
import sys
from datetime import datetime, timezone

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [SCRIPTS_DIR, os.path.dirname(SCRIPTS_DIR)]

from benchmark_cards import card_benchmarks  # noqa: E402

# NDR Core UI elements (JavaScript modules) holding the humben-card and humben-results widgets.
CARD_ELEMENT = "benchmark_card"
RESULTS_ELEMENT = "benchmark_results"
RESULTS_PAGE = "benchmark-results"
DASHBOARD_ELEMENT = "dashboard"
LEADERBOARD_PAGE = "leaderboard"
RUNS_ELEMENT = "test_runs"
RUNS_PAGE = "testruns"
COMPARE_CONSTRUCTOR = "HumbenCompare"
TEMPLATE_PAGE = 1  # NdrCorePage.PageType.TEMPLATE


def render_page(element):
    """template_text of a page that holds only `element`."""
    return f"<p>[[element|{element}]]</p>"


def _element_exists(db, element):
    return db.execute("SELECT 1 FROM ndr_core_ndrcoreuielement WHERE name = ?", (element,)).fetchone() is not None


def _write(db, label, page, target, dry_run, out):
    """Bring `page` (id, page_type, template_text, show_page_title) to `target`, a dict of columns."""
    page_id, page_type, text, show_title = page
    current = {"page_type": page_type, "template_text": text, "show_page_title": show_title}
    if all(current[k] == v for k, v in target.items()):
        out(f"{label}: unchanged")
        return "unchanged"
    if dry_run:
        split = lambda t: (t or "").replace("</p>", "</p>\n").splitlines()
        lines = [f"{k}: {current[k]!r} -> {v!r}" for k, v in target.items()
                 if k != "template_text" and current[k] != v]
        lines += difflib.unified_diff(split(text), split(target["template_text"]),
                                      f"{label} (current)", f"{label} (widget)", lineterm="")
        out("\n".join(lines))
        return "diff"
    now = datetime.now(timezone.utc).replace(tzinfo=None).isoformat(sep=" ")
    columns = ", ".join(f"{k} = ?" for k in target)
    with db:
        db.execute(f"UPDATE ndr_core_ndrcorepage SET {columns}, last_modified = ? WHERE id = ?",
                   (*target.values(), now, page_id))
    out(f"{label}: written")
    return "written"


def sync(db, name, dry_run=False, out=print):
    """Point one benchmark's page at the card widget. Returns 'written', 'unchanged', 'diff' or 'no page'."""
    page = db.execute(
        "SELECT p.id, p.page_type, p.template_text, p.show_page_title FROM ndr_core_ndrcorepage p "
        "JOIN ndr_core_ndrcorepage parent ON p.parent_page_id = parent.id "
        "WHERE p.view_name = ? AND parent.view_name = 'benchmarks'", (name,)).fetchone()
    if page is None:
        out(f"{name}: no page under 'benchmarks'; skipped")
        return "no page"
    return _write(db, name, page, {"template_text": render_page(CARD_ELEMENT), "show_page_title": 0}, dry_run, out)


def sync_results_page(db, dry_run=False, out=print):
    """Turn the result overview page into a template page holding the results widget."""
    page = db.execute(
        "SELECT id, page_type, template_text, show_page_title FROM ndr_core_ndrcorepage WHERE view_name = ?",
        (RESULTS_PAGE,)).fetchone()
    if page is None:
        out(f"{RESULTS_PAGE}: no such page; skipped")
        return "no page"
    target = {"page_type": TEMPLATE_PAGE, "template_text": render_page(RESULTS_ELEMENT), "show_page_title": 0}
    return _write(db, RESULTS_PAGE, page, target, dry_run, out)


def sync_simple_page(db, view_name, target, dry_run=False, out=print):
    """Bring the top-level page `view_name` to `target`, a dict of columns."""
    page = db.execute(
        "SELECT id, page_type, template_text, show_page_title FROM ndr_core_ndrcorepage "
        "WHERE view_name = ? AND parent_page_id IS NULL", (view_name,)).fetchone()
    if page is None:
        out(f"{view_name}: no such page; skipped")
        return "no page"
    return _write(db, view_name, page, target, dry_run, out)


def _compare_element(db):
    """Name of the UI element running the compare widget, or None. Matched on the constructor:
    a hand-edited module config need not carry the package name."""
    row = db.execute(
        "SELECT belongs_to_id FROM ndr_core_ndrcoreuielementitem WHERE js_module_config LIKE ?",
        (f'%"constructor": "{COMPARE_CONSTRUCTOR}"%',)).fetchone()
    return row[0] if row else None


def sync_runs_page(db, dry_run=False, out=print):
    """Turn the test-run search page into a template page holding the runs widget."""
    page = db.execute(
        "SELECT id, page_type, template_text, show_page_title FROM ndr_core_ndrcorepage WHERE view_name = ?",
        (RUNS_PAGE,)).fetchone()
    if page is None:
        out(f"{RUNS_PAGE}: no such page; skipped")
        return "no page"
    text = render_page(RUNS_ELEMENT)
    compare = _compare_element(db)
    if compare:
        text += render_page(compare)
    else:
        out(f"{RUNS_PAGE}: no {COMPARE_CONSTRUCTOR} element; run cards will have no comparison view")
    target = {"page_type": TEMPLATE_PAGE, "template_text": text, "show_page_title": 0}
    return _write(db, RUNS_PAGE, page, target, dry_run, out)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--db", required=True, help="path to the site's db.sqlite3")
    parser.add_argument("--only", nargs="*", help="limit the card pages to these benchmarks")
    parser.add_argument("--dry-run", action="store_true", help="print a diff per page, write nothing")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(errors="replace")
    if not os.path.isfile(args.db):
        parser.error(f"{args.db} does not exist")
    db = sqlite3.connect(args.db)
    failed = []
    try:
        if _element_exists(db, CARD_ELEMENT):
            for name in card_benchmarks():
                if args.only and name not in args.only:
                    continue
                try:
                    sync(db, name, args.dry_run)
                except (OSError, sqlite3.Error) as e:
                    failed.append(name)
                    print(f"{name}: {e} (page left unchanged)", file=sys.stderr)
        else:
            print(f"UI element '{CARD_ELEMENT}' does not exist; benchmark pages left unchanged.")
        if _element_exists(db, RESULTS_ELEMENT):
            try:
                sync_results_page(db, args.dry_run)
            except sqlite3.Error as e:
                failed.append(RESULTS_PAGE)
                print(f"{RESULTS_PAGE}: {e} (page left unchanged)", file=sys.stderr)
        else:
            print(f"UI element '{RESULTS_ELEMENT}' does not exist; {RESULTS_PAGE} left unchanged.")
        if _element_exists(db, DASHBOARD_ELEMENT):
            try:
                sync_simple_page(db, LEADERBOARD_PAGE, {"template_text": render_page(DASHBOARD_ELEMENT),
                                                        "show_page_title": 0}, args.dry_run)
            except sqlite3.Error as e:
                failed.append(LEADERBOARD_PAGE)
                print(f"{LEADERBOARD_PAGE}: {e} (page left unchanged)", file=sys.stderr)
        if _element_exists(db, RUNS_ELEMENT):
            try:
                sync_runs_page(db, args.dry_run)
            except sqlite3.Error as e:
                failed.append(RUNS_PAGE)
                print(f"{RUNS_PAGE}: {e} (page left unchanged)", file=sys.stderr)
        else:
            print(f"UI element '{RUNS_ELEMENT}' does not exist; {RUNS_PAGE} left unchanged.")
    finally:
        db.close()
    if failed:
        print(f"not synced: {', '.join(failed)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
