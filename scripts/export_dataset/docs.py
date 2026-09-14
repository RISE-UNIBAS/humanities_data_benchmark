"""The files that let the dataset travel without the repository.

`datapackage.json` describes the tables to a machine, the README to a person, and
`CITATION.cff` to a citation tool. All three are generated from the schema and the column
dictionary rather than written by hand, so a column cannot be renamed in one place and
documented in another.

One thing is deliberately absent: a licence. The software is GPL-3.0, but a dataset is not
software, and whether the stored model responses and the ground truths can carry the same
terms has not been decided. The plan's §6 is explicit that unresolved terms are release
preparation work, not something to assume, so the README says the licence is undetermined
and the build does not invent one. That is a release blocker, and it is stated as one.
"""
import json
from datetime import date

from scripts.export_dataset import SCHEMA_VERSION
from scripts.export_dataset import columns as C
from scripts.export_dataset.coverage import COLUMNS as COVERAGE_COLUMNS
from scripts.export_dataset.schema import TABLES, UNIQUE_KEYS

DATASET_NAME = "humanities-data-benchmark-results"
DATASET_TITLE = "Humanities Data Benchmark: complete stored results"

SOFTWARE_CONCEPT_DOI = "10.5281/zenodo.16941752"

_ARROW_TO_FRICTIONLESS = {
    "string": "string",
    "int64": "integer",
    "double": "number",
    "bool": "boolean",
}


def _field(table, name, arrow_type):
    return {
        "name": name,
        "type": _ARROW_TO_FRICTIONLESS.get(str(arrow_type), "any"),
        "description": C.BY_TABLE[table][name],
    }


def datapackage(manifest):
    resources = []
    for name in sorted(TABLES):
        schema = TABLES[name]
        resources.append({
            "name": name,
            "path": "%s.csv" % name,
            "alternate_paths": ["%s.parquet" % name],
            "format": "csv",
            "mediatype": "text/csv",
            "encoding": "utf-8",
            "dialect": {"delimiter": ",", "lineTerminator": "\n",
                        "quoteChar": '"', "header": True},
            "schema": {
                "fields": [_field(name, f.name, f.type) for f in schema],
                "primaryKey": list(UNIQUE_KEYS[name]),
            },
        })

    resources.append({
        "name": "coverage",
        "path": "coverage.csv",
        "format": "csv",
        "mediatype": "text/csv",
        "encoding": "utf-8",
        "schema": {"fields": [{"name": c, "type": "string" if c in
                               ("table", "column", "group_dimension", "group_value")
                               else "number", "description": C.COVERAGE[c]}
                              for c in COVERAGE_COLUMNS]},
    })

    return {
        "profile": "tabular-data-package",
        "name": DATASET_NAME,
        "title": DATASET_TITLE,
        "description": (
            "Every stored result of the Humanities Data Benchmark, as three joinable "
            "tables with a metric dictionary and lossless payload sidecars. Nothing is "
            "filtered: runs that failed, were never scored, or whose configuration is no "
            "longer known are rows carrying a status, not omissions."),
        "version": SCHEMA_VERSION,
        "created": manifest["build_started_utc"],
        "licenses": [],
        "resources": resources,
        "keywords": ["benchmark", "LLM", "digital humanities", "OCR", "HTR",
                     "information extraction"],
        "relatedIdentifiers": [{
            "relationType": "isSupplementTo",
            "relatedIdentifier": SOFTWARE_CONCEPT_DOI,
            "relatedIdentifierType": "DOI",
            "note": "concept DOI of the software that produced these results",
        }],
        "sources": [{
            "title": "Humanities Data Benchmark stored results",
            "path": "results/",
            "note": ("source commit %s; see source_manifest.jsonl for a SHA-256 of every "
                     "file consumed" % (manifest.get("source_commit") or "unknown")),
        }],
    }


def _table_summary(manifest):
    lines = ["| Table | Rows | Grain |", "|---|---|---|"]
    grain = {
        "runs": "one stored run directory",
        "requests": "one stored request file",
        "scores_long": "one numeric metric observation",
        "metrics": "one metric definition",
    }
    for name in ("runs", "requests", "scores_long", "metrics"):
        lines.append("| `%s` | %s | %s |"
                     % (name, "{:,}".format(manifest["row_counts"][name]), grain[name]))
    return "\n".join(lines)


PARTIAL_BANNER = """
> **This is a partial build and is not a release.** It was produced with a `--date`,
> `--benchmark` or `--limit` filter, so the tables below cover only the selected runs while
> the inventory figures describe the whole source archive. `manifest.json` records
> `partial: true` and the filters used. Do not cite or deposit it.
"""


def readme(manifest):
    counts = manifest["row_counts"]
    inv = manifest["inventory"]
    return """# {title}
{partial}
Every stored result of the Humanities Data Benchmark, as joinable tables.

Release `{version}` · data through {cutoff} · built from source commit `{commit}`

{summary}

Alongside them: `metrics.csv` defining every number, `payloads/` holding the complete
original JSON, `coverage.csv` measuring how much of each column is populated,
`source_manifest.jsonl` hashing every one of the {files:,} files consumed,
`diagnostics.jsonl` listing anything the exporter could not handle, and `manifest.json`
recording versions and output hashes.

Each table is written twice, as Parquet and as CSV, from the same typed rows. **Parquet is
the lossless copy** — read that one unless you have a reason not to, for the reason given
under "Loading the CSV" below.

## The one thing to understand first

Nothing is filtered. A run whose configuration is no longer known, a run that was never
scored, a request that failed — all are rows, each carrying a status column saying which.
This is deliberate: an analyst cannot tell a filtered-out row from a row that never
existed, so an archive that filters is an archive that misleads.

The corollary is that **null means "not recorded" and never zero**. A request with no
`input_tokens` did not use zero tokens; nothing was written down. Aggregate accordingly.

## Keys and joins

- `runs.run_id` is `<test_id>@<date>`. A test run on another date is a different run.
- `requests` joins to `runs` on `run_id`, and its own key is `(run_id, object_id)`.
- `scores_long` joins on `run_id` and, for request- and field-level rows, `object_id`.
  Its `metric_id` joins to `metrics`.
- `object_id` is a **string**. Leading zeros are significant (`00414956` is an identifier,
  not a number) and some ids contain non-ASCII characters.
- `line` is populated only when an object id is exactly `line_<digits>`. It is presentation
  metadata and never a join key.

## Reading the metrics

`scores_long` is deliberately shapeless — six columns, one row per observation — which
makes every number look alike. `metrics.csv` is what stops you averaging a true-positive
count with an F1 score. Consult it before aggregating anything.

- `metric_role` separates a `performance` measurement from a `count` and from a
  `parameter`. `iou_threshold` is a setting the scorer was given; `mean_iou` is what it
  measured. They are not comparable.
- `aggregation` says what combining is legitimate: `sum` for counts, `not_summable` for a
  ratio the scorer already averaged, `not_aggregatable` for a parameter.
- `direction` matters: `cer` is an error rate, so lower is better, and pooling it with
  similarity scores without inverting it produces nonsense.
- Metric ids are **scoped by benchmark** because the same name means different things.
  `book_advert_xml` records `fuzzy` on a 0–100 scale; every other benchmark records 0–1.

An F1 score is not a count of correct extractions. If you need a count, use the
true-positive metrics — see `examples/business_letters_cost.py`, which does exactly that.

## Costs

Two column families, answering different questions, and neither overwrites the other.

- `stored_*` is what the run recorded at the time, verbatim. Costed against whatever price
  table was live then, which varied across the corpus, and absent for many requests.
- `derived_*` is recomputed here from the recorded tokens and the price in force on the
  run's own date. Uniform and reproducible, and it covers more requests.

**A derived cost is not what was charged.** It is what the price table says the run would
have cost at that date. It changes if the table is corrected, which is why the table's
version and hash are recorded in `manifest.json` and `source_manifest.jsonl`.

Where a model has no real price in the table, the derived cost is null and
`cost_provenance` says why. Note the converse trap: at least one model resolves to a price
of exactly zero because of a bad source, so a derived cost of `0.0` may mean "unpriced"
rather than "free". Check `pricing_input_price_per_million` before concluding a model is
cheap.

Spend figures are **observed subtotals**, never totals. The runner saves no request when an
answer is empty, and a same-day re-run overwrites the earlier one, so the stored requests
are observations rather than a complete log of attempts. Failed requests cost money and are
included; excluding them would understate spend.

## Time

`date` is the directory a run was stored under, not a timestamp.

`timestamp_utc` is **null for every row in this release**. Every stored timestamp is naive
local time with no offset, and the machine that produced it is not recorded, so converting
would mean inventing a timezone. Use `timestamp_raw` and `date`, and treat sub-day ordering
across machines as unknown.

Runs repeat: the same test appears on several dates, and a same-day re-run may have
overwritten an earlier one. Rows are **not** independent replicates. Decide explicitly
whether you want the latest run, a mean, or all of them.

## Which rows to analyse

The default analytical view is `hidden = false`. Filter on that rather than `hidden != true`
— `hidden` is null where visibility could not be resolved, and null is not a licence to
include. Hidden and unknown rows stay in the export; report what you excluded.

`configured_provider`/`configured_model` come from the test configuration; `response_provider`/
`response_model` come from what the stored response says actually served the request. They
disagree for aliased and routed models. Group by whichever you mean, and say which.

All configuration and benchmark metadata describes the **export snapshot**, not necessarily
the state at run time. Prompts, ground truths and scorers changed over the corpus. This
export does not recover their historical state, and comparisons across distant dates mix
those changes with whatever else you are measuring.

## Loading the CSV

Use Parquet if you can. If you must use the CSV, `pandas.read_csv` will get two things
wrong: it turns leading-zero object ids into integers, and it cannot distinguish a null
from an empty string. The second matters in exactly one place — `scores_long.field_path` is
legitimately the empty string for several thousand field observations — and the rule that
recovers it is that **`field_path` is non-null exactly when `level` is `field`**.

```python
import pandas as pd
requests = pd.read_csv("requests.csv", dtype={{"object_id": "string"}},
                       keep_default_na=False, na_values=[""])
```

`examples/business_letters_cost.py` reads Parquet and needs only `pyarrow`.

## Coverage and diagnostics

`coverage.csv` gives, for every table and column, the non-null count and its denominator —
globally, per benchmark, per provider, per date, and per benchmark/provider/date triple.
Groups whose grouping value is itself null are kept under `<null>` rather than dropped.

`diagnostics.jsonl` lists everything the exporter could not handle, with a severity and what
it did instead. An empty file means nothing was encountered, not that nothing was checked.

## Reproducing this

```
python -m scripts.export_dataset
```

from the source repository at the commit recorded in `manifest.json`. The build hashes every
input into `source_manifest.jsonl` and every output into `manifest.json`, so a rebuild that
differs can be traced to an input or to the exporter.

## Licence

**Not yet determined.** The software that produced these results is GPL-3.0, but a dataset
is not software, and the terms covering the stored model responses and the ground truths
have not been settled. Do not assume the software licence applies. This is a release
blocker and is recorded as one rather than resolved by assumption.

## Citation

See `CITATION.cff`. This dataset has no DOI yet; it is minted at deposit. Cite the exact
version — figures change between releases as results are added and as corrections are made.
""".format(
        title=DATASET_TITLE,
        version=SCHEMA_VERSION,
        cutoff=manifest["data_cutoff"],
        commit=(manifest.get("source_commit") or "unknown")[:9],
        summary=_table_summary(manifest),
        files=inv["files_hashed"],
        counts=counts,
        partial=PARTIAL_BANNER if manifest.get("partial") else "",
    )


def changelog(manifest):
    return """# Changelog — dataset

Dataset releases, separate from the software changelog. Figures change between releases
both because results are added and because corrections are made, so an analysis should
cite the exact version it used.

## {version} — unreleased

Initial export. Data through {cutoff}, built from source commit `{commit}`.

- {runs:,} runs, {requests:,} requests, {scores:,} metric observations, {metrics} metric
  definitions.
- Per-request cost is exported twice: as the run recorded it, and as derived from recorded
  tokens and the price in force on the run's date.
- `timestamp_utc` is null throughout: every stored timestamp is naive and no source
  timezone is recorded.
- Licence not yet determined; see the README. Not depositable until it is.
""".format(
        version=SCHEMA_VERSION,
        cutoff=manifest["data_cutoff"],
        commit=(manifest.get("source_commit") or "unknown")[:9],
        runs=manifest["row_counts"]["runs"],
        requests=manifest["row_counts"]["requests"],
        scores=manifest["row_counts"]["scores_long"],
        metrics=manifest["row_counts"]["metrics"],
    )


def citation(manifest, software_citation):
    """Dataset CITATION.cff, reusing the software's authors.

    No DOI: one is minted at deposit, and inventing a placeholder that looks like an
    identifier is worse than having none. No licence either -- see the module docstring.
    """
    lines = [
        "cff-version: 1.2.0",
        "message: If you use this dataset, please cite it using these metadata.",
        "type: dataset",
        "title: %s" % json.dumps(DATASET_TITLE),
        "abstract: >-",
        "  Every stored result of the Humanities Data Benchmark as joinable tables:",
        "  %s runs, %s requests and %s metric observations covering data through %s."
        % ("{:,}".format(manifest["row_counts"]["runs"]),
           "{:,}".format(manifest["row_counts"]["requests"]),
           "{:,}".format(manifest["row_counts"]["scores_long"]),
           manifest["data_cutoff"]),
        "  Nothing is filtered: unscored, failed and unresolved runs are rows carrying a",
        "  status rather than omissions.",
        "version: %s" % SCHEMA_VERSION,
        "date-released: '%s'" % date.today().isoformat(),
    ]

    authors = (software_citation or {}).get("authors")
    if authors:
        lines.append("authors:")
        for author in authors:
            entry = []
            for key in ("family-names", "given-names", "orcid", "affiliation"):
                if author.get(key):
                    entry.append("    %s: %s" % (key, json.dumps(author[key])))
            if entry:
                entry[0] = "  -" + entry[0][3:]
                lines.extend(entry)

    lines.extend([
        "keywords:",
        "  - benchmark",
        "  - LLM",
        "  - digital humanities",
        "identifiers: []   # version DOI is added at deposit",
        "# license: intentionally absent -- not yet determined, see README.md",
        "references:",
        "  - type: software",
        "    title: Humanities Data Benchmark",
        "    doi: %s" % SOFTWARE_CONCEPT_DOI,
        "    notes: the software that produced these results",
    ])
    return "\n".join(lines) + "\n"
