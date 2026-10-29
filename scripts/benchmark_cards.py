"""Build and check the BenchmarkCard kept in each benchmark's README.md.

A README that contains MARKER is a card. Its `##` sections are the five BenchmarkCard sections
in schema order, followed by `## Beyond the BenchmarkCard`; inside each, every field is a
`**Label:**` line in schema order. List fields are bullet lists. Unknown values are
`Not specified`, never omitted.

Fields in GENERATED are derived from meta.json, the benchmark's files and CITATION.cff and
rewritten by this script; edit meta.json, not the README, to change them. How to Cite cites the
benchmark (its contributors, the year of meta.json `added`, the newest version, the suite's
all-versions DOI), its source record (meta.json `source` and `license`) and the suite's papers.
Versions lists meta.json `versions` from 1.0.0 on; that list, newest first, holds the whole history
(0.y.z before the card: y counts incompatible changes, z compatible ones), each entry with its
date, the commit that made it, the kind of change and a summary. check_meta_versions states the
rules it must follow.
Data Licensing names two licences: meta.json `license` for the source material, and DATA_LICENSE
for everything the benchmark itself creates (ground truth, prompts, annotations).
The card is exported to benchmark_card.json beside the README and validated against
scripts/benchmark_card_schema.py.

Run:
    python scripts/benchmark_cards.py [name ...]          # regenerate (all cards if no name)
    python scripts/benchmark_cards.py --check [name ...]  # exit 1 on drift, write nothing
"""

import argparse
import json
import os
import re
import sys
from collections import namedtuple

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPTS_DIR)
sys.path[:0] = [SCRIPTS_DIR, REPO_ROOT]

from benchmark_base import Benchmark  # noqa: E402
from benchmark_card_schema import (  # noqa: E402
    AUDIENCE_VOCAB, DATA_TYPE_VOCAB, HUMBEN_AUDIENCE_VOCAB, SCHEMA_ID, BenchmarkCard,
)

BENCHMARKS_DIR = os.path.join(REPO_ROOT, "benchmarks")
CONTRIBUTORS_PATH = os.path.join(SCRIPTS_DIR, "data", "contributors.json")
CITATION_PATH = os.path.join(REPO_ROOT, "CITATION.cff")
SUITE_TITLE = "RISE Humanities Data Benchmark"
DATA_LICENSE = "CC BY 4.0"
SITE_URL = "https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/{name}"
REPO_URL = "https://github.com/RISE-UNIBAS/humanities_data_benchmark/tree/main/benchmarks/{name}"

MARKER = (
    "This README is a BenchmarkCard (Sokol et al., NeurIPS 2025, arXiv 2410.12974), "
    "schema as in evaleval/auto-benchmarkcard v0.2.0."
)
NOT_SPECIFIED = "Not specified"

# (key, heading, [(field, label, kind)]); kinds: text, list, breakdown, bool, int.
SECTIONS = [
    ("benchmark_details", "Benchmark Details", [
        ("name", "Name", "text"),
        ("overview", "Overview", "text"),
        ("data_type", "Data Type", "text"),
        ("domains", "Domains", "list"),
        ("languages", "Languages", "list"),
        ("similar_benchmarks", "Similar Benchmarks", "list"),
        ("resources", "Resources", "list"),
        ("authors", "Authors", "list"),
    ]),
    ("purpose_and_intended_users", "Purpose and Intended Users", [
        ("goal", "Goal", "text"),
        ("audience", "Audience", "list"),
        ("tasks", "Tasks", "list"),
        ("limitations", "Limitations", "text"),
        ("out_of_scope_uses", "Out-of-Scope Uses", "list"),
    ]),
    ("data", "Data", [
        ("source", "Source", "text"),
        ("size", "Size", "text"),
        ("format", "Format", "text"),
        ("annotation", "Annotation", "text"),
        ("size_breakdown", "Size Breakdown", "breakdown"),
        ("collection_date", "Collection Date", "text"),
        ("contamination_controls", "Contamination Controls", "text"),
    ]),
    ("methodology", "Methodology", [
        ("methods", "Methods", "list"),
        ("metrics", "Metrics", "list"),
        ("calculation", "Calculation", "text"),
        ("interpretation", "Interpretation", "text"),
        ("baseline_results", "Baseline Results", "text"),
        ("validation", "Validation", "text"),
        ("human_baseline", "Human Baseline", "text"),
        ("judge_uses_llm", "Judge Uses LLM", "bool"),
        ("judge_num", "Judge Num", "int"),
        ("judge_models", "Judge Models", "list"),
        ("judge_score_consolidation", "Judge Score Consolidation", "text"),
        ("validity_justification", "Validity Justification", "text"),
    ]),
    ("ethical_and_legal_considerations", "Ethical and Legal Considerations", [
        ("privacy_and_anonymity", "Privacy and Anonymity", "text"),
        ("data_licensing", "Data Licensing", "text"),
        ("consent_procedures", "Consent Procedures", "text"),
        ("compliance_with_regulations", "Compliance with Regulations", "text"),
    ]),
]
BEYOND = ("beyond", "Beyond the BenchmarkCard", [
    ("versions", "Versions", "list"),
    ("how_to_cite", "How to Cite", "text"),
    ("contributors_by_role", "Contributors by Role", "list"),
])
ALL_SECTIONS = SECTIONS + [BEYOND]

GENERATED = {
    ("benchmark_details", "name"),
    ("benchmark_details", "overview"),
    ("benchmark_details", "data_type"),
    ("benchmark_details", "domains"),
    ("benchmark_details", "languages"),
    ("benchmark_details", "similar_benchmarks"),
    ("benchmark_details", "resources"),
    ("benchmark_details", "authors"),
    ("data", "size"),
    ("data", "size_breakdown"),
    ("ethical_and_legal_considerations", "data_licensing"),
    ("beyond", "versions"),
    ("beyond", "how_to_cite"),
    ("beyond", "contributors_by_role"),
}

LANGUAGES = {
    "de": "German", "el": "Greek", "en": "English", "fi": "Finnish", "fr": "French",
    "it": "Italian", "la": "Latin", "pl": "Polish", "sv": "Swedish",
}

ParsedField = namedtuple("ParsedField", "kind raw start end")


class CardError(ValueError):
    pass


def is_card(readme_text):
    return MARKER in readme_text


def card_benchmarks():
    """Names of benchmarks whose README is a card."""
    names = []
    for name in sorted(os.listdir(BENCHMARKS_DIR)):
        readme = os.path.join(BENCHMARKS_DIR, name, "README.md")
        if os.path.isfile(os.path.join(BENCHMARKS_DIR, name, "meta.json")) and os.path.isfile(readme):
            with open(readme, encoding="utf-8") as f:
                if is_card(f.read()):
                    names.append(name)
    return names


def _split_sections(text):
    """[(heading, body_start, body_end)] for every `## ` heading outside code fences."""
    headings = []
    fence = None
    pos = 0
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if fence:
            if stripped.startswith(fence):
                fence = None
        elif stripped.startswith("```") or stripped.startswith("~~~"):
            fence = stripped[:3]
        elif line.startswith("## "):
            headings.append((line[3:].strip(), pos, pos + len(line)))
        pos += len(line)
    sections = []
    for i, (heading, _, body_start) in enumerate(headings):
        body_end = headings[i + 1][1] if i + 1 < len(headings) else len(text)
        sections.append((heading, body_start, body_end))
    return sections


def parse(text):
    """{section: {field: ParsedField}}. Raises CardError on any structural deviation."""
    if not is_card(text):
        raise CardError("README does not contain the BenchmarkCard reference sentence")
    sections = _split_sections(text)
    found = [h for h, _, _ in sections]
    expected = [heading for _, heading, _ in ALL_SECTIONS]
    if found != expected:
        raise CardError(f"## sections must be exactly {expected}, found {found}")
    parsed = {}
    for (key, heading, fields), (_, body_start, body_end) in zip(ALL_SECTIONS, sections):
        body = text[body_start:body_end]
        matches = []
        cursor = 0
        for field, label, kind in fields:
            m = re.compile(rf"^\*\*{re.escape(label)}:\*\*", re.M).search(body, cursor)
            if not m:
                raise CardError(f"{heading}: missing or out-of-order field **{label}:**")
            matches.append((field, kind, m))
            cursor = m.end()
        parsed[key] = {}
        for i, (field, kind, m) in enumerate(matches):
            end = matches[i + 1][2].start() if i + 1 < len(matches) else len(body)
            raw = body[m.end():end].rstrip()
            parsed[key][field] = ParsedField(kind, raw, body_start + m.end(),
                                             body_start + m.end() + len(raw))
    return parsed


def _value(kind, raw, where):
    value = raw.strip()
    if not value:
        raise CardError(f"{where}: empty; write '{NOT_SPECIFIED}'")
    if kind == "text":
        return value
    if value == NOT_SPECIFIED:
        return [NOT_SPECIFIED] if kind == "list" else NOT_SPECIFIED
    if kind in ("list", "breakdown"):
        lines = [line.strip() for line in value.splitlines() if line.strip()]
        if not all(line.startswith("- ") for line in lines):
            raise CardError(f"{where}: must be a bullet list or '{NOT_SPECIFIED}'")
        items = [line[2:].strip() for line in lines]
        if kind == "list":
            return items
        breakdown = {}
        for item in items:
            m = re.fullmatch(r"(.+?):\s*(\d+)", item)
            if not m:
                raise CardError(f"{where}: items must read '- <subset>: <count>'")
            breakdown[m.group(1)] = int(m.group(2))
        return breakdown
    if kind == "bool":
        if value not in ("true", "false"):
            raise CardError(f"{where}: must be true, false or '{NOT_SPECIFIED}'")
        return value == "true"
    if kind == "int":
        if not value.isdigit():
            raise CardError(f"{where}: must be an integer or '{NOT_SPECIFIED}'")
        return int(value)
    raise AssertionError(kind)


def to_card(parsed):
    """The card dict (schema sections only), validated against the vendored model."""
    card = {}
    for key, heading, fields in SECTIONS:
        card[key] = {field: _value(kind, parsed[key][field].raw, f"{heading} / {label}")
                     for field, label, kind in fields}
    model = BenchmarkCard.model_validate(card)
    problems = []
    data_types = [t.strip() for t in model.benchmark_details.data_type.split(",")]
    problems += [f"data_type '{t}' not in {sorted(DATA_TYPE_VOCAB)}"
                 for t in data_types if t not in DATA_TYPE_VOCAB]
    audiences = AUDIENCE_VOCAB | HUMBEN_AUDIENCE_VOCAB
    problems += [f"audience '{a}' not in {sorted(audiences)}"
                 for a in model.purpose_and_intended_users.audience
                 if a not in audiences and a != NOT_SPECIFIED]
    if problems:
        raise CardError("; ".join(problems))
    return model.model_dump(exclude_none=True)


def format_value(kind, value):
    """The text that follows `**Label:**` in the README."""
    if kind == "list":
        if value == [NOT_SPECIFIED]:
            return " " + NOT_SPECIFIED
        return "\n\n" + "\n".join(f"- {item}" for item in value)
    if kind == "breakdown":
        if isinstance(value, str):
            return " " + value
        return "\n\n" + "\n".join(f"- {k}: {v}" for k, v in value.items())
    if kind == "bool":
        return " " + ("true" if value else "false")
    return f" {value}"


def _load_contributors():
    with open(CONTRIBUTORS_PATH, encoding="utf-8") as f:
        return json.load(f)


def _load_citation():
    import yaml
    with open(CITATION_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _apa_names(names):
    """'A, B., C, D., & E, F.' from (family, given) pairs."""
    def one(family, given):
        initials = " ".join("-".join(p[0] + "." for p in part.split("-")) for part in given.split())
        return f"{family}, {initials}" if initials else family
    parts = [one(f, g) for f, g in names]
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + ", & " + parts[-1]


def _suite_doi(citation):
    for ident in citation.get("identifiers", []):
        if ident.get("type") == "doi" and ident.get("description") == "All versions":
            return ident["value"]
    raise CardError("CITATION.cff has no DOI described as 'All versions'")


def how_to_cite(meta, people, version, citation):
    """The How to Cite text: this benchmark, its source, the suite's papers.

    `people` is [(person id, registry entry)] in author order; names come from the CITATION.cff
    authors (matched by ORCID), else from the display name split at its last space."""
    by_orcid = {a.get("orcid", "").rsplit("/", 1)[-1]: (a["family-names"], a["given-names"])
                for a in citation.get("authors", []) if "family-names" in a}
    names = []
    for _, entry in people:
        if entry.get("orcid") in by_orcid:
            names.append(by_orcid[entry["orcid"]])
        else:
            given, _, family = entry["display_name"].rpartition(" ")
            names.append((family, given))
    if "added" not in meta:
        raise CardError("meta.json lacks 'added' (YYYY-MM, when the benchmark's data was added)")
    year = meta["added"][:4]
    blocks = ["This benchmark:", f"> {_apa_names(names)} ({year}). {meta['title']} "
              f"(benchmark version {version}). In *{SUITE_TITLE}*. Zenodo. "
              f"https://doi.org/{_suite_doi(citation)}"]
    source = meta.get("source", {})
    parts = [source.get(k) for k in ("collection", "signature", "period")
             if source.get(k) and source.get(k) != NOT_SPECIFIED]
    parts = [re.sub(r"^(\d{4})-(\d{4})$", r"\1–\2", part) for part in parts]
    if parts:
        line = f"{', '.join(parts)}. Licence of the source material: {meta['license']}."
        if source.get("url") and source["url"] != NOT_SPECIFIED:
            line += f" {source['url']}"
        blocks += ["Source:", f"> {line}"]
    papers = [r for r in citation.get("references", []) if r.get("type") == "article"]
    if papers:
        quoted = []
        for r in sorted(papers, key=lambda r: (r.get("year", 0), r.get("number", 0))):
            authors = _apa_names([(a["family-names"], a["given-names"]) for a in r["authors"]])
            title = " ".join(r["title"].split())
            quoted.append(f"> {authors} ({r['year']}). {title}. *{r['journal']}*, *{r['volume']}*"
                          f"({r['issue']}), {r['number']}. https://doi.org/{r['doi']}")
        blocks += ["The benchmark suite:", "\n>\n".join(quoted)]
    return "\n\n".join(blocks)


def _basename_pattern(name, directory):
    import importlib.util
    benchmark_file = os.path.join(directory, "benchmark.py")
    spec = importlib.util.spec_from_file_location(f"_card_bench_{name}", benchmark_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    cls = getattr(module, "".join(p.capitalize() for p in name.split("_")))
    return cls.get_basename_pattern(cls.__new__(cls))


def generated_values(name, meta, contributors=None, version="1.0.0", citation=None):
    """{(section, field): value} for every GENERATED field; `version` is the newest in Versions."""
    directory = os.path.join(BENCHMARKS_DIR, name)
    contributors = contributors if contributors is not None else _load_contributors()
    citation = citation if citation is not None else _load_citation()

    missing = [k for k in ("data_type", "license") if k not in meta]
    if missing:
        raise CardError(f"meta.json lacks {missing}")
    codes = meta.get("tags", {}).get("language", [])
    unknown = [c for c in codes if c not in LANGUAGES]
    if unknown:
        raise CardError(f"no language name for {unknown}; add it to LANGUAGES")

    def display(person):
        if person not in contributors:
            raise CardError(f"contributor '{person}' not in scripts/data/contributors.json")
        return contributors[person]["display_name"]

    authors, by_role, people = [], [], []
    for entry in meta.get("contributors", []):
        names = [display(p) for p in entry["contributors"]]
        by_role.append(f"{entry['role']}: {', '.join(names)}")
        authors += [n for n in names if n not in authors]
        people += [(p, contributors[p]) for p in entry["contributors"] if p not in dict(people)]

    pattern = _basename_pattern(name, directory)
    breakdown = {}
    for sub, label in (("images", "image files"), ("texts", "text files")):
        path = os.path.join(directory, sub)
        if os.path.isdir(path):
            count = sum(1 for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)))
            if count:
                breakdown[label] = count
    objects = Benchmark.get_all_basenames(
        [os.path.join(directory, "images"), os.path.join(directory, "texts")],
        page_pattern=pattern,
    )

    values = {
        ("benchmark_details", "name"): meta["title"],
        ("benchmark_details", "overview"): meta["description"],
        ("benchmark_details", "data_type"): meta["data_type"],
        ("benchmark_details", "domains"): meta.get("domains") or [NOT_SPECIFIED],
        ("benchmark_details", "languages"): [LANGUAGES[c] for c in codes] or [NOT_SPECIFIED],
        ("benchmark_details", "similar_benchmarks"): meta.get("similar_benchmarks") or [NOT_SPECIFIED],
        ("benchmark_details", "resources"): [SITE_URL.format(name=name), REPO_URL.format(name=name)],
        ("benchmark_details", "authors"): authors or [NOT_SPECIFIED],
        ("data", "size"): f"{len(objects)} evaluated objects",
        ("data", "size_breakdown"): breakdown or NOT_SPECIFIED,
        ("ethical_and_legal_considerations", "data_licensing"):
            f"Source material: {meta['license']}. Ground truth, prompts and other data created for "
            f"this benchmark: {DATA_LICENSE}.",
        ("beyond", "how_to_cite"): how_to_cite(meta, people, version, citation),
        ("beyond", "contributors_by_role"): by_role or [NOT_SPECIFIED],
    }
    if meta.get("versions"):
        values[("beyond", "versions")] = ["%s — %s" % (v["version"], v["summary"]) for v in meta["versions"]
                                          if not v["version"].startswith("0.")]
    return values


def render(text, parsed, values):
    """README text with every generated field rewritten."""
    edits = []
    for (section, field), value in values.items():
        pf = parsed[section][field]
        edits.append((pf.start, pf.end, format_value(pf.kind, value)))
    for start, end, new in sorted(edits, reverse=True):
        text = text[:start] + new + text[end:]
    return text


VERSION_LINE = re.compile(r"-\s+(\d+)\.(\d+)\.(\d+)\s+—\s+\S")


def newest_version(raw):
    m = VERSION_LINE.match(raw.strip())
    return ".".join(m.groups()) if m else "1.0.0"


def check_versions(raw):
    """Versions is a bullet list of `- MAJOR.MINOR.PATCH — what changed`, each version once."""
    lines = [line.strip() for line in raw.strip().splitlines() if line.strip()]
    if not lines or lines == [NOT_SPECIFIED]:
        raise CardError("Beyond the BenchmarkCard / Versions must list the benchmark's versions")
    seen = set()
    for line in lines:
        m = VERSION_LINE.match(line)
        if not m:
            raise CardError(f"Versions: '{line}' must read '- MAJOR.MINOR.PATCH — what changed'")
        version = tuple(int(g) for g in m.groups())
        if version in seen:
            raise CardError(f"Versions: {'.'.join(m.groups())} is listed twice")
        seen.add(version)


CHANGES = ("initial", "major", "minor", "patch")


def _bumped(older, newer, change):
    """Whether `newer` follows `older` by `change`. Before 1.0.0 the minor place counts incompatible
    changes and the patch place compatible ones; 1.0.0 starts the card's numbering."""
    if change == "initial":
        return newer == (1, 0, 0) and older[0] == 0
    if older[0] == 0:
        if change == "major":
            return newer == (0, older[1] + 1, 0)
        return newer == (0, older[1], older[2] + 1)
    return newer == {"major": (older[0] + 1, 0, 0), "minor": (older[0], older[1] + 1, 0),
                     "patch": (older[0], older[1], older[2] + 1)}[change]


def check_meta_versions(entries):
    """meta.json `versions`: newest first; each entry has version, date, change and summary, and the
    commit that made it once committed (a full hash); the oldest is the initial 0.1.0, or 1.0.0 for
    a benchmark created with its card, and each later one follows by its change; dates do not go
    back; `published_as` (numbers once published for it) only from 1.0.0 on."""
    if not isinstance(entries, list) or not entries:
        raise CardError("meta.json versions must be a non-empty list")
    parsed = []
    for e in entries:
        missing = [k for k in ("version", "date", "change", "summary") if not e.get(k)]
        if missing:
            raise CardError(f"meta.json versions: {e.get('version')} lacks {missing}")
        if not re.fullmatch(r"\d+\.\d+\.\d+", e["version"]) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", e["date"]):
            raise CardError(f"meta.json versions: {e['version']} has a malformed version or date")
        if "commit" in e and not re.fullmatch(r"[0-9a-f]{40}", e["commit"]):
            raise CardError(f"meta.json versions: {e['version']} commit must be a full hash")
        if e["change"] not in CHANGES:
            raise CardError(f"meta.json versions: {e['version']} change must be one of {CHANGES}")
        if e.get("published_as") and e["version"].startswith("0."):
            raise CardError(f"meta.json versions: {e['version']} was never published")
        parsed.append((tuple(int(g) for g in e["version"].split(".")), e))
    parsed.reverse()
    if parsed[0][0] not in ((0, 1, 0), (1, 0, 0)) or parsed[0][1]["change"] != "initial":
        raise CardError("meta.json versions: the oldest entry must be the initial 0.1.0 or 1.0.0")
    for (old, a), (new, b) in zip(parsed, parsed[1:]):
        if not _bumped(old, new, b["change"]):
            raise CardError(f"meta.json versions: {b['version']} does not follow {a['version']} by a {b['change']} change")
        if b["date"] < a["date"]:
            raise CardError(f"meta.json versions: {b['version']} is dated before {a['version']}")


def card_json(card):
    payload = {"benchmark_card": card, "card_info": {"schema": SCHEMA_ID, "source": "README.md"}}
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def build(name, contributors=None):
    """(README text, benchmark_card.json text) as they should be on disk."""
    directory = os.path.join(BENCHMARKS_DIR, name)
    with open(os.path.join(directory, "README.md"), encoding="utf-8") as f:
        readme = f.read()
    with open(os.path.join(directory, "meta.json"), encoding="utf-8") as f:
        meta = json.load(f)
    parsed = parse(readme)
    if meta.get("versions"):
        check_meta_versions(meta["versions"])
        version = meta["versions"][0]["version"]
    else:
        version = newest_version(parsed["beyond"]["versions"].raw)
    readme = render(readme, parsed, generated_values(name, meta, contributors, version))
    parsed = parse(readme)
    card = to_card(parsed)
    metric = meta.get("ranking", {}).get("metric")
    if metric and not any(metric in m for m in card["methodology"]["metrics"]):
        raise CardError(f"Methodology / Metrics must name the ranking metric '{metric}'")
    check_versions(parsed["beyond"]["versions"].raw)
    return readme, card_json(card)


def drift(name, contributors=None):
    """Files of `name` that differ from what build() produces."""
    readme, payload = build(name, contributors)
    directory = os.path.join(BENCHMARKS_DIR, name)
    stale = []
    for filename, expected in (("README.md", readme), ("benchmark_card.json", payload)):
        path = os.path.join(directory, filename)
        current = None
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                current = f.read()
        if current != expected:
            stale.append(filename)
    return stale


def write(name):
    readme, payload = build(name)
    directory = os.path.join(BENCHMARKS_DIR, name)
    with open(os.path.join(directory, "README.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(readme)
    with open(os.path.join(directory, "benchmark_card.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(payload)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("names", nargs="*", help="benchmarks (default: every card)")
    parser.add_argument("--check", action="store_true", help="report drift, write nothing")
    args = parser.parse_args(argv)
    names = args.names or card_benchmarks()
    failed = False
    for name in names:
        try:
            if args.check:
                stale = drift(name)
                if stale:
                    failed = True
                    print(f"{name}: out of date: {', '.join(stale)} "
                          f"(run python scripts/benchmark_cards.py {name})")
            else:
                write(name)
                print(f"{name}: written")
        except (CardError, ValueError) as e:
            failed = True
            print(f"{name}: {e}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
