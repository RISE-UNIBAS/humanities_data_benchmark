"""Site data integrity guards.

The website's widgets read only the folder that scripts/ndr_export/generate_site_data.py builds
(collected_results/site/). Parts of it come from this repository; a release or guide that does not
match the format the widgets parse is silently left off the page, so these guards fail instead.
news.md and about.md live in the benchmark-frontend repository; the generator checks news.md at
deploy, and its check is tested here.

Rules enforced here:
  1. Every versioned `## ` heading in CHANGELOG.md reads `[vX.Y.Z] - YYYY-MM-DD`, newest first.
  2. CONTRIBUTING.md starts with a `# ` title.
  3. The news check accepts `## YYYY-MM-DD — Title`, newest first, and reports anything else.
"""
import os
import re

import pytest

from scripts.ndr_export.generate_site_data import check_news

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


def test_news_check_accepts_the_format():
    news = "# News\n\n## 2026-10-16 — Second\n\nText.\n\n## 2026-09-11 — First\n\n```\n## not a post\n```\n"
    assert check_news(news) == []


@pytest.mark.parametrize("news,problem", [
    ("## 2026-10-16 - Hyphen instead of em dash\n", "must read"),
    ("## 16.10.2026 — Swiss date\n", "must read"),
    ("## 2026-13-01 — No such month\n", "invalid date"),
    ("## 2026-09-11 — Old\n\n## 2026-10-16 — New\n", "newest first"),
])
def test_news_check_reports_problems(news, problem):
    assert any(problem in p for p in check_news(news))
