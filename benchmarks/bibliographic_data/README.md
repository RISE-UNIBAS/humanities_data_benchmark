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

**Goal:** Measure how well vision-language models turn a printed scholarly bibliography page into structured, citation-style records (CSL-like JSON): splitting the page into entries, classifying each entry, separating authors into family and given names, and recording publication details, cross-references between entries and entries that continue on the next page. The results are meant to guide librarians, historians and digital humanities projects in choosing a model for retro-converting printed bibliographies into databases.

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

**Limitations:** Five pages from a single printed bibliography (philosophy of history, works of 1945–1957), English-language apparatus with titles in several European languages; results do not transfer automatically to other citation styles, periods or layouts. Entries are compared by position (`entries[0]` with `entries[0]`), so a missed or split entry shifts every later entry and is penalised many times over. Only fields present in the ground truth are scored, so extra entries and extra fields in a response cost nothing. Part of the ground truth cannot be reproduced by a response that follows the `Document` schema: 69 of the 729 scored fields use hyphenated keys (`container-title`, `publisher-place`, `event-date`) or nested objects (`relation`, `reprint`, `related`) where the schema has underscored keys or plain strings, and 13 entry types (`article-journal`, `chapter`, `review`) are not among the schema's values (`book`, `journal-article`, `other`). These mismatches prevent exact agreement on the affected fields; a single ceiling cannot be inferred just by dividing incompatible fields by the total because pages are weighted equally and type mismatches can earn partial credit. The prompt explains only page number, reviews and incomplete entries; all other conventions come from the schema alone.

**Out-of-Scope Uses:**

- drawing conclusions about the works or authors listed
- evaluating citation parsing from born-digital text
- ranking models on bibliographies in other styles, languages or periods

## Data

**Source:** Five page images of the "Bibliography of Works in the Philosophy of History, 1945–1957", compiled by John C. Rule and published as "Chronological List" in History and Theory, Beiheft 1 ('s-Gravenhage: Mouton, 1961), pp. 1–74, digitised on JSTOR: http://www.jstor.org/stable/2504495. The pages list books, journal articles and reviews by year, with author, title, publisher, place, year, volume and pages, and with cross-references between entries.

**Size:** 5 evaluated objects

**Format:** One JPEG scan per page, about 1750–1910 × 2880–2950 px and 300–400 KB each. The ground truth is one JSON file per page, using the historical ground-truth representation illustrated below. This example is not a schema-valid response: `issued` is numeric and `relation` is an object, whereas the current response schema expects strings:

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

The five pages hold 82 entries (14–20 per page) and 729 scored fields. `id` is the running number printed in the bibliography; `issued` is an integer in the ground truth and a string in the schema, which the scorer treats as equal. Some files deviate from the schema as described under Limitations.

**Annotation:** Ground truths were created manually by the annotators Sven Burkhardt and Pema Frick, with Pema Frick as domain expert (see Contributors by Role), extracting and structuring the entries in a CSL-like representation, including cross-references and entries continued across pages. The ground truths of three pages were revised in April 2025.

**Size Breakdown:**

- images files: 5

**Collection Date:** Not specified for benchmark collection or digitisation. Source-document dates: The bibliography covers works published 1945–1957 and was itself published in 1961.

**Contamination Controls:** No held-out private split, training-data audit or other contamination control is documented. Inputs, prompts and ground truths are distributed together in this public repository. Whether any evaluated model saw these materials during training is unknown.

## Methodology

**Methods:**

- zero-shot structured extraction from a single image per request
- structured JSON output requested using the `Document` dataclass
- the page number, taken from the file name, is inserted into the prompt

**Metrics:**

- Fuzzy similarity (`fuzzy`, used for ranking)

**Calculation:** Every terminal field of the ground truth outside `metadata` (for example `entries[3].author[0].family`) is looked up at the same path in the response. Fields only in the response are ignored.

- identical values (after converting both to strings) score 1.0
- a missing value in the response scores 0.0
- otherwise the score is the rapidfuzz `ratio` divided by 100, between 0 and 1; there is no threshold

The page score is the mean over that page's fields. The benchmark score is the mean of the page scores, so each page counts equally regardless of how many entries it holds. A response that cannot be parsed into the schema is not scored and does not enter the mean.

**Interpretation:** Scores range from 0 to 1; higher is better. Because partial string similarity earns partial credit, a wrong but similar value (for example `journal-article` for `article-journal`) still scores around 0.5. The schema/ground-truth mismatches described under Limitations mean that the gap to 1.0 is not all model error; no exact schema-conformant ceiling is established here.

**Baseline Results:** Model results are available on the [benchmark page](https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/bibliographic_data) and in `results/<date>/<test_id>/` at the repository root. Compare runs with the same prompt, scoring rules and ground-truth revision, and report the number of successfully scored objects alongside the score. No fixed model baseline with a run ID and date is specified here.

Observed across models: common difficulties are entries with many authors, abbreviated journal titles and volume notations, telling reviews apart from the works they review, and entries that run over the page break.

**Validation:** Ground truths were created and later revised by the annotators. Scoring is deterministic; the scorer is covered by the repository's test suite. The ground truths do not consistently conform to the response schema (see Limitations); JSON validity alone does not establish schema compatibility.

**Human Baseline:** Not specified

**Judge Uses LLM:** false

**Judge Num:** Not specified

**Judge Models:** Not specified

**Judge Score Consolidation:** Not specified

**Validity Justification:** Field-level similarity reflects the downstream use: each field becomes a value in a bibliographic record, and near-misses need less correction than wrong values. Not specified beyond that.

## Ethical and Legal Considerations

**Privacy and Anonymity:** The pages name the authors, editors and reviewers of scholarly works published 1945–1957, as printed in a published bibliography. They contain no personal data beyond what is in the published record.

**Data Licensing:** Not specified

**Consent Procedures:** Not specified

**Compliance with Regulations:** The page images are JSTOR scans of a 1961 journal issue that is still under copyright (the journal is now published by Wiley). No licence or permission to redistribute them is held; they are used for non-commercial academic research. No ethical review was carried out.

## Beyond the BenchmarkCard

This section is not part of the BenchmarkCard schema and is not exported to `benchmark_card.json`.

**Versions:**

- 1.0.0 — initial versioned state

**Contributors by Role:**

- Domain Expert: Pema Frick
- Data Curator: Pema Frick
- Annotator: Sven Burkhardt, Pema Frick
- Analyst: Pema Frick, Sorin Marti
- Engineer: Pema Frick, Sorin Marti
