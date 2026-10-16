# Company Lists

This README is a BenchmarkCard (Sokol et al., NeurIPS 2025, arXiv 2410.12974), schema as in evaleval/auto-benchmarkcard v0.2.0.

<!-- Every field stays, in this order; write 'Not specified' when unknown. Fields marked
     (generated) are filled from meta.json and the benchmark's files by
     `python scripts/benchmark_cards.py <name>`; edit meta.json, not the README, to change them. -->

The scoring implementation is in [benchmark.py](benchmark.py), the requested output schema in [dataclass.py](dataclass.py), and the instructions in [prompts/](prompts/).

To run this benchmark, use `python scripts/run_single_test.py --adhoc` from the repository root and select `company_lists`. Provider setup is described in the [root README](../../README.md#quick-start); configured prompts, models and scoring rules are recorded in [benchmarks_tests.csv](../benchmarks_tests.csv). Provider-backed runs incur API charges.

## Benchmark Details

**Name:** Company Lists

**Overview:** Evaluates models' ability to extract company names and locations from printed member lists and trade indexes of the British Chamber of Commerce for Switzerland (1921–1958), across changing layouts, in English and German.

**Data Type:** image

**Domains:**

- history
- economic history
- trade directories

**Languages:**

- English
- German

**Similar Benchmarks:** Not specified

**Resources:**

- https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/company_lists
- https://github.com/RISE-UNIBAS/humanities_data_benchmark/tree/main/benchmarks/company_lists

**Authors:**

- Lea Kasper
- Sorin Marti

## Purpose and Intended Users

**Goal:** Measure how well vision-language models turn printed directory pages with changing layouts (alphabetical directories, thematic trade indexes, one or two columns) into a list of entries with company name and location. The results are meant to guide historians, archivists and digital humanities projects in choosing a model for extracting serial records from printed directories, for example as a first step towards georeferencing firms.

**Audience:**

- AI researchers
- model developers
- industry practitioners

**Tasks:**

- entry segmentation on printed list pages
- extraction of company names and locations

**Limitations:** 15 pages from one publication series, mostly English with German headings and company names in several languages; results do not transfer automatically to other directories. Entries are compared by position, so a skipped, merged or extra entry shifts every later entry and turns correct extractions into mismatches; reading two-column pages in a different order has the same effect. The ground truth also scores `page_id` and `entry_id`, whose expected values are the image basename and `<page_id>-<n>`. The prompt contains a literal `{page_id}` placeholder, but this benchmark does not implement `get_prompt_kwargs`, so the runner does not substitute it. The prompt also shows malformed JSON and describes an array while the schema requires a `ListPage` object. These inconsistencies penalise otherwise correct content extraction. Addresses, telephone numbers and other details on the pages are not extracted.

**Out-of-Scope Uses:**

- drawing conclusions about the firms or persons listed
- evaluating full-text OCR of directory pages
- treating a score as company-name/location accuracy alone, because identifiers are also scored

## Data

**Source:** Trade indexes of the British Chamber of Commerce for Switzerland, issued 1921–1958, held by the Swiss Economic Archives (Schweizerisches Wirtschaftsarchiv), shelf mark UBW Zo 1394, digitised on e-manuscripta: https://doi.org/10.7891/e-manuscripta-174832. The complete record comprises 14 indexes; each lists the chamber's members, first as an alphabetical directory with page references, then as a trade index with full entries (addresses, locations and, in later years, telephone numbers and telegraphic codes).

**Size:** 15 evaluated objects

**Format:** One JPG scan per page, about 1868×2931 px and 350 KB each. The ground truth is one JSON file per page, following the `ListPage` dataclass in `dataclass.py`:

```json
{
  "page_id": "156089_1321092_18",
  "entries": [
    {
      "entry_id": "156089_1321092_18-1",
      "company_name": "Färbereien Schetty, A.-G.",
      "location": "Basle"
    },
    {
      "entry_id": "156089_1321092_18-2",
      "company_name": "G. Kappeler A.-G.",
      "location": "Zofingen"
    }
  ]
}
```

- `page_id`: the image file name without extension
- `entry_id`: `<page_id>-<n>`, numbered in reading order
- `company_name`: the name as printed, including persons listed as firms
- `location`: the location as printed, or `"null"` when the entry has none

The 15 pages hold 353 entries; on three alphabetical pages most entries have no location.

**Annotation:** Ground truths were created by the annotators Lea Kasper and Sorin Marti, with Lea Kasper as domain expert (see Contributors by Role). No annotation guidelines are documented beyond the [prompt file](prompts/prompt.txt).

**Size Breakdown:**

- images files: 15

**Collection Date:** Not specified for benchmark collection or digitisation. Source-document dates: The indexes were issued 1921-1958.

**Contamination Controls:** No held-out private split, training-data audit or other contamination control is documented. Inputs, prompts and ground truths are distributed together in this public repository. Whether any evaluated model saw these materials during training is unknown.

## Methodology

**Methods:**

- zero-shot structured extraction from a single image per request
- structured JSON output requested using the `ListPage` dataclass
- two prompt variants: [prompt.txt](prompts/prompt.txt) describes the source, the two list types and the output fields; [prompt_min.txt](prompts/prompt_min.txt) only asks for valid JSON and leaves the structure to the dataclass

**Metrics:**

- F1 macro (`f1_macro`, used for ranking)
- F1 micro (`f1_micro`)

**Calculation:** A response that is a bare list is wrapped as `entries`. Every terminal field of the JSON is then compared between response and ground truth by its path, for example `entries[3].company_name`; fields under `metadata` are ignored. `null`, `"null"` and missing values count as empty. Values are compared with a rapidfuzz similarity score, and a field is a match at a score of 0.92 or above.

- TP: both have a value and the score is at least 0.92
- FP and FN: both have a value but the score is below 0.92 (the field counts once as each)
- FP: only the response has a value
- FN: only the ground truth has a value

F1 per page is rounded to two decimals. F1 macro averages the per-page F1; F1 micro sums TP, FP and FN over all scored pages before computing F1. With a configured response schema, the shared runner excludes unparseable responses before scoring; neither aggregate includes those pages.

**Interpretation:** Scores range from 0 to 1; higher is better. Macro F1 is the mean of rounded page F1 values; micro F1 pools field counts. Perfect company names and locations with nonmatching IDs score about 0.63 (see Baseline Results), but this is a conditional diagnostic, not a hard maximum: correct IDs can score points too. Compare the descriptive and minimal prompts separately because they supply different instructions.

**Baseline Results:** Model results are available on the [benchmark page](https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/company_lists) and in `results/<date>/<test_id>/` at the repository root. Compare runs with the same prompt, scoring rules and ground-truth revision, and report the number of successfully scored objects alongside the score. No fixed model baseline with a run ID and date is specified here. A diagnostic response that copies every company name and location in the correct order but sets all page and entry IDs to `wrong` scores macro F1 0.628 and micro F1 0.629032 across the 15 pages. This assumes perfect content extraction and is not a hard upper bound.

Observed across models: allowing for the ID fields the model is not given (see Interpretation; the best stored score is 0.61), most models handle the English directory layouts well. Pages that break the entry order, notably two-column German thematic lists, score near zero for many models, because entries are compared by position. Addresses, telephone numbers and product descriptions were left out on purpose, as they are not available for every entry. Company name and location are the fields of analytical interest, as they are the basis for georeferencing the firms and analysing the chamber's membership over time.

**Validation:** The ground truths were created by the annotators and the domain expert listed under Contributors by Role; no separate second check is recorded. Scoring is deterministic; the scorer is covered by the repository's test suite.

**Human Baseline:** Not specified

**Judge Uses LLM:** false

**Judge Num:** Not specified

**Judge Models:** Not specified

**Judge Score Consolidation:** Not specified

**Validity Justification:** Field-level F1 reflects the downstream use: each entry becomes a database record whose name and location must be usable for georeferencing. Not specified beyond that.

## Ethical and Legal Considerations

**Privacy and Anonymity:** The pages list firms; some entries are sole proprietors named as persons (for example `Adolf Bürgin`). The entries give business names and locations only, from printed directories published 1921-1958. Nothing is anonymised.

**Data Licensing:** Public Domain Mark 1.0

**Consent Procedures:** Not specified

**Compliance with Regulations:** The indexes are printed publications held by the Swiss Economic Archives, which publishes the scans on e-manuscripta under the Public Domain Mark 1.0. No separate reuse terms are stated for the ground truths. No ethical review was carried out.

## Beyond the BenchmarkCard

This section is not part of the BenchmarkCard schema and is not exported to `benchmark_card.json`.

<!-- Versions use semantic versioning, newest first, one line each: `- MAJOR.MINOR.PATCH — what
     changed and why`.
     MAJOR: scores before and after are not comparable (ground truths corrected, scoring or
            ranking metric changed, objects added or removed).
     MINOR: something added that leaves existing scores unchanged (e.g. a new prompt variant).
     PATCH: a fix that changes no score (e.g. a better scan of the same image). -->

**Versions:**

- 1.0.0 — initial versioned state

**Contributors by Role:**

- Domain Expert: Lea Kasper
- Data Curator: Lea Kasper
- Annotator: Lea Kasper, Sorin Marti
- Analyst: Lea Kasper
- Engineer: Sorin Marti
