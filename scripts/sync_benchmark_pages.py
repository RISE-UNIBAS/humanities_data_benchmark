"""Write the site's benchmark pages from the BenchmarkCard READMEs.

The website (rise_benchmarks, NDR Core) keeps each benchmark page as HTML with NDR template tags
in the `template_text` of an `ndr_core_ndrcorepage` row under the page `benchmarks`. For every
benchmark whose README is a card, this script renders that text from the README, meta.json and
benchmark_card.json and writes it into the site's SQLite database. Pages of benchmarks without a
card are never touched. A page is written only when its whole conversion succeeds, each in its own
transaction; a second run changes nothing.

Page layout: an Overview block (description, buttons, table of contents), a Dataset block (fact
table, tags, contributors and example image elements), then one block per `##` section of the
README.

Run (the deploy does this after pulling, as the user that owns the database):
    python scripts/sync_benchmark_pages.py --db /srv/rise_benchmarks/db.sqlite3 [--only name ...] [--dry-run]
"""
import argparse
import difflib
import html
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone

import markdown

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [SCRIPTS_DIR, os.path.dirname(SCRIPTS_DIR)]

from benchmark_cards import BENCHMARKS_DIR, _split_sections, card_benchmarks, is_card  # noqa: E402

REPO_BLOB = "https://github.com/RISE-UNIBAS/humanities_data_benchmark/blob/main/benchmarks/{name}/{path}"
REPO_RAW = "https://raw.githubusercontent.com/RISE-UNIBAS/humanities_data_benchmark/main/benchmarks/{name}/{path}"
# NDR Core refuses to render a page with more container tags than this.
MAX_CONTAINER_TAGS = 50
# ndr_core_ndrcoreresultfield ids that render a benchmark's tags, example image and contributors.
ELEMENT_RESULT_FIELDS = {12: "tags", 5: "img", 14: "cont"}

_FENCE = re.compile(r"^(```|~~~)([\w-]*)[^\n]*\n(.*?)^\1[ \t]*$", re.M | re.S)
_BARE_URL = re.compile(r"(?<![<(\[\"'=`])(https?://[^\s<>()\]`]*[^\s<>()\]`.,;:])")


class PageRenderError(ValueError):
    pass


def _markdown_to_html(text, name):
    codes = []

    def stash(m):
        codes.append((m.group(2) or "text", m.group(3).rstrip("\n")))
        return f"\n\nNDRCODEBLOCK{len(codes) - 1}\n\n"

    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = _FENCE.sub(stash, text)
    text = _BARE_URL.sub(r"<\1>", text)
    out = markdown.markdown(text, extensions=["tables", "sane_lists"])

    def relink(m):
        attr, url = m.group(1), m.group(2)
        if re.match(r"^(?:[a-z][a-z0-9+.-]*:|#|/)", url, re.I):
            return m.group(0)
        template = REPO_RAW if attr == "src" else REPO_BLOB
        return f'{attr}="{template.format(name=name, path=url)}"'

    out = re.sub(r'(href|src)="([^"]*)"', relink, out)
    if "[[" in out:
        raise PageRenderError("README text contains '[[', which the site reads as a template tag")

    def unstash(m):
        language, code = codes[int(m.group(1))]
        return f"[[start_code={language}]]{html.escape(code, quote=False)}[[end_code]]"

    out = re.sub(r"<p>NDRCODEBLOCK(\d+)</p>", unstash, out)
    if "NDRCODEBLOCK" in out:
        raise PageRenderError("a code block could not be placed (fence inside a list or quote?)")
    return out


def _fact_table(meta, card, elements):
    source = meta.get("source", {})
    details = card.get("benchmark_details", {})
    origin = html.escape(source.get("collection", ""), quote=False)
    if source.get("url"):
        url = html.escape(source["url"])
        origin = f'{origin}, <a href="{url}">{url}</a>'
    rows = [
        ("Data Type", details.get("data_type", "")),
        ("Amount", card.get("data", {}).get("size", "")),
        ("Signature", source.get("signature", "")),
        ("Language", ", ".join(details.get("languages", []))),
        ("Time Period", source.get("period", "")),
        ("License", meta.get("license", "")),
    ]
    rows = [(k, html.escape(v, quote=False)) for k, v in rows]
    rows.insert(2, ("Origin", origin))
    if elements.get("tags"):
        rows.append(("Tags", f"[[element|{elements['tags']}]]"))
    body = "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in rows if v)
    return f'<figure class="table"><table><tbody>{body}</tbody></table></figure>'


def render_page(name, readme, meta, card, elements):
    """template_text for benchmark `name`.

    card: the "benchmark_card" object of benchmark_card.json.
    elements: {"tags", "img", "cont"} -> NDR UI element name; missing keys are left out.
    """
    if not is_card(readme):
        raise PageRenderError(f"{name}/README.md is not a BenchmarkCard")
    description = html.escape(meta.get("description", ""), quote=False)
    parts = [
        "<p>[[start_block=Overview]]</p><p>[[start_cell]]</p>",
        f"<p>{description}</p>",
        "<p>"
        f"[[page-btn-secondary-lg|benchmarks/{name}|Dataset Description]] "
        f"[[page-btn-primary-lg|benchmark-results?id={name}|Result Overview]] "
        f"[[page-btn-primary-lg|testruns?testruns_benchmark={name}__true&amp;search_button_testruns=Search|Test Runs]]"
        "</p>",
        "<p>[[end_cell]]</p><p>[[start_cell=40%]]</p><p>[[toc]]</p><p>[[end_cell]]</p><p>[[end_block]]</p>",
        "<p>[[start_block=Dataset]]</p><p>[[start_cell]]</p>",
        _fact_table(meta, card, elements),
    ]
    if elements.get("cont"):
        parts.append(f"<p>[[element|{elements['cont']}]]</p>")
    parts.append("<p>[[end_cell]]</p>")
    if elements.get("img"):
        parts.append(f"<p>[[start_cell=40%]]</p><p>[[element|{elements['img']}]]</p><p>[[end_cell]]</p>")
    parts.append("<p>[[end_block]]</p>")

    for heading, body_start, body_end in _split_sections(readme):
        if "[" in heading or "]" in heading:
            raise PageRenderError(f"section heading '{heading}' contains a bracket")
        parts.append(f"<p>[[start_block={html.escape(heading, quote=False)}]]</p>")
        parts.append(_markdown_to_html(readme[body_start:body_end].strip(), name))
        parts.append("<p>[[end_block]]</p>")

    text = "".join(parts)
    containers = len(re.findall(r"\[\[(?:start|end)_(?:block|cell)", text))
    if containers > MAX_CONTAINER_TAGS:
        raise PageRenderError(f"{containers} container tags; the site renders at most {MAX_CONTAINER_TAGS}")
    return text


def _find_page(db, name):
    return db.execute(
        "SELECT p.id, p.template_text FROM ndr_core_ndrcorepage p "
        "JOIN ndr_core_ndrcorepage parent ON p.parent_page_id = parent.id "
        "WHERE p.view_name = ? AND parent.view_name = 'benchmarks'", (name,)).fetchone()


def _elements(db, name):
    marks = ",".join("?" * len(ELEMENT_RESULT_FIELDS))
    rows = db.execute(
        f"SELECT belongs_to_id, result_field_id FROM ndr_core_ndrcoreuielementitem "
        f"WHERE object_id = ? AND result_field_id IN ({marks})", (name, *ELEMENT_RESULT_FIELDS))
    return {ELEMENT_RESULT_FIELDS[field]: element for element, field in rows}


def sync(db, name, dry_run=False, out=print):
    """Render and write one benchmark's page. Returns 'written', 'unchanged', 'diff' or 'no page'."""
    directory = os.path.join(BENCHMARKS_DIR, name)
    page = _find_page(db, name)
    if page is None:
        out(f"{name}: no page under 'benchmarks'; skipped")
        return "no page"
    with open(os.path.join(directory, "README.md"), encoding="utf-8") as f:
        readme = f.read()
    with open(os.path.join(directory, "meta.json"), encoding="utf-8") as f:
        meta = json.load(f)
    card_path = os.path.join(directory, "benchmark_card.json")
    if not os.path.isfile(card_path):
        raise PageRenderError("benchmark_card.json missing; run scripts/benchmark_cards.py")
    with open(card_path, encoding="utf-8") as f:
        card = json.load(f)["benchmark_card"]

    elements = _elements(db, name)
    for key in sorted(set(ELEMENT_RESULT_FIELDS.values()) - set(elements)):
        out(f"{name}: no '{key}' element; left out of the page")

    page_id, current = page
    new_text = render_page(name, readme, meta, card, elements)
    if new_text == current:
        out(f"{name}: unchanged")
        return "unchanged"
    if dry_run:
        split = lambda t: (t or "").replace("</p>", "</p>\n").splitlines()
        out("\n".join(difflib.unified_diff(split(current), split(new_text), f"{name} (current)",
                                           f"{name} (from README)", lineterm="")))
        return "diff"
    now = datetime.now(timezone.utc).replace(tzinfo=None).isoformat(sep=" ")
    with db:
        db.execute("UPDATE ndr_core_ndrcorepage SET template_text = ?, last_modified = ? WHERE id = ?",
                   (new_text, now, page_id))
    out(f"{name}: written")
    return "written"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--db", required=True, help="path to the site's db.sqlite3")
    parser.add_argument("--only", nargs="*", help="limit to these benchmarks")
    parser.add_argument("--dry-run", action="store_true", help="print a diff per page, write nothing")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(errors="replace")
    if not os.path.isfile(args.db):
        parser.error(f"{args.db} does not exist")
    db = sqlite3.connect(args.db)
    failed = []
    try:
        for name in card_benchmarks():
            if args.only and name not in args.only:
                continue
            try:
                sync(db, name, args.dry_run)
            except (PageRenderError, OSError, ValueError, sqlite3.Error) as e:
                failed.append(name)
                print(f"{name}: {e} (page left unchanged)", file=sys.stderr)
    finally:
        db.close()
    if failed:
        print(f"not synced: {', '.join(failed)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
