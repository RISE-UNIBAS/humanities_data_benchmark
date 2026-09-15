"""The files that let the dataset travel without the repository.

`datapackage.json` describes the tables to a machine, the README to a person, and
`CITATION.cff` to a citation tool. All three are generated from the schema and the column
dictionary rather than written by hand, so a column cannot be renamed in one place and
documented in another.

The dataset is CC BY 4.0, which is a separate decision from the software's GPL-3.0: a
dataset is not software, and the plan's §6 requires the terms to be stated rather than
inherited by assumption. The README says what the licence covers and what it does not,
because the export bundles three kinds of content -- the tables this repository derives,
the ground truths it maintains, and stored responses returned by third-party models -- and
a single licence line over all of them would overstate what is being granted.
"""
import json

from scripts.export_dataset import SCHEMA_VERSION
from scripts.export_dataset import columns as C
from scripts.export_dataset.coverage import COLUMNS as COVERAGE_COLUMNS
from scripts.export_dataset.schema import TABLES, UNIQUE_KEYS

DATASET_NAME = "humanities-data-benchmark-results"
DATASET_TITLE = "Humanities Data Benchmark: complete stored results"

SOFTWARE_CONCEPT_DOI = "10.5281/zenodo.16941752"

LICENSE_ID = "CC-BY-4.0"
LICENSE_TITLE = "Creative Commons Attribution 4.0 International"
LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/"

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
        "version": manifest.get("dataset_version") or SCHEMA_VERSION,
        "schema_version": SCHEMA_VERSION,
        # Deliberately not the build time. datapackage.json is hashed into manifest.json,
        # so a wall-clock stamp here would make two builds of identical data differ and
        # destroy the reproducibility claim. The build time lives in manifest.json, which
        # is excluded from its own hash list. Plan §5: keep build time outside the
        # deterministic content identity.
        "created": manifest["data_cutoff"],
        "licenses": [{"name": LICENSE_ID, "title": LICENSE_TITLE, "path": LICENSE_URL}],
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
    lines = ["| Table | Rows | Unit of observation |", "|---|---|---|"]
    grain = {
        "runs": "one stored run directory",
        "requests": "one stored request file",
        "scores_long": "one numeric metric observation, as recorded",
        "rescored_fields": "one field observation from a subsequent scoring pass",
        "metrics": "one metric definition",
    }
    # Only what the manifest reports. A build that found no compare_detail writes no
    # rescored_fields count, and an older manifest may predate a table entirely; neither
    # should stop the documentation being generated.
    for name in ("runs", "requests", "scores_long", "rescored_fields", "metrics"):
        count = manifest["row_counts"].get(name)
        if count is None:
            continue
        lines.append("| `%s` | %s | %s |"
                     % (name, "{:,}".format(count), grain[name]))
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
This dataset provides the stored results of the RISE Humanities Data Benchmark as
relational tables for analysis of model performance, token usage, and estimated costs
on humanities tasks. It includes run metadata, request records, recorded scores,
supplementary field-level evaluations, and JSON payloads documenting both sources.

Release `{version}` · schema `{schema}` · data through {cutoff} · built from source commit `{commit}`

{summary}

## Files and formats

Each table is available in Parquet and CSV, generated from the same typed records.
**Parquet is recommended** because it preserves column types and distinguishes null
values from empty strings without additional parsing rules.

| File or directory | Contents |
|---|---|
| [datapackage.json](datapackage.json) | Table schemas, column definitions, and primary keys |
| [payloads/](payloads/) | Original request and scoring JSON, plus supplementary re-scoring records, in compressed sidecar files |
| [coverage.csv](coverage.csv) | Column completeness and validity statistics |
| [source_manifest.jsonl](source_manifest.jsonl) | Source paths and SHA-256 hashes for the {files:,} files consumed |
| [diagnostics.jsonl](diagnostics.jsonl) | Export issues, severity levels, and handling decisions |
| [manifest.json](manifest.json) | Release and schema versions, build provenance, row counts, and output hashes |
| [examples/](examples/) | Example analysis scripts |
| [CITATION.cff](CITATION.cff) | Dataset citation metadata |
| [CHANGELOG.md](CHANGELOG.md) | Dataset release history |

## Loading Parquet files

The following example uses `pyarrow` and assumes the dataset directory is the working
directory:

```python
import pyarrow.parquet as pq

runs = pq.read_table("runs.parquet")
requests = pq.read_table("requests.parquet")
```

The [Business Letters cost example](examples/business_letters_cost.py) also requires only
`pyarrow`. It estimates cost per correct extraction and reports the coverage supporting
each estimate.

## Scope and missing values

The full export retains every stored run directory and request file, including failed
requests, unscored runs, and runs whose test configuration cannot be resolved. Status
columns distinguish these cases so that inclusion criteria can be applied explicitly.
Completeness refers to the stored archive; attempts that were not saved cannot be recovered.

**Null values represent missing or unavailable information, not zero.** For example, a null
`input_tokens` value indicates that no usable input-token count was recorded. Missing values
should remain distinct from measured zeros when calculating aggregates.

## Keys and joins

- `runs.run_id` is `<test_id>@<date>`. A test run on another date is a different run.
- `requests` joins to `runs` on `run_id`, and its own key is `(run_id, object_id)`.
- `scores_long` joins on `run_id` and, for request- and field-level rows, `object_id`.
  Its `metric_id` joins to `metrics.metric_id`. Select the appropriate `level` before
  joining or aggregating to avoid counting both summary and component observations.
- `rescored_fields` joins to `requests` on `(run_id, object_id)` and is keyed by
  `(run_id, object_id, field_path)`. It has no `metric_id`; its `score` column contains
  the per-field value supplied by the benchmark's scorer.
- `object_id` is a **string**. Leading zeros are significant (`00414956` is an identifier,
  not a number) and some ids contain non-ASCII characters.
- `line` is populated only when an object id is exactly `line_<digits>`. It is presentation
  metadata and never a join key.

## Recorded and recomputed evaluations

`scores_long` preserves numeric observations from the original run records.
`rescored_fields` provides supplementary field-level evaluations produced by a subsequent
scoring pass over stored responses, using the scoring code and ground truths available
at that time. The dataset exporter imports these evaluations from the comparison-detail
files; it does not execute scorers or modify the original results.

In this release, the original records contain field-level detail for four benchmarks.
The supplementary evaluations extend field-level coverage to twelve benchmarks by
processing inputs without stored field detail. This coverage does not imply that every
request has a field-level evaluation. If the comparison-detail files are unavailable,
`rescored_fields` is empty.

The following columns describe the supplementary evaluations:

| Column | Interpretation |
|---|---|
| `score` | Per-field value returned by the scorer; null where no numeric similarity is assigned, including evaluations based on counts |
| `rescored_date` | Date of the subsequent scoring pass, distinct from the original run date and export date |
| `scorer_revision` | Recorded commit that last changed the benchmark's scorer file |
| `ground_truth_revision` | Recorded commit that last changed the benchmark's ground truths |
| `scorer_dirty` | Whether uncommitted scorer or ground-truth changes were reported; true means the revision identifiers do not fully describe the evaluated state |
| `reproduces_stored_score` | Whether the recomputed numeric metrics for the input equal its stored numeric metrics; null when no comparison result is available |

A false `reproduces_stored_score` value identifies a discrepancy, but does not by itself
establish its cause. A true value indicates agreement in the compared metrics, not that
the scorer or ground truths are unchanged. This input-level flag is repeated for each
field belonging to the input.

Recorded and recomputed evaluations represent different evaluation contexts. Analyse them
separately unless the methods and reference data have been shown to be comparable.

## Metrics and aggregation

`scores_long` stores one numeric observation per row at the run, request, or field level.
The `metrics` table defines each observation's meaning, unit, direction, and aggregation
rule. Consult these definitions before comparing or combining values.

- `metric_role` separates a `performance` measurement from a `count` and from a
  `parameter`. `iou_threshold` is a setting the scorer was given; `mean_iou` is what it
  measured. They are not comparable.
- `aggregation` specifies the supported operation: `sum` for counts,
  `mean_over_requests` for applicable performance metrics, `not_summable` for ratios,
  and `not_aggregatable` for parameters.
- `direction` indicates whether higher or lower values represent better performance.
  Character error rate (`cer`) is lower-is-better; it should not be pooled directly with
  higher-is-better similarity scores.
- Metric ids are **scoped by benchmark** because the same name means different things.
  `book_advert_xml` records `fuzzy` on a 0–100 scale; other benchmarks that report `fuzzy`
  use 0–1. Rescaling alone does not establish comparability across different tasks.

F1 scores measure performance rather than the number of correct extractions. Analyses
requiring counts should use the corresponding true-positive metrics where available.

## Cost estimates

Request-level costs are provided in two separate column families:

| Columns | Interpretation |
|---|---|
| `stored_*` | Cost estimates copied from the original request record, using the pricing information available to the runner at the time; absent for many requests |
| `derived_*` | Cost estimates recalculated during export from recorded token counts and dated pricing entries, using a consistent method across the archive |

**Derived costs are estimates, not verified billing amounts.** The exporter selects the
most recent matching price-table entry on or before the run date, with no maximum age.
`pricing_bucket_date` identifies the entry and `pricing_age_days` reports its age at the
time of the run. Gaps in the pricing history therefore affect the reliability of estimates.
The pricing-table version and source hash are recorded in `manifest.json` and
`source_manifest.jsonl` so that calculations can be reproduced.

Historical reconstruction uses dated pricing entries; it does not reconstruct the
evaluation methods used for the original scores. A derived cost reflects the available
price history rather than a verified historical charge, and it may change if that history
is corrected. Supplementary evaluations carry the provenance described in
[Recorded and recomputed evaluations](#recorded-and-recomputed-evaluations).

`cost_provenance` records whether a cost was derived or why it is unavailable. If only
one token count is available, the corresponding cost component is retained and the total
remains null. Missing prices are also represented as null. Some source pricing entries
contain erroneous zeros; a derived cost of `0.0` does not establish that a model was free
to use. Review the recorded input and output prices before interpreting zero costs.

Cost aggregates are **observed subtotals over saved requests**, not a complete record of
expenditure. The runner does not save a request when no answer is returned, and a same-day
rerun may overwrite an earlier result. Saved failures remain included because failed
attempts can incur costs. Report cost coverage alongside any subtotal or efficiency ratio.

## Dates and repeated runs

`date` is the name of the directory in which a run was stored, not an execution timestamp.
`timestamp_raw` preserves the recorded timestamp. `timestamp_utc` is **null for every row
in this release** because the stored timestamps lack UTC offsets and the source machine's
timezone is unknown. Sub-day ordering across machines cannot be established reliably.

The same test can occur on multiple dates, and same-day reruns may have overwritten earlier
results. These observations should not be treated as independent replicates without
further justification. State how repeated runs are selected or combined in an analysis.

## Selection and comparability

The default analytical view selects runs with `hidden = false`. Require an explicit false
value: visibility is null where it could not be resolved, and the treatment of nulls in
inequality filters varies between tools. Hidden and unresolved runs remain in the export;
report their exclusion when presenting results.

`configured_provider` and `configured_model` identify the test configuration.
`response_provider` and `response_model` preserve the identity reported in the stored
response. These values can differ for aliased or routed models. Specify which identity
is used for grouping and comparison.

Configuration and benchmark metadata describe the **export snapshot**, which may differ
from the configuration at execution time. Prompts, ground truths, and scoring code changed
over the archive's history. Stored scores are preserved as recorded; the export does not
reconstruct the historical versions of those evaluation components.

Derived costs use dated pricing entries, as described above, whereas scores retain their
original evaluation context. Historical cost reconstruction does not resolve changes in
models, prompts, or source documents. Comparisons of scores across dates additionally
require attention to changes in ground truths and scoring methods that are not versioned
in the exported records.

## Loading CSV files

CSV readers require explicit handling of missing values and identifier types.

**Nulls and empty strings:** the exported CSV distinguishes an unquoted empty field (null)
from a quoted empty string (`""`). By default, `pandas.read_csv` maps both to `NaN`;
`keep_default_na=False` maps both to an empty string unless additional rules are supplied.
For `scores_long.field_path`, an empty string is a valid field identifier. The build checks
that `field_path` is non-null exactly when `level` is `field`; this rule can be used to
restore empty field identifiers after loading CSV.
Empty strings are also valid in `rescored_fields.field_path`. All rows in that table
represent fields, so empty field identifiers should be preserved when reading its CSV.

**Identifier types:** always load `object_id` as a string. A subset containing only
numeric-looking identifiers can otherwise be inferred as integers, removing significant
leading zeros such as those in `00414956`. CSV quoting does not prevent type inference.

For example, from the dataset directory:

```python
import pandas as pd

requests = pd.read_csv(
    "requests.csv",
    dtype={{"object_id": "string"}},
    keep_default_na=False,
    na_values=[""],
)
```

## Coverage and diagnostics

`coverage.csv` reports row counts, non-null counts, null counts, invalid-value counts, and
the fraction of non-null values for each column in `runs`, `requests`, `scores_long`,
and `rescored_fields`.
Coverage is reported globally and, where the table contains the relevant columns, by
benchmark, configured provider, date, and their combination. `scores_long` has global
coverage only. Null grouping values are retained under the label `<null>`.
`rescored_fields` has global and per-benchmark coverage; its scoring date is recorded
as `rescored_date`, which is not a coverage grouping dimension.

`diagnostics.jsonl` records issues detected during export, including their severity and
the action taken. An empty file indicates that no diagnostic entries were generated.

## Reproducibility

To rebuild this dataset, use the source repository at the commit recorded in
`manifest.json`, with the recorded inputs and dependencies. Run from the repository root:

```console
python -m scripts.export_dataset --dataset-version {version}
```

`source_manifest.jsonl` records a SHA-256 hash for each consumed input. `manifest.json`
records output hashes and build metadata; the manifest itself is excluded from the output
hash list. These records support verification of the files and identification of changes
between builds. Builds using selection filters are marked as partial and are not releases.

## Licence

The project-authored tables, metric dictionary, coverage and manifest files, documentation,
and ground truths are released under [{license_title} ({license_id})]({license_url}).
This licence is separate from the GPL-3.0 licence of the benchmark software.

The payload sidecars also contain responses returned by third-party models, retained as
evidence of model behaviour. The project does not claim authorship of these responses or
grant rights beyond those it holds; reuse may depend on the relevant provider's terms.
Benchmark input documents are not included in this export.

## Citation

Use the citation metadata in [CITATION.cff](CITATION.cff) and identify the dataset version
used in the analysis. Results may change between releases as records are added or corrected.
A dataset DOI has not yet been assigned; it will be added when the dataset is deposited.
""".format(
        title=DATASET_TITLE,
        version=manifest.get("dataset_version") or SCHEMA_VERSION,
        schema=SCHEMA_VERSION,
        cutoff=manifest["data_cutoff"],
        commit=(manifest.get("source_commit") or "unknown")[:9],
        summary=_table_summary(manifest),
        files=inv["files_hashed"],
        counts=counts,
        partial=PARTIAL_BANNER if manifest.get("partial") else "",
        license_id=LICENSE_ID,
        license_title=LICENSE_TITLE,
        license_url=LICENSE_URL,
    )


def changelog(manifest):
    return """# Changelog — dataset

Dataset releases, separate from the software changelog. Figures change between releases
both because results are added and because corrections are made, so an analysis should
cite the exact version it used.

## {version} — unreleased

Initial export. Schema {schema}. Data through {cutoff}, built from source commit `{commit}`.

- {runs:,} runs, {requests:,} requests, {scores:,} metric observations, {metrics} metric
  definitions.
- Per-request cost is exported twice: as the run recorded it, and as derived from recorded
  tokens and the price in force on the run's date.
- `timestamp_utc` is null throughout: every stored timestamp is naive and no source
  timezone is recorded.
- Licensed CC BY 4.0, separately from the software's GPL-3.0. The payload
  sidecars additionally contain third-party model output; see the README.
""".format(
        version=manifest.get("dataset_version") or SCHEMA_VERSION,
        schema=SCHEMA_VERSION,
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
        "version: %s" % (manifest.get("dataset_version") or SCHEMA_VERSION),
        "license: %s" % LICENSE_ID,
    ]

    # `date-released` only when the release date is supplied as explicit metadata. It used
    # to be date.today(), and this file is hashed into the manifest, so two identical
    # builds on different days produced different deterministic content -- invisible to a
    # same-day rebuild comparison, which is how it survived B-D5. The data cutoff is not a
    # substitute: it is when the data ends, not when the release was published.
    released = manifest.get("release_date")
    if released:
        lines.append("date-released: '%s'" % released)

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
        "references:",
        "  - type: software",
        "    title: Humanities Data Benchmark",
        "    doi: %s" % SOFTWARE_CONCEPT_DOI,
        "    notes: the software that produced these results",
    ])
    return "\n".join(lines) + "\n"


# --- the packaged release describes itself, not the build ------------------------
#
# The build directory and the release tree are not the same artifact: the release ships
# Parquet only, gzips the text files and leaves the payloads out. Copying the build's
# datapackage and README into it produced a package whose five declared CSV resources did
# not exist at those paths and whose README promised `payloads/`, an uncompressed source
# manifest and uncompressed diagnostics -- none of them present. A consumer following the
# documentation could not load the thing they had.

def release_datapackage(manifest, packaged_paths, payload_archive=None):
    """A descriptor for what the release tree actually contains.

    `packaged_paths` is the set of paths present after packaging, so every declared
    resource is checked against reality rather than against what the build produced.
    """
    resources = []
    for name in sorted(TABLES):
        path = "%s.parquet" % name
        if path not in packaged_paths:
            continue
        resources.append({
            "name": name,
            "path": path,
            "format": "parquet",
            "mediatype": "application/vnd.apache.parquet",
            "schema": {
                "fields": [_field(name, f.name, f.type) for f in TABLES[name]],
                "primaryKey": list(UNIQUE_KEYS[name]),
            },
        })

    if "coverage.csv.gz" in packaged_paths:
        resources.append({
            "name": "coverage",
            "path": "coverage.csv.gz",
            "format": "csv",
            "mediatype": "text/csv",
            "compression": "gz",
            "encoding": "utf-8",
            "schema": {"fields": [
                {"name": c,
                 "type": "string" if c in ("table", "column", "group_dimension",
                                           "group_value") else "number",
                 "description": C.COVERAGE[c]}
                for c in COVERAGE_COLUMNS]},
        })

    package = {
        "profile": "tabular-data-package",
        "name": DATASET_NAME,
        "title": DATASET_TITLE,
        "description": (
            "Every stored result of the Humanities Data Benchmark, as joinable Parquet "
            "tables with a metric dictionary. Nothing is filtered: runs that failed, were "
            "never scored, or whose configuration is no longer known are rows carrying a "
            "status, not omissions."),
        "version": manifest.get("dataset_version") or SCHEMA_VERSION,
        "schema_version": SCHEMA_VERSION,
        "created": manifest["data_cutoff"],
        "licenses": [{"name": LICENSE_ID, "title": LICENSE_TITLE, "path": LICENSE_URL}],
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
            "note": ("source commit %s; source_manifest.jsonl.gz carries a SHA-256 of "
                     "every file consumed"
                     % (manifest.get("source_commit") or "unknown")),
        }],
    }
    if payload_archive:
        package["relatedIdentifiers"].append({
            "relationType": "hasPart",
            "relatedIdentifier": payload_archive,
            "relatedIdentifierType": "other",
            "note": "complete stored request and scoring JSON, distributed separately",
        })
    return package


def release_readme(manifest, packaged_paths, payload_archive=None):
    """The README that ships with the release tree.

    Differs from the build's in what it can promise: Parquet only, text files gzipped,
    payloads elsewhere. The analytical guidance is the same, because the data is.
    """
    full = readme(manifest)
    guidance = full[full.index("## Scope and missing values"):]
    guidance = guidance[:guidance.index("## Loading CSV files")] + \
        guidance[guidance.index("## Coverage and diagnostics"):]

    payload_line = (
        "The payload sidecars -- the complete original request and scoring JSON -- are "
        "**not** in this package. They are %s, distributed separately because they are "
        "four fifths of the artifact by volume and are mostly third-party model output."
        % (("`%s`" % payload_archive) if payload_archive else
           "a separate archive named in the deposit"))

    listing = "\n".join("- `%s`" % p for p in sorted(packaged_paths))

    return """# {title}

Release `{version}` · schema `{schema}` · data through {cutoff} · source commit `{commit}`

Every stored result of the Humanities Data Benchmark, as joinable **Parquet** tables.

{summary}

## What is in this package

{listing}

Text files are gzipped so that every file clears the size limits of the repository this
release is committed to; `packaging.json` maps each one back to the name and SHA-256 the
build recorded, so it can be reconciled with `manifest.json`.

{payload_line}

## Reading it

```python
import pyarrow.parquet as pq
runs = pq.read_table("runs.parquet").to_pylist()
```

`pyarrow` is the only dependency. `examples/business_letters_cost.py` is a worked analysis
that runs against this directory as it stands.

{guidance}""".format(
        title=DATASET_TITLE,
        version=manifest.get("dataset_version") or SCHEMA_VERSION,
        schema=SCHEMA_VERSION,
        cutoff=manifest["data_cutoff"],
        commit=(manifest.get("source_commit") or "unknown")[:9],
        summary=_table_summary(manifest),
        listing=listing,
        payload_line=payload_line,
        guidance=guidance,
    )
