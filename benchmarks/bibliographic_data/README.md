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

- humanities researchers
- archivists and librarians
- AI researchers
- model developers

**Tasks:**

- segmentation of a printed list into bibliographic entries
- structured extraction of bibliographic fields from images
- classification of entry types
- linking reviews to the entries they review
- detection of entries that continue on the next page

**Limitations:** The benchmark covers five pages of a single printed bibliography (philosophy of history, works of 1945–1957), with an English-language apparatus and titles in several European languages. Results do not transfer to other citation styles, periods or layouts.

Entries are aligned in page order before scoring (see Calculation), so a missed or split entry costs only its own fields. Only fields present in the ground truth are scored, so extra entries and extra fields in a response cost nothing.

The ground truth records what each entry prints, and the schema leaves some conventions open that `prompt.txt` does not settle: the `id` is the printed running number (stated in `prompt_v2.txt`), a year is recorded only where the entry prints one, and a parenthetical or bracketed remark goes into `note` as printed. A model that numbers entries its own way loses every `id` and `relation`; a year inferred from the section heading where none is printed costs nothing. Top models score close to 1 (see Baseline Results), so the benchmark separates weaker models more than strong ones.

**Out-of-Scope Uses:**

- drawing conclusions about the works or authors listed
- evaluating citation parsing from born-digital text
- ranking models on bibliographies in other styles, languages or periods

## Data

**Source:** Five page images of the "Bibliography of Works in the Philosophy of History, 1945–1957", compiled by John C. Rule and published as "Chronological List" in History and Theory, Beiheft 1 ('s-Gravenhage: Mouton, 1961), pp. 1–74, digitised on JSTOR: http://www.jstor.org/stable/2504495. The pages list books, journal articles and reviews by year, with author, title, publisher, place, year, volume and pages, and with cross-references between entries.

**Size:** 5 evaluated objects

**Format:** One JPEG scan per page, about 1,750–1,910 × 2,880–2,950 px and 300–400 KB each. The ground truth is one JSON file per page in the shape of the response schema; the excerpt below is from `page_2.json`:

```json
{
  "metadata": { "title": "Books", "year": "1945", "page_number": 1 },
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
      "note": "Bulletin 53"
    },
    {
      "id": "6",
      "type": "journal-article",
      "author": [ { "family": "Lapiere", "given": "R. T." } ],
      "container_title": "The American Journal of Sociology",
      "volume": "LII",
      "page": "156-157",
      "issued": "1946",
      "relation": "5"
    }
  ]
}
```

The five pages hold 91 entries (14–21 per page) and 741 scored fields. `id` is the running number printed in the bibliography; `relation` holds the `id` of the reviewed entry; `related` lists the entries a volume contains. The first entry of `page_3` is the end of entry 14 from the previous page and has no `id`. Fields the page does not print are left out, even where the schema requires them (the `title` of eight untitled reviews, and the `title` and `id` of that continued entry); fields left out are not scored.

**Annotation:** Sven Burkhardt and Pema Frick created the ground truth by hand, with Pema Frick as domain expert. They structured each entry in a CSL-like representation, including cross-references and entries that continue across pages. For version 2.0.0 the ground truth was checked entry by entry against the scans and brought into the shape of the response schema: transcription errors corrected (names, titles, volumes, pages, years), six missing entries of `page_5` (64–69) added, entries 146–148 of `page_10` made entries of their own, untitled reviews left without a title, notes given as printed, years kept only where the entry prints one, and initials written with spaces as printed.

**Size Breakdown:**

- image files: 5

**Collection Date:** Source documents: works published 1945–1957, listed in a bibliography published in 1961. Added to the benchmark: February 2025 (pages 2 and 10), April 2025 (pages 3–5).

**Contamination Controls:** None. The page images, prompt and ground truth have been public in this repository since February 2025.

## Methodology

**Methods:**

- zero-shot structured extraction from a single image per request
- structured JSON output requested using the `Document` dataclass
- [prompt.txt](prompts/prompt.txt), used by all existing tests, adds three instructions to the schema: the page number (taken from the file name, so `page_2` is told it is page 2 though it is printed page 1), the `id` of the reviewed entry in `relation`, and `incomplete` for an entry that continues on the next page. New tests use [prompt_v2.txt](prompts/prompt_v2.txt), which gives the printed page number and says that `id` is the running number printed in front of an entry. All other conventions come from the schema alone
- output cap: the repository default of 16,384 tokens per request, adjusted per model in `scripts/benchmark_base.py`

**Metrics:**

- Fuzzy similarity (`fuzzy`, used for ranking)

**Calculation:** Response entries are first aligned to ground-truth entries: an alignment that keeps both page orders and maximises the summed similarity of aligned entries, where the similarity of two entries is the mean field score below over the ground-truth entry's fields. Every terminal field of the ground truth outside `metadata` (for example `entries[3].author[0].family`) is then looked up at the same path in the aligned response entry. A ground-truth entry without a counterpart scores 0 in every field; response entries without a counterpart and fields only in the response are ignored.

- identical values (after converting both to strings) score 1.0
- a missing value in the response scores 0.0
- otherwise the score is the rapidfuzz `ratio` divided by 100, between 0 and 1; there is no threshold

The page score is the mean over that page's fields. The benchmark score is the mean of the page scores, so each page counts equally regardless of how many entries it holds. A response whose Document is nested under a single wrapper key (as some providers' tool calls return it) is unwrapped; a response that cannot be parsed scores 0.

**Interpretation:** Scores range from 0 to 1; higher is better. Because partial string similarity earns partial credit, a wrong but similar value (for example `Journal of Philosphy` for `Journal of Philosophy`, 0.98) still scores high; a score near 1 means near-exact records, not a share of correct entries.

**Baseline Results:** Model results are available on the [benchmark page](https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/bibliographic_data) and in `results/<date>/<test_id>/` at the repository root. Compare runs with the same prompt, scoring rules and ground-truth revision. No fixed baseline run is designated. Across the latest run of each of the 95 non-legacy tests, `fuzzy` has a median of 0.95 and a best of 0.99 (gpt-6-astra).

Observed across models: averaged over all scored fields of those runs, `note` (0.55), `relation` (0.71) and `issued` (0.73) score lowest, since they depend on conventions the prompt leaves open; names, titles, publishers and pages score about 0.9.

**Validation:** The annotators created the ground truth by hand; for version 2.0.0 every entry was checked against the scans, guided by the fields on which most of the ten best-scoring models agreed against the ground truth. Scoring is deterministic; the scorer is covered by `tests/test_bibliographic_data_scoring.py` and `tests/test_simple_averagers_scoring.py`, including a check that every ground-truth file scores 1 against itself.

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

- 2.0.0 (2026-10-18) — ground truth checked against the scans and conformed to the response schema (transcription errors, six missing entries, entries 146–148 unnested, `relation` as the reviewed `id`, notes and years as printed); `prompt_v2.txt` for new tests; entries aligned in page order instead of by position; a response nested under a wrapper key is unwrapped; a response that cannot be parsed is scored as a miss; all stored runs re-scored
- 1.0.0 (2026-10-16) — initial versioned state, when the card was introduced; same content as 0.10.1
- 0.10.1 (2026-09-11) — per-field comparison recorded with each answer; scores unchanged
- 0.10.0 (2026-09-09) — answers capped at 32,768 output tokens
- 0.9.0 (2026-08-16) — an answer that cannot be parsed is left out of the average instead of scored as a miss
- 0.8.2 (2026-06-30) — a run with no scored object scores 0 instead of failing
- 0.8.1 (2026-04-22) — a failed object is left out of the average instead of stopping the run
- 0.8.0 (2025-11-24) — answers are parsed by the API client instead of the benchmark; failed requests stop the run again
- 0.7.0 (2025-10-20) — numbers and strings compared as text, so a number matches the same digits given as a string
- 0.6.0 (2025-10-17) — requests that fail are saved as empty answers and scored as misses
- 0.5.0 (2025-10-16) — the prompt states the page number instead of a literal `{page_number}`
- 0.4.0 (2025-09-24) — schema rebuilt with pydantic: `relation` and `reprint` become strings, empty defaults become null
- 0.3.0 (2025-04-08) — `metadata` fields no longer scored; answers given as a list are accepted; two ground-truth files made valid JSON
- 0.2.0 (2025-04-03) — three pages added (page_3 to page_5); `issued` asked for as a string
- 0.1.0 (2025-03-01) — first state

**How to Cite:** This benchmark:

> Frick, P., Burkhardt, S., & Marti, S. (2025). Bibliographic Data (benchmark version 2.0.0). In *RISE Humanities Data Benchmark*. Zenodo. https://doi.org/10.5281/zenodo.16941752

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
