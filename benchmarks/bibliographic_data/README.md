# Bibliographic Data

This README is a BenchmarkCard (Sokol et al., NeurIPS 2025, arXiv 2410.12974), schema as in evaleval/auto-benchmarkcard v0.2.0.

<!-- Every field stays, in this order; write 'Not specified' when unknown. Fields marked
     (generated) are filled from meta.json and the benchmark's files by
     `python scripts/benchmark_cards.py <name>`; edit meta.json, not the README, to change them. -->

The scoring implementation is in [benchmark.py](benchmark.py), the requested output schema in [dataclass.py](dataclass.py), and the instructions in [prompts/](prompts/).

To run this benchmark, use `python scripts/run_single_test.py --adhoc` from the repository root and select `bibliographic_data`. Provider setup is described in the [root README](../../README.md#quick-start); configured prompts, models and scoring rules are recorded in [benchmarks_tests.csv](../benchmarks_tests.csv). Provider-backed runs incur API charges.

## Benchmark Details

**Name:** Bibliographic Data

**Overview:** Tests models on extracting structured entries (author, title, publisher, place, year, pages, cross-references) from the pages of a printed 1961 bibliography of the philosophy of history.

**Data Type:** image

**Domains:**

- bibliography
- library science
- philosophy of history

**Languages:**

- English

**Similar Benchmarks:** Not specified

**Resources:**

- https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/bibliographic_data
- https://github.com/RISE-UNIBAS/humanities_data_benchmark/tree/main/benchmarks/bibliographic_data

**Authors:**

- Pema Frick
- Sven Burkhardt
- Sorin Marti

## Purpose and Intended Users

**Goal:** Measure how well vision-language models turn a printed scholarly bibliography page into structured, citation-style records (CSL-like JSON): splitting the page into entries, classifying each entry, separating authors into family and given names, and recording publication details, cross-references between entries and entries that continue on the next page. The results serve researchers and developers comparing models on structured extraction from printed sources, and practitioners in libraries, historical research and digital humanities projects who choose a model for converting printed bibliographies into databases.

**Audience:**

- AI researchers
- model developers
- industry practitioners

**Tasks:**

- segmentation of a printed list into bibliographic entries
- structured extraction of bibliographic fields from images
- classification of entry types
- linking reviews to the entries they review
- detection of entries that continue on the next page

**Limitations:** The benchmark covers five pages of a single printed bibliography (philosophy of history, works of 1945–1957), with an English-language apparatus and titles in several European languages. Results do not transfer to other citation styles, periods or layouts.

Entries are compared by position (see Calculation), so a missed or split entry shifts every later entry and is penalised many times over. Only fields present in the ground truth are scored, so extra entries and extra fields in a response cost nothing.

Part of the ground truth cannot be reproduced by a response that follows the `Document` schema. 69 of the 729 scored fields use hyphenated keys (`container-title`, `publisher-place`, `event-date`) or nested objects (`relation`, `reprint`, `related`) where the schema has underscored keys or plain strings, and 13 entry types (`article-journal`, `chapter`, `review`) are not among the schema's values (`book`, `journal-article`, `other`). No schema-conformant response can match these fields exactly, so the attainable score is below 1.0.

**Out-of-Scope Uses:**

- drawing conclusions about the works or authors listed
- evaluating citation parsing from born-digital text
- ranking models on bibliographies in other styles, languages or periods

## Data

**Source:** Five page images of the "Bibliography of Works in the Philosophy of History, 1945–1957", compiled by John C. Rule and published as "Chronological List" in History and Theory, Beiheft 1 ('s-Gravenhage: Mouton, 1961), pp. 1–74, digitised on JSTOR: http://www.jstor.org/stable/2504495. The pages list books, journal articles and reviews by year, with author, title, publisher, place, year, volume and pages, and with cross-references between entries.

**Size:** 5 evaluated objects

**Format:** One JPEG scan per page, about 1,750–1,910 × 2,880–2,950 px and 300–400 KB each. The ground truth is one JSON file per page; the excerpt below is from `page_2.json`. It is not a schema-valid response: `issued` is numeric and `relation` is an object, where the response schema expects strings:

```json
{
  "metadata": {
    "title": "Books",
    "year": "1945",
    "page_number": 1
  },
  "entries": [
    {
      "id": "5",
      "type": "book",
      "title": "The Use of Personal Documents in History, Anthropology, and Sociology",
      "author": [
        { "family": "Gottschalk", "given": "L." },
        { "family": "Kluckhohn", "given": "C." },
        { "family": "Angell", "given": "R." }
      ],
      "publisher": "Social Science Research Council",
      "publisher_place": "New York",
      "note": "Published as Bulletin 53 by the SSRC",
      "issued": 1945
    },
    {
      "id": "6",
      "type": "journal-article",
      "title": "Review of The Use of Personal Documents in History, Anthropology, and Sociology",
      "author": [
        { "family": "Lapiere", "given": "R. T." }
      ],
      "container_title": "The American Journal of Sociology",
      "volume": "LII",
      "issued": 1946,
      "relation": { "reviewed": "5" }
    }
  ]
}
```

The five pages hold 82 entries (14–20 per page) and 729 scored fields. `id` is the running number printed in the bibliography. `issued` is an integer in the ground truth and a string in the schema; the scorer compares both as strings, so they match. Further deviations from the schema are listed under Limitations.

**Annotation:** Sven Burkhardt and Pema Frick created the ground truth by hand, with Pema Frick as domain expert. They structured each entry in a CSL-like representation, including cross-references and entries that continue across pages.

**Size Breakdown:**

- image files: 5

**Collection Date:** Source documents: works published 1945–1957, listed in a bibliography published in 1961. Added to the benchmark: February 2025 (pages 2 and 10), April 2025 (pages 3–5).

**Contamination Controls:** None. The page images, prompt and ground truth have been public in this repository since February 2025.

## Methodology

**Methods:**

- zero-shot structured extraction from a single image per request
- structured JSON output requested using the `Document` dataclass
- one prompt, [prompt.txt](prompts/prompt.txt), used by all tests; it adds three instructions to the schema: the page number (taken from the file name), the `id` of the reviewed entry in `relation`, and `incomplete` for an entry that continues on the next page. All other conventions come from the schema alone
- output cap: the repository default of 16,384 tokens per request, adjusted per model in `scripts/benchmark_base.py`

**Metrics:**

- Fuzzy similarity (`fuzzy`, used for ranking)

**Calculation:** Every terminal field of the ground truth outside `metadata` (for example `entries[3].author[0].family`) is looked up at the same path in the response, so entries are matched by position. Fields only in the response are ignored.

- identical values (after converting both to strings) score 1.0
- a missing value in the response scores 0.0
- otherwise the score is the rapidfuzz `ratio` divided by 100, between 0 and 1; there is no threshold

The page score is the mean over that page's fields. The benchmark score is the mean of the page scores, so each page counts equally regardless of how many entries it holds. A response that cannot be parsed into the schema is not scored and does not enter the mean.

**Interpretation:** Scores range from 0 to 1; higher is better. Because partial string similarity earns partial credit, a wrong but similar value (for example `journal-article` for `article-journal`) still scores about 0.5. Part of the gap to 1.0 is not model error but the schema mismatch described under Limitations.

**Baseline Results:** Model results are available on the [benchmark page](https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/bibliographic_data) and in `results/<date>/<test_id>/` at the repository root. Compare runs with the same prompt, scoring rules and ground-truth revision, and report the number of successfully scored objects alongside the score. No fixed baseline run is designated.

Observed across models: common difficulties are entries with many authors, abbreviated journal titles and volume notations, telling reviews apart from the works they review, and entries that run over the page break.

**Validation:** The annotators created the ground truth by hand. Scoring is deterministic; the scorer is covered by the repository's test suite. The ground truth does not consistently conform to the response schema (see Limitations).

**Human Baseline:** Not specified

**Judge Uses LLM:** false

**Judge Num:** Not specified

**Judge Models:** Not specified

**Judge Score Consolidation:** Not specified

**Validity Justification:** Field-level similarity reflects the downstream use: each field becomes a value in a bibliographic record, and near-misses need less correction than wrong values.

## Ethical and Legal Considerations

**Privacy and Anonymity:** The pages name the authors, editors and reviewers of scholarly works published 1945–1957, as printed in a published bibliography. They contain no personal data beyond what is in the published record.

**Data Licensing:** Source material: Not specified. Ground truth, prompts and other data created for this benchmark: CC BY 4.0.

**Consent Procedures:** Not specified

**Compliance with Regulations:** The page images are JSTOR scans of a 1961 journal supplement that is still under copyright (the journal is now published by Wiley). No licence or permission to redistribute them is held; they are used for non-commercial academic research. The ground truth records the bibliographic data of the entries, which are facts rather than protected expression. No ethical review was carried out.

## Beyond the BenchmarkCard

This section is not part of the BenchmarkCard schema and is not exported to `benchmark_card.json`.

**Versions:**

- 1.0.0 — initial versioned state

**How to Cite:** This benchmark:

> Frick, P., Burkhardt, S., & Marti, S. (2025). Bibliographic Data (benchmark version 1.0.0). In *RISE Humanities Data Benchmark*. Zenodo. https://doi.org/10.5281/zenodo.16941752

Source:

> History and Theory, Beiheft 1 (1961), via JSTOR, 1945–1957. Licence of the source material: Not specified. http://www.jstor.org/stable/2504495

The benchmark suite:

> Hindermann, M., Marti, S., Kasper, L. K., & Bosse, A. (2026). The RISE Humanities Data Benchmark: A Framework for Evaluating Large Language Models for Humanities Tasks. *Journal of Open Humanities Data*, *12*(1), 24. https://doi.org/10.5334/johd.481
>
> Hindermann, M., Kasper, L. K., Marti, S., & Bosse, A. (2026). From Experiments to Epistemic Practice: The RISE Humanities Data Benchmark. *Journal of Open Humanities Data*, *12*(1), 38. https://doi.org/10.5334/johd.470

**Contributors by Role:**

- Domain Expert: Pema Frick
- Data Curator: Pema Frick
- Annotator: Sven Burkhardt, Pema Frick
- Analyst: Pema Frick, Sorin Marti
- Engineer: Pema Frick, Sorin Marti
