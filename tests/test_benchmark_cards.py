import pytest

import benchmark_cards as bc

TEMPLATE_PATH = bc.os.path.join(bc.BENCHMARKS_DIR, "README_TEMPLATE.md")


def _template():
    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        return f.read()


def test_template_parses():
    parsed = bc.parse(_template())
    assert [key for key, _, _ in bc.ALL_SECTIONS] == list(parsed)


def test_missing_field_is_reported():
    text = _template().replace("**Goal:** Not specified\n", "")
    with pytest.raises(bc.CardError, match="Goal"):
        bc.parse(text)


def test_out_of_order_field_is_reported():
    text = _template().replace("**Goal:** Not specified\n\n", "")
    text = text.replace("**Limitations:**", "**Goal:** Not specified\n\n**Limitations:**")
    with pytest.raises(bc.CardError, match="out-of-order"):
        bc.parse(text)


def test_section_heading_inside_code_fence_is_ignored():
    text = _template().replace(
        "**Calculation:** Not specified",
        "**Calculation:**\n\n```markdown\n## Not a section\n**Goal:** x\n```",
    )
    parsed = bc.parse(text)
    assert "## Not a section" in parsed["methodology"]["calculation"].raw


def test_bold_text_inside_a_field_stays_in_the_field():
    text = _template().replace(
        "**Calculation:** Not specified",
        "**Calculation:**\n\n**Rules:** something\n\nmore",
    )
    raw = bc.parse(text)["methodology"]["calculation"].raw
    assert "**Rules:** something" in raw and "more" in raw


@pytest.mark.parametrize("kind,raw,expected", [
    ("list", "\n\n- a\n- b", ["a", "b"]),
    ("list", " Not specified", ["Not specified"]),
    ("breakdown", "\n\n- image files: 3", {"image files": 3}),
    ("breakdown", " Not specified", "Not specified"),
    ("bool", " false", False),
    ("int", " 2", 2),
    ("text", " a\n\nb", "a\n\nb"),
])
def test_values(kind, raw, expected):
    assert bc._value(kind, raw, "x") == expected


def test_list_field_rejects_prose():
    with pytest.raises(bc.CardError, match="bullet list"):
        bc._value("list", " prose", "x")


def test_render_rewrites_generated_field_only():
    text = _template()
    parsed = bc.parse(text)
    out = bc.render(text, parsed, {("benchmark_details", "languages"): ["German", "French"]})
    assert "**Languages:**\n\n- German\n- French\n\n**Similar Benchmarks:** (generated)" in out
    assert bc.render(out, bc.parse(out), {("benchmark_details", "languages"): ["German", "French"]}) == out


def test_audience_vocabulary_is_enforced():
    text = _template()
    parsed = bc.parse(text)
    values = {(k, f): ("x" if kind == "text" else ["x"] if kind == "list" else "Not specified")
              for k, _, fields in bc.SECTIONS for f, _, kind in fields}
    values[("benchmark_details", "data_type")] = "image"
    values[("purpose_and_intended_users", "audience")] = ["historians"]
    out = bc.render(text, parsed, values)
    with pytest.raises(bc.CardError, match="audience"):
        bc.to_card(bc.parse(out))


@pytest.mark.parametrize("raw", [
    "\n\n- 1.0.0 — initial version",
    "\n\n- 1.1.0 — new prompt variant\n- 1.0.0 — initial version",
])
def test_semantic_versions_pass(raw):
    bc.check_versions(raw)


@pytest.mark.parametrize("raw,match", [
    ("\n\n- 1 — initial version", "MAJOR.MINOR.PATCH"),
    ("\n\n- v1.0 — initial version", "MAJOR.MINOR.PATCH"),
    ("\n\n- 1.0.0", "MAJOR.MINOR.PATCH"),
    ("\n\n- 1.0.0 — a\n- 1.0.0 — b", "listed twice"),
    (" Not specified", "must list"),
])
def test_bad_versions_are_reported(raw, match):
    with pytest.raises(bc.CardError, match=match):
        bc.check_versions(raw)


@pytest.mark.parametrize("names,expected", [
    ([("Serif", "Ina")], "Serif, I."),
    ([("Leonte", "Ana-Maria"), ("Kasper", "Lea Katharina")], "Leonte, A.-M., & Kasper, L. K."),
    ([("A", "Bea"), ("C", "Dan"), ("E", "Fay")], "A, B., C, D., & E, F."),
])
def test_apa_names(names, expected):
    assert bc._apa_names(names) == expected


def test_newest_version_is_the_first_line():
    assert bc.newest_version("\n\n- 2.0.0 — fix\n- 1.0.0 — initial version") == "2.0.0"


CITATION = {
    "authors": [{"family-names": "Serif", "given-names": "Ina", "orcid": "https://orcid.org/0000-0003-2419-4252"}],
    "identifiers": [{"type": "doi", "value": "10.5281/zenodo.1", "description": "All versions"}],
    "references": [{"type": "article", "authors": [{"family-names": "Hindermann", "given-names": "Maximilian"}],
                    "title": "A Paper", "journal": "J", "year": 2026, "volume": 12, "issue": 1,
                    "number": 24, "doi": "10.5334/x"}],
}


def test_how_to_cite():
    meta = {"title": "Fraktur Adverts", "added": "2025-03", "license": "CC BY 4.0",
            "source": {"collection": "UB Basel", "signature": "Not specified", "period": "1731-1762",
                       "url": "https://example.org"}}
    people = [("ina_serif", {"orcid": "0000-0003-2419-4252", "display_name": "Ina Serif"}),
              ("x", {"display_name": "José Luis Losada"})]
    text = bc.how_to_cite(meta, people, "1.1.0", CITATION)
    assert ("> Serif, I., & Losada, J. L. (2025). Fraktur Adverts (benchmark version 1.1.0). "
            "In *RISE Humanities Data Benchmark*. Zenodo. https://doi.org/10.5281/zenodo.1") in text
    assert "> UB Basel, 1731–1762. Licence of the source material: CC BY 4.0. https://example.org" in text
    assert "> Hindermann, M. (2026). A Paper. *J*, *12*(1), 24. https://doi.org/10.5334/x" in text


def test_how_to_cite_needs_added():
    with pytest.raises(bc.CardError, match="added"):
        bc.how_to_cite({"title": "x", "license": "x"}, [], "1.0.0", CITATION)
