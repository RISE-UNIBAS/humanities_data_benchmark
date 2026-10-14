import sqlite3

import pytest

import sync_benchmark_pages as sbp
from benchmark_card_schema import SCHEMA_ID  # noqa: F401  (schema module importable without the runner)
from benchmark_cards import MARKER

META = {
    "description": "Cards & more.",
    "license": "Public Domain",
    "source": {"collection": "Archive", "url": "https://example.org/x", "signature": "E1", "period": "1941-1961"},
}
CARD = {"benchmark_details": {"data_type": "image", "languages": ["German"]}, "data": {"size": "3 evaluated objects"}}
ELEMENTS = {"tags": "x_tags", "img": "x_img", "cont": "x_cont"}


def readme(body="**Goal:** text with `code` and [prompt](prompts/prompt.txt)."):
    return (f"# X\n\n{MARKER}\n\n<!-- hidden -->\n\n"
            f"## Purpose and Intended Users\n\n{body}\n\n## Data\n\n**Size:** 3\n")


def render(body=None, elements=ELEMENTS):
    return sbp.render_page("x", readme() if body is None else readme(body), META, CARD, elements)


def test_stub_readme_is_rejected():
    with pytest.raises(sbp.PageRenderError):
        sbp.render_page("x", "# X\n\nstub", META, CARD, ELEMENTS)


def test_one_block_per_section_after_overview_and_dataset():
    text = render()
    blocks = [b.split("]]")[0] for b in text.split("[[start_block=")[1:]]
    assert blocks == ["Overview", "Dataset", "Purpose and Intended Users", "Data"]
    assert text.count("[[start_block") == text.count("[[end_block]]")
    assert text.count("[[start_cell") == text.count("[[end_cell]]")


def test_preamble_and_comments_are_not_rendered():
    text = render()
    assert "hidden" not in text and MARKER not in text


def test_elements_and_fact_table():
    text = render()
    for name in ELEMENTS.values():
        assert f"[[element|{name}]]" in text
    assert "<th>Amount</th><td>3 evaluated objects</td>" in text
    assert "Cards &amp; more." in text


def test_missing_elements_are_left_out():
    assert "[[element|" not in render(elements={})


def test_relative_links_point_to_github_and_bare_urls_are_linked():
    text = render("**Goal:** [prompt](prompts/prompt.txt) and https://a.org/x#/de/1. and `https://b.org`")
    assert ('href="https://github.com/RISE-UNIBAS/humanities_data_benchmark/blob/main/'
            'benchmarks/x/prompts/prompt.txt"') in text
    assert '<a href="https://a.org/x#/de/1">' in text
    assert "<code>https://b.org</code>" in text


def test_code_fence_becomes_ndr_code_block():
    text = render('**Format:**\n\n```json\n{"a": "<b>", "c": "[[x]]"}\n```\n\nafter')
    assert '[[start_code=json]]{"a": "&lt;b&gt;", "c": "[[x]]"}[[end_code]]' in text
    assert "<p>[[start_code" not in text


def test_double_brackets_in_text_are_refused():
    with pytest.raises(sbp.PageRenderError):
        render("**Goal:** see [[toc]]")


@pytest.fixture
def db():
    conn = sqlite3.connect(":memory:")
    conn.executescript("""
        CREATE TABLE ndr_core_ndrcorepage (id INTEGER PRIMARY KEY, view_name TEXT, parent_page_id INTEGER,
                                           template_text TEXT, last_modified TEXT);
        CREATE TABLE ndr_core_ndrcoreuielementitem (belongs_to_id TEXT, object_id TEXT, result_field_id INTEGER);
        INSERT INTO ndr_core_ndrcorepage VALUES (3, 'benchmarks', NULL, '', '');
        INSERT INTO ndr_core_ndrcorepage VALUES (18, 'personnel_cards', 3, '<p>old</p>', '');
        INSERT INTO ndr_core_ndrcoreuielementitem VALUES ('personel_cards_tags', 'personnel_cards', 12);
        INSERT INTO ndr_core_ndrcoreuielementitem VALUES ('personnel_cards_img', 'personnel_cards', 5);
    """)
    yield conn
    conn.close()


def test_sync_writes_once_then_is_unchanged(db):
    messages = []
    assert sbp.sync(db, "personnel_cards", dry_run=True, out=messages.append) == "diff"
    assert db.execute("SELECT template_text FROM ndr_core_ndrcorepage WHERE id = 18").fetchone()[0] == "<p>old</p>"
    assert sbp.sync(db, "personnel_cards", out=messages.append) == "written"
    text = db.execute("SELECT template_text FROM ndr_core_ndrcorepage WHERE id = 18").fetchone()[0]
    assert "[[element|personel_cards_tags]]" in text and "[[element|personnel_cards_img]]" in text
    assert any("no 'cont' element" in m for m in messages)
    assert sbp.sync(db, "personnel_cards", out=messages.append) == "unchanged"


def test_sync_skips_benchmark_without_page(db):
    db.execute("DELETE FROM ndr_core_ndrcorepage WHERE id = 18")
    assert sbp.sync(db, "personnel_cards", out=lambda m: None) == "no page"
