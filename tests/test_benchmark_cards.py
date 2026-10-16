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
    ("breakdown", "\n\n- images files: 3", {"images files": 3}),
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
