# Company Lists

This README is a BenchmarkCard (Sokol et al., NeurIPS 2025, arXiv 2410.12974), schema as in evaleval/auto-benchmarkcard v0.2.0.

<!-- Every field stays, in this order; write 'Not specified' when unknown. Fields marked
     (generated) are filled from meta.json and the benchmark's files by
     `python scripts/benchmark_cards.py <name>`; edit meta.json, not the README, to change them. -->

The scorer is in [benchmark.py](benchmark.py), the requested output schema in [dataclass.py](dataclass.py) and the prompts in [prompts/](prompts/).

To run this benchmark, use `python scripts/run_single_test.py --adhoc` from the repository root and select `company_lists`. Provider setup is described in the [root README](../../README.md#quick-start); configured prompts, models and scoring rules are recorded in [benchmarks_tests.csv](../benchmarks_tests.csv). Provider-backed runs incur API charges.

## Benchmark Details

**Name:** Company Lists

**Overview:** Models extract company names and locations from printed member lists and trade indexes of the British Chamber of Commerce for Switzerland, 1921–1958, held by the Swiss Economic Archives; the pages change layout and are in English and German.

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

**Limitations:** The 15 pages come from one publication series, mostly in English with German headings and company names in several languages; results do not transfer to other directories. Addresses, telephone numbers and product descriptions are not extracted, because not every entry has them. Entries are compared by position (see Calculation), so a skipped, merged or extra entry shifts every later entry and turns correct extractions into mismatches; reading a two-column page in a different order has the same effect. The ground truth also contains `page_id` and `entry_id`, whose expected values are the image basename and `<page_id>-<n>`. Both prompts contain a literal `{page_id}` placeholder that the benchmark does not fill (it implements no `get_prompt_kwargs`), so the model is never given these values. `prompt.txt` also shows malformed JSON and describes an array, while the schema requires a `ListPage` object. These inconsistencies penalise otherwise correct content extraction.

**Out-of-Scope Uses:**

- drawing conclusions about the firms or persons listed
- evaluating full-text OCR of directory pages
- treating a score as company-name/location accuracy alone, because identifiers are also scored

## Data

**Source:** Trade indexes of the British Chamber of Commerce for Switzerland, issued 1921–1958, held by the Swiss Economic Archives (Schweizerisches Wirtschaftsarchiv), shelf mark UBW Zo 1394, digitised on e-manuscripta: https://doi.org/10.7891/e-manuscripta-174832. The complete record comprises 14 indexes; each lists the chamber's members, first as an alphabetical directory with page references, then as a trade index with full entries (addresses, locations and, in later years, telephone numbers and telegraphic codes).

**Size:** 15 evaluated objects

**Format:** One JPG scan per page, between 1636×2422 and 1868×2931 px and about 290 KB on average. The ground truth is one JSON file per page, following the `ListPage` dataclass in `dataclass.py`:

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

**Annotation:** The annotators Lea Kasper and Sorin Marti created the ground truth, with Lea Kasper as domain expert. No annotation guidelines are recorded beyond the [prompt file](prompts/prompt.txt).

**Size Breakdown:**

- image files: 15

**Collection Date:** Source documents: 1921–1958. Added to the benchmark: October 2025.

**Contamination Controls:** None. The scans, prompts and ground truth have been public in this repository since October 2025.

## Methodology

**Methods:**

- zero-shot structured extraction from a single image per request, temperature 0.5
- structured JSON output requested using the `ListPage` dataclass
- two prompt variants: [prompt.txt](prompts/prompt.txt) describes the source, the two list types and the output fields; [prompt_min.txt](prompts/prompt_min.txt) only asks for valid JSON and leaves the structure to the dataclass
- output cap: the repository default of 16,384 tokens per request

**Metrics:**

- F1 macro (`f1_macro`, used for ranking)
- F1 micro (`f1_micro`)

**Calculation:** A response that is a bare list is wrapped as `entries`. Every terminal field of the JSON is then compared between response and ground truth by its path, for example `entries[3].company_name`; fields under `metadata` are ignored. `null`, `"null"` and missing values count as empty. Values are compared with the rapidfuzz `fuzz.ratio` similarity scaled to 0–1; a field is a match at 0.92 or above.

- TP: both have a value and the score is at least 0.92
- FP and FN: both have a value but the score is below 0.92 (the field counts once as each)
- FP: only the response has a value
- FN: only the ground truth has a value

F1 per page is rounded to two decimals. F1 macro averages the rounded per-page F1; F1 micro sums TP, FP and FN over all scored pages before computing F1 and is not rounded. A response that does not parse is not scored and enters neither aggregate.

**Interpretation:** Scores range from 0 to 1; higher is better. The identifier fields are scored but their values are never given to the model, so perfect company names and locations with non-matching identifiers score about 0.63 (see Baseline Results); this is not a hard maximum, as a model that produces the expected identifiers scores higher. Compare the descriptive and minimal prompts separately, because they give different instructions.

**Baseline Results:** Results are on the [benchmark page](https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/company_lists) and in `results/<date>/<test_id>/` at the repository root. No fixed baseline is recorded. Compare runs only with the same prompt, rules and ground-truth revision, and report the number of scored pages with the score. A diagnostic response that copies every company name and location in the correct order but sets all page and entry identifiers to `wrong` scores macro F1 0.628 and micro F1 0.629032 across the 15 pages.

Observed across models: allowing for the identifier fields the model is not given (see Interpretation; the best stored score is 0.61), most models handle the English directory layouts well. Pages that break the entry order, notably two-column German thematic lists, score near zero for many models, because entries are compared by position.

**Validation:** The ground truth was created by the annotators and the domain expert named under Annotation; no separate check is recorded. Scoring is deterministic; the scorer is covered by the repository's test suite.

**Human Baseline:** Not specified

**Judge Uses LLM:** false

**Judge Num:** Not specified

**Judge Models:** Not specified

**Judge Score Consolidation:** Not specified

**Validity Justification:** Field-level F1 reflects the downstream use: each entry becomes a database record whose name and location must be usable for georeferencing.

## Ethical and Legal Considerations

**Privacy and Anonymity:** The pages list firms; some entries are sole proprietors named as persons (for example `Adolf Bürgin`). The entries give business names and locations only, from printed directories published 1921–1958. Nothing is anonymised.

**Data Licensing:** Source material: Public Domain Mark 1.0. Ground truth, prompts and other data created for this benchmark: CC BY 4.0.

**Consent Procedures:** Not specified

**Compliance with Regulations:** The indexes are printed publications held by the Swiss Economic Archives, which publishes the scans on e-manuscripta under the Public Domain Mark 1.0. No ethical review was carried out.

## Beyond the BenchmarkCard

This section is not part of the BenchmarkCard schema and is not exported to `benchmark_card.json`.

<!-- Versions use semantic versioning, newest first, one line each: `- MAJOR.MINOR.PATCH — what
     changed and why`.
     MAJOR: scores before and after are not comparable (ground truth corrected, scoring or
            ranking metric changed, objects added or removed).
     MINOR: something added that leaves existing scores unchanged (e.g. a new prompt variant).
     PATCH: a fix that changes no score (e.g. a better scan of the same image). -->

**Versions:**

- 1.0.0 — initial versioned state

**How to Cite:** This benchmark:

> Kasper, L., & Marti, S. (2025). Company Lists (benchmark version 1.0.0). In *RISE Humanities Data Benchmark*. Zenodo. https://doi.org/10.5281/zenodo.16941752

Source:

> Schweizerisches Wirtschaftsarchiv, UBW Zo 1394, 1921–1958. Licence of the source material: Public Domain Mark 1.0. https://doi.org/10.7891/e-manuscripta-174832

The benchmark suite:

> Hindermann, M., Marti, S., Kasper, L. K., & Bosse, A. (2026). The RISE Humanities Data Benchmark: A Framework for Evaluating Large Language Models for Humanities Tasks. *Journal of Open Humanities Data*, *12*(1), 24. https://doi.org/10.5334/johd.481
>
> Hindermann, M., Kasper, L. K., Marti, S., & Bosse, A. (2026). From Experiments to Epistemic Practice: The RISE Humanities Data Benchmark. *Journal of Open Humanities Data*, *12*(1), 38. https://doi.org/10.5334/johd.470

**Contributors by Role:**

- Domain Expert: Lea Kasper
- Data Curator: Lea Kasper
- Annotator: Lea Kasper, Sorin Marti
- Analyst: Lea Kasper
- Engineer: Sorin Marti
