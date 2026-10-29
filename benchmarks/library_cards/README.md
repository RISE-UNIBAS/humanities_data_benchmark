# Library Cards

This README is a BenchmarkCard (Sokol et al., NeurIPS 2025, arXiv 2410.12974), schema as in evaleval/auto-benchmarkcard v0.2.0.

<!-- Every field stays, in this order; write 'Not specified' when unknown. Fields marked
     (generated) are filled from meta.json and the benchmark's files by
     `python scripts/benchmark_cards.py <name>`; edit meta.json, not the README, to change them. -->

The scoring implementation is in [benchmark.py](benchmark.py), the requested output schema in [dataclass.py](dataclass.py), and the instructions in [prompts/](prompts/).

To run this benchmark, use `python scripts/run_single_test.py --adhoc` from the repository root and select `library_cards`. Provider setup is described in the [root README](../../README.md#quick-start); configured prompts, models and scoring rules are recorded in [benchmarks_tests.csv](../benchmarks_tests.csv). Provider-backed runs incur API charges.

## Benchmark Details

**Name:** Library Cards

**Overview:** Tests models on extracting bibliographic records (author, title, year, place, pages, publisher, format, shelfmark, subjects and the card's type) from typed, printed and handwritten cards of the University Library Basel's dissertation catalogue (before 1980).

**Data Type:** image

**Domains:**

- library science
- bibliography
- history of universities

**Languages:**

- German
- French
- English
- Latin
- Greek
- Finnish
- Swedish
- Polish

**Similar Benchmarks:** Not specified

**Resources:**

- https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/library_cards
- https://github.com/RISE-UNIBAS/humanities_data_benchmark/tree/main/benchmarks/library_cards

**Authors:**

- Gabriel Müller
- Maximilian Hindermann

## Purpose and Intended Users

**Goal:** Measure how well vision-language models turn catalogue cards of historical dissertations into structured bibliographic records (author, title, year, place, pages, publisher, format, shelfmark, subjects) and tell full descriptions apart from cross-reference cards. The results serve researchers and developers comparing models on historical document extraction, and practitioners in libraries, archives and digital humanities projects who choose a model for converting card catalogues into machine-readable metadata.

**Audience:**

- humanities researchers
- archivists and librarians
- AI researchers
- model developers

**Tasks:**

- bibliographic field extraction from card images
- classification of a card as a dissertation description or a cross-reference

**Limitations:** The 263 cards are a random sample from a single catalogue (see Source), not stratified by period, language or card condition. They mix typed, printed and handwritten entries, mostly in German. Only 10 are cross-references, so results on that class rest on very few cases.

The ground truth was created by correcting GPT-4o output, so where the corrector accepted an ambiguous reading it may lean towards that model's choices; the stored runs show no strong effect (GPT-4o scores F1 macro 0.85, rank 54 of 119 runs, against a median of 0.81 for models of its generation). It follows the normalisation conventions described under Annotation, so it measures agreement with those conventions rather than with a neutral cataloguing standard.

All fields weigh equally, so a wrong shelfmark costs as much as a wrong author. The match threshold (see Calculation) is strict for short fields: `X, 184` against `X,184` or `Thieme Verlag` against `Thieme` scores as wrong. Fields empty on both sides are not counted, so a sparse card has a small denominator and a single error moves its F1 considerably.

**Out-of-Scope Uses:**

- evaluating full-text transcription of catalogue cards
- evaluating extraction of the thesis defence, faculty, supervisor or later editions, which the cards sometimes record but the schema does not
- drawing conclusions about the authors named on the cards

## Data

**Source:** Catalogue cards of the *Dissertationenkatalog bis 1980*, the dissertation catalogue of the University Library Basel (Universitätsbibliothek Basel), https://ub.unibas.ch/cmsdata/spezialkataloge/ipac/searchform.php?KatalogID=ak2. The catalogue covers the roughly 700,000 dissertations the library collected before 1980; the benchmark's cards were drawn at random from its 680,671 scanned cards. The dissertations come mainly from Switzerland and neighbouring countries. A card describes one dissertation, usually its author and the published version of record, sometimes also the defence or other published versions, without separating these explicitly. Some cards are cross-references: they name an author followed by `s.` (German *siehe*, "see") on a separate line and point to another card.

**Size:** 263 evaluated objects

**Format:** One JPG per card, about 1000×600 px and 75 KB, typed, printed or handwritten. Each card has one ground-truth JSON file following the `Document` dataclass in `dataclass.py`:

```json
{
  "type": {"type": "Dissertation or thesis"},
  "author": {"last_name": "Müller", "first_name": "Maurice Edmond"},
  "publication": {
    "title": "Die hüftnahen Femurosteotomien unter Berücksichtigung der Form,Funktion und Beanspruchung des Hüftgelenkes",
    "year": "1957",
    "place": "Stuttgart",
    "pages": "X,184",
    "publisher": "Thieme",
    "format": "4'"
  },
  "library_reference": {"shelfmark": "AT Zürich 7", "subjects": ""}
}
```

- `type.type`: `Dissertation or thesis` or `Reference`
- `author`: `last_name`, `first_name`
- `publication`: `title`, `year`, `place`, `pages`, `publisher`, `format`; the dataclass also allows `editor`, which no ground-truth file fills
- `library_reference`: `shelfmark` (often beginning `Diss.` or `AT`, or marked `Standort:`), `subjects`

The ground truth stores `year` as a string, empty when the card gives none. The response schema allows a string or null, and the local Pydantic validator converts a numeric year to a string. The scorer compares both as strings, so `1957` and `"1957"` match.

**Annotation:** GPT-4o drafted the ground truth; Gabriel Müller and Maximilian Hindermann corrected it by hand, card by card, in a viewer showing the image beside the draft. They followed the extraction rules of [prompt.txt](prompts/prompt.txt): a card with `s.` on its own line is a `Reference`, and pages are given without `S.`. In addition, pages keep unnumbered parts (`IV S. + 67-74 S.` becomes `IV 67-74`), and the octavo mark is kept exactly as on the card (`8°` or `8'`).

**Size Breakdown:**

- image files: 263

**Collection Date:** Source documents: dissertations published 1593–1979, most of them 1880–1979. Added to the benchmark: April 2025.

**Contamination Controls:** None. The card images, prompts and ground truth have been public in this repository since April 2025.

## Methodology

**Methods:**

- zero-shot structured extraction from a single card image per request
- structured JSON output requested using the `Document` dataclass
- two prompt variants: [prompt.txt](prompts/prompt.txt) (127 tests) asks for `year` as an integer, although the response schema allows only a string or null, which can make constrained decoding emit whitespace until the output cap; [prompt_year-string.txt](prompts/prompt_year-string.txt) (4 tests, the default for new tests) asks for a string and is otherwise identical. Scores of the two variants are not directly comparable for a model affected by the loop
- output cap: the repository default of 16,384 tokens per request, adjusted per model in `scripts/benchmark_base.py`

**Metrics:**

- F1 macro (`f1_macro`, used for ranking)
- F1 micro (`f1_micro`)

**Calculation:** Every terminal field of the JSON (for example `publication.title`) present in the response or the ground truth is compared; empty strings count as missing. Legacy `examination` fields, `publication.reprint_note` and `library_reference.publication_number` are excluded. Field values are compared with a rapidfuzz similarity score (`ratio`/100; values are compared as strings), and a field is a match at a score of 0.92 or above.

- TP: both have a value and the score is at least 0.92
- FP and FN: both have a value but the score is below 0.92 (the field counts once as each)
- FP: only the response has a value
- FN: only the ground truth has a value
- neither: both are empty

F1 macro averages the per-card F1, each rounded to two decimals. F1 micro sums TP, FP and FN over all cards before computing F1. A response that cannot be parsed is scored as a miss: every ground-truth field counts as a false negative.

For example, for the ground truth above and a response that differs only in `first_name` (`Maurice`), `pages` (`X, 184`) and `publisher` (`Thieme Verlag`), the card has 7 TP, 3 FP and 3 FN (`subjects` is empty in both and not counted), so precision, recall and F1 are 0.70.

**Interpretation:** Scores range from 0 to 1; higher is better. F1 macro weights every card equally; F1 micro weights cards by their number of filled fields, so full descriptions count more than sparse cards and cross-references. A score does not separate misreadings from differences in normalisation (see Limitations). Across the 95 active test configurations, F1 macro has a median of 0.85 and an interquartile range of 0.79–0.88; the best reach 0.91.

**Baseline Results:** Model results are available on the [benchmark page](https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/library_cards) and in `results/<date>/<test_id>/` at the repository root. Compare runs with the same prompt, scoring rules and ground-truth revision, and report the number of successfully scored objects alongside the score. No fixed baseline run is designated.

Observed across models: the card type (93% of fields correct across all stored runs), first names (88%) and places (87%) are read best; subjects (61%), shelfmarks (70%), formats (70%) and pages (77%) worst. Common errors are omitted or misparsed shelfmarks and subject classifications, small formatting differences in pages and publisher, publisher names with an added "Verlag", and variant notations of format and academic abbreviations.

**Validation:** The annotators checked the ground truth by hand against the images. Scoring is deterministic; the scorer is covered by the repository's test suite. No inter-annotator agreement was measured.

**Human Baseline:** Not specified

**Judge Uses LLM:** false

**Judge Num:** Not specified

**Judge Models:** Not specified

**Judge Score Consolidation:** Not specified

**Validity Justification:** Field-level F1 reflects the downstream use: each field becomes a value in a catalogue record, so a field is either usable or needs correction.

## Ethical and Legal Considerations

**Privacy and Anonymity:** The cards name the authors of dissertations together with the title, place and year of the work; the same data is in the library's public catalogue. The cards are not anonymised: they hold metadata of published works and no personal data beyond the authorship the publications themselves state.

**Data Licensing:** Source material: CC0. Ground truth, prompts and other data created for this benchmark: CC BY 4.0.

**Consent Procedures:** Not specified

**Compliance with Regulations:** The cards are bibliographic records of published works, so no personal-rights issue arises. The University Library Basel provided the card images and granted their use under CC0; no licence is published with the catalogue itself. No ethical review was carried out.

## Beyond the BenchmarkCard

This section is not part of the BenchmarkCard schema and is not exported to `benchmark_card.json`.

<!-- Versions use semantic versioning, newest first, one line each: `- MAJOR.MINOR.PATCH — what
     changed and why`.
     MAJOR: scores before and after are not comparable (ground truth corrected, scoring or
            ranking metric changed, objects added or removed).
     MINOR: something added that leaves existing scores unchanged (e.g. a new prompt variant).
     PATCH: a fix that changes no score (e.g. a better scan of the same image). -->

**Versions:**

- 2.0.0 — ground truth corrected: `00575005` (a cross-reference without a year) has an empty year instead of `0`; ground-truth files hold only the card record, years as strings; two files without an image removed; a response that cannot be parsed is scored as a miss instead of being left out; all stored runs re-scored
- 1.0.0 — initial versioned state, when the card was introduced; same content as 0.6.1

**How to Cite:** This benchmark:

> Müller, G., & Hindermann, M. (2025). Library Cards (benchmark version 2.0.0). In *RISE Humanities Data Benchmark*. Zenodo. https://doi.org/10.5281/zenodo.16941752

Source:

> Universitätsbibliothek Basel, Dissertationenkatalog bis 1980, 1593–1979. Licence of the source material: CC0. https://ub.unibas.ch/cmsdata/spezialkataloge/ipac/searchform.php?KatalogID=ak2

The benchmark suite:

> Hindermann, M., Marti, S., Kasper, L. K., & Bosse, A. (2026). The RISE Humanities Data Benchmark: A Framework for Evaluating Large Language Models for Humanities Tasks. *Journal of Open Humanities Data*, *12*(1), 24. https://doi.org/10.5334/johd.481
>
> Hindermann, M., Kasper, L. K., Marti, S., & Bosse, A. (2026). From Experiments to Epistemic Practice: The RISE Humanities Data Benchmark. *Journal of Open Humanities Data*, *12*(1), 38. https://doi.org/10.5334/johd.470

**Contributors by Role:**

- Domain Expert: Gabriel Müller
- Data Curator: Gabriel Müller
- Annotator: Maximilian Hindermann, Gabriel Müller
- Analyst: Maximilian Hindermann
- Engineer: Maximilian Hindermann
