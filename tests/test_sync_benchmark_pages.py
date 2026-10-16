import sqlite3

import pytest

import sync_benchmark_pages as sbp

SCHEMA = """
    CREATE TABLE ndr_core_ndrcorepage (id INTEGER PRIMARY KEY, view_name TEXT, parent_page_id INTEGER,
                                       page_type INTEGER, template_text TEXT, show_page_title INTEGER,
                                       last_modified TEXT);
    CREATE TABLE ndr_core_ndrcoreuielement (name TEXT PRIMARY KEY);
    CREATE TABLE ndr_core_ndrcoreuielementitem (belongs_to_id TEXT, js_module_config TEXT);
    INSERT INTO ndr_core_ndrcorepage VALUES (3, 'benchmarks', NULL, 1, '', 1, '');
    INSERT INTO ndr_core_ndrcorepage VALUES (18, 'personnel_cards', 3, 1, '<p>old</p>', 1, '');
    INSERT INTO ndr_core_ndrcorepage VALUES (19, 'benchmark-results', NULL, 4, '', 1, '');
    INSERT INTO ndr_core_ndrcorepage VALUES (2, 'testruns', NULL, 3, '<p>intro</p>', 1, '');
    INSERT INTO ndr_core_ndrcorepage VALUES (4, 'leaderboard', NULL, 1, '<p>intro</p><p>[[element|dashboard]]</p>', 1, '');
    INSERT INTO ndr_core_ndrcorepage VALUES (5, 'news', NULL, 1, '<p>old news</p>', 1, '');
    INSERT INTO ndr_core_ndrcorepage VALUES (6, 'about', NULL, 1, '<p>old about</p>', 1, '');
"""


def _connect(path=":memory:", elements=("benchmark_card", "benchmark_results")):
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    conn.executemany("INSERT INTO ndr_core_ndrcoreuielement VALUES (?)", [(e,) for e in elements])
    conn.commit()
    return conn


def _page(db, page_id):
    return db.execute("SELECT page_type, template_text, show_page_title FROM ndr_core_ndrcorepage WHERE id = ?",
                      (page_id,)).fetchone()


@pytest.fixture
def db():
    conn = _connect()
    yield conn
    conn.close()


def test_page_holds_only_the_element():
    assert sbp.render_page("benchmark_card") == "<p>[[element|benchmark_card]]</p>"


def test_card_page_written_once_then_unchanged(db):
    quiet = lambda m: None
    assert sbp.sync(db, "personnel_cards", dry_run=True, out=quiet) == "diff"
    assert _page(db, 18) == (1, "<p>old</p>", 1)
    assert sbp.sync(db, "personnel_cards", out=quiet) == "written"
    assert _page(db, 18) == (1, "<p>[[element|benchmark_card]]</p>", 0)
    assert sbp.sync(db, "personnel_cards", out=quiet) == "unchanged"


def test_card_page_missing_is_skipped(db):
    db.execute("DELETE FROM ndr_core_ndrcorepage WHERE id = 18")
    assert sbp.sync(db, "personnel_cards", out=lambda m: None) == "no page"


def test_results_page_becomes_template_with_widget(db):
    quiet = lambda m: None
    assert sbp.sync_results_page(db, out=quiet) == "written"
    assert _page(db, 19) == (1, "<p>[[element|benchmark_results]]</p>", 0)
    assert sbp.sync_results_page(db, out=quiet) == "unchanged"


@pytest.mark.parametrize("elements,card,results", [
    ((), (1, "<p>old</p>", 1), (4, "", 1)),
    (("benchmark_card",), (1, "<p>[[element|benchmark_card]]</p>", 0), (4, "", 1)),
    (("benchmark_results",), (1, "<p>old</p>", 1), (1, "<p>[[element|benchmark_results]]</p>", 0)),
])
def test_missing_element_leaves_its_pages_alone(tmp_path, elements, card, results):
    path = tmp_path / "site.sqlite3"
    _connect(str(path), elements).close()
    assert sbp.main(["--db", str(path), "--only", "personnel_cards"]) == 0
    conn = sqlite3.connect(path)
    assert _page(conn, 18) == card
    assert _page(conn, 19) == results
    conn.close()


def test_runs_page_holds_runs_widget_then_compare(db):
    # As on the live site: no "name" key in the config, only scripts, constructor and options.
    db.execute("""INSERT INTO ndr_core_ndrcoreuielementitem VALUES
                  ('compare', '{"scripts": [], "constructor": "HumbenCompare", "options": {"mode": "cards"}}')""")
    assert sbp.sync_runs_page(db, out=lambda m: None) == "written"
    assert _page(db, 2) == (1, "<p>[[element|test_runs]]</p><p>[[element|compare]]</p>", 0)
    assert sbp.sync_runs_page(db, out=lambda m: None) == "unchanged"


def test_runs_page_without_compare_element(db):
    messages = []
    assert sbp.sync_runs_page(db, out=messages.append) == "written"
    assert _page(db, 2)[1] == "<p>[[element|test_runs]]</p>"
    assert any("no HumbenCompare element" in m for m in messages)


def test_leaderboard_page_holds_only_the_dashboard(db):
    target = {"template_text": sbp.render_page("dashboard"), "show_page_title": 0}
    assert sbp.sync_simple_page(db, "leaderboard", target, out=lambda m: None) == "written"
    assert _page(db, 4) == (1, "<p>[[element|dashboard]]</p>", 0)


def test_site_pages_follow_their_elements(tmp_path):
    path = tmp_path / "site.sqlite3"
    _connect(str(path), ("site_news",)).close()
    assert sbp.main(["--db", str(path)]) == 0
    conn = sqlite3.connect(path)
    assert _page(conn, 5) == (1, "<p>[[element|site_news]]</p>", 0)
    assert _page(conn, 6) == (1, "<p>old about</p>", 1)   # site_about does not exist: untouched
    conn.close()
