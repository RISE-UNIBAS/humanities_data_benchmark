"""Integrity guards for the files the website reads from this repository.

The website (benchmark-frontend) builds its release notes from CHANGELOG.md and its Contribute
page from CONTRIBUTING.md; a release or guide that does not match the format it parses is
silently left off the page, so these guards fail instead.

Rules enforced here:
  1. Every versioned `## ` heading in CHANGELOG.md reads `[vX.Y.Z] - YYYY-MM-DD`, newest first.
  2. CONTRIBUTING.md starts with a `# ` title.
"""
import os
import re

import pytest

pytestmark = pytest.mark.integrity

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _read(*parts):
    with open(os.path.join(REPO_ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def _h2(text):
    """`## ` headings outside code fences."""
    out, fence = [], False
    for line in text.splitlines():
        if line.strip().startswith(("```", "~~~")):
            fence = not fence
        elif not fence and line.startswith("## "):
            out.append(line[3:].strip())
    return out


def test_changelog_releases_are_dated_and_ordered():
    bad, versions = [], []
    for heading in _h2(_read("CHANGELOG.md")):
        if heading.lower().startswith("unreleased") or not heading.startswith("["):
            continue
        m = re.fullmatch(r"\[v(\d+)\.(\d+)\.(\d+)[^\]]*\] - (\d{4}-\d{2}-\d{2})", heading)
        if not m:
            bad.append(f"'{heading}' must read '[vX.Y.Z] - YYYY-MM-DD'")
            continue
        versions.append(tuple(int(g) for g in m.groups()[:3]))
    if versions != sorted(versions, reverse=True):
        bad.append("releases must be newest first")
    assert not bad, f"CHANGELOG.md: {bad}"


def test_contributing_has_a_title():
    assert _read("CONTRIBUTING.md").startswith("# "), "CONTRIBUTING.md must start with a '# ' title"

