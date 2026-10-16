# Library Cards

This README is a BenchmarkCard (Sokol et al., NeurIPS 2025, arXiv 2410.12974), schema as in evaleval/auto-benchmarkcard v0.2.0.

<!-- Every field stays, in this order; write 'Not specified' when unknown. Fields marked
     (generated) are filled from meta.json and the benchmark's files by
     `python scripts/benchmark_cards.py <name>`; edit meta.json, not the README, to change them. -->

The scoring implementation is in [benchmark.py](benchmark.py), the requested output schema in [dataclass.py](dataclass.py), and the instructions in [prompts/](prompts/).

To run this benchmark, use `python scripts/run_single_test.py --adhoc` from the repository root and select `library_cards`. Provider setup is described in the [root README](../../README.md#quick-start); configured prompts, models and scoring rules are recorded in [benchmarks_tests.csv](../benchmarks_tests.csv). Provider-backed runs incur API charges.

## Benchmark Details

**Name:** Library Cards

**Overview:** Tests models on extracting bibliographic data (author, title, year, place and the card's type) from typed, printed and handwritten cards of the University Library Basel's dissertation catalogue (before 1980).

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

**Goal:** Measure how well vision-language models turn catalogue cards of historical dissertations into structured bibliographic records (author, title, year, place, pages, publisher, format, shelfmark, subjects) and tell full descriptions apart from cross-reference cards. The results are meant to guide libraries, archivists and digital humanities projects in choosing a model for converting card catalogues into machine-readable metadata.

**Audience:**

- AI researchers
- model developers
- industry practitioners

**Tasks:**

- bibliographic field extraction from card images
- classification of a card as a dissertation description or a cross-reference

**Limitations:** 263 cards drawn at random from a single catalogue, the dissertation catalogue of the University Library Basel (about 700,000 dissertations before 1980); the cards mix typed, printed and handwritten entries, mostly in German, and only 10 are cross-references, so results on the reference class rest on very few cases. Random sampling was not stratified by period, language or card condition.

The ground truth was created by correcting GPT-4o output, so where the corrector accepted an ambiguous reading the reference may lean towards that model's choices. It also follows normalisation rules set in the prompt (e.g. pages without `S.`, octavo kept as `8°` or `8'` as on the card), so it measures agreement with those conventions rather than with a neutral catalogue standard. Some ground truths contain errors: `00575005` has year `0`.

All fields count equally, so a wrong shelfmark costs as much as a wrong author. A field counts as matched only at a fuzzy similarity of 0.92 or above, so short fields that differ by a space or a word (`X, 184` against `X,184`, `Thieme Verlag` against `Thieme`) score as wrong. Fields empty in both the ground truth and the response are not counted at all, so a sparse card has a small denominator and a single error moves its F1 a lot.

**Out-of-Scope Uses:**

- evaluating full-text transcription of catalogue cards
- evaluating extraction of the thesis defence, faculty, supervisor or later editions, which the cards sometimes record but the schema does not
- drawing conclusions about the authors named on the cards

## Data

**Source:** Catalogue cards of the *Dissertationenkatalog bis 1980*, the dissertation catalogue of the University Library Basel (Universitätsbibliothek Basel), https://ub.unibas.ch/cmsdata/spezialkataloge/ipac/searchform.php?KatalogID=ak2, a random sample of the cards for the roughly 700,000 dissertations the library collected before 1980. The dissertations come mainly from Switzerland and neighbouring countries. A card describes one dissertation, usually its author and the published version of record, sometimes also the defence or other published versions, without separating these explicitly. Some cards are cross-references: they name an author followed by `s.` (German *siehe*, "see") on a separate line and point to another card.

**Size:** 263 evaluated objects

**Format:** One JPG per card, about 1000×600 px and 75 KB, typed, printed or handwritten. There are 263 image-matched ground-truth JSON files. Two additional files, `00604370.json` and `00604375.json`, have no matching input image and are not evaluated by the normal runner. The fields `provider`, `model`, `test_time`, `execution_time` and `scores` record how the ground truth was drafted; only `response_text` is scored. It follows the `Document` dataclass in `dataclass.py`:

```json
{
  "type": {"type": "Dissertation or thesis"},
  "author": {"last_name": "Müller", "first_name": "Maurice Edmond"},
  "publication": {
    "title": "Die hüftnahen Femurosteotomien unter Berücksichtigung der Form,Funktion und Beanspruchung des Hüftgelenkes",
    "year": 1957,
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
- `publication`: `title`, `year`, `place`, `pages`, `publisher`, `format`; the dataclass also allows `editor`, which no ground truth fills
- `library_reference`: `shelfmark` (often beginning `Diss.` or `AT`, or marked `Standort:`), `subjects`

Ground truths store `year` mostly as an integer, the provider-facing response schema as a string or null; the local Pydantic validator also accepts numeric years and converts them to strings; the scorer compares the two as strings, so `1957` and `"1957"` match.

**Annotation:** Ground truths were drafted by GPT-4o and corrected by hand by the annotators listed under Authors with the `ground_truther.py` tool, following the rules in the [prompt file](prompts/prompt.txt): a card with `s.` on its own line is a `Reference`; pages are given without `p.` or `S.` but keep unnumbered parts (`IV S. + 67-74 S.` becomes `IV 67-74`); the octavo mark is kept exactly as on the card (`8°` or `8'`).

**Size Breakdown:**

- images files: 263

**Collection Date:** Not specified for benchmark collection or digitisation. Source-document dates: The cards describe dissertations published between 1593 and 1979, most of them between 1880 and 1979.

**Contamination Controls:** No held-out private split, training-data audit or other contamination control is documented. Inputs, prompts and ground truths are distributed together in this public repository. Whether any evaluated model saw these materials during training is unknown.

## Methodology

**Methods:**

- zero-shot structured extraction from a single card image per request
- structured JSON output requested using the `Document` dataclass
- two prompt variants: `prompt.txt`, used by most tests, asks for `year` as an integer although the provider-facing JSON schema allows only a string or null (the local parser can coerce a numeric year), which can make constrained decoding loop until the output cap; new tests use `prompt_year-string.txt`, which asks for a string and is otherwise identical. Scores of the two variants are not directly comparable where a model was affected by the loop

**Metrics:**

- F1 macro (`f1_macro`, used for ranking)
- F1 micro (`f1_micro`)

**Calculation:** Every terminal field of the JSON (for example `publication.title`) present in the response or the ground truth is compared; empty strings count as missing. Legacy `examination` fields, `publication.reprint_note` and `library_reference.publication_number` are excluded. Field values are compared with a rapidfuzz similarity score (`ratio`/100; values are compared as strings), and a field is a match at a score of 0.92 or above.

- TP: both have a value and the score is at least 0.92
- FP and FN: both have a value but the score is below 0.92 (the field counts once as each)
- FP: only the response has a value
- FN: only the ground truth has a value
- neither: both are empty

F1 macro averages the per-card F1, each rounded to two decimals. F1 micro sums TP, FP and FN over all cards before computing F1. A response that is not parseable JSON is left out of both rather than scored as zero.

For example, for the ground truth above and a response that differs only in `first_name` (`Maurice`), `pages` (`X, 184`) and `publisher` (`Thieme Verlag`), the card has 7 TP, 3 FP and 3 FN (`subjects` is empty in both and not counted), so precision, recall and F1 are 0.70.

**Interpretation:** Scores range from 0 to 1; higher is better. F1 macro weights every card equally; F1 micro weights cards by their number of filled fields, so full descriptions count more than sparse cards and cross-references.

**Baseline Results:** Model results are available on the [benchmark page](https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/library_cards) and in `results/<date>/<test_id>/` at the repository root. Compare runs with the same prompt, scoring rules and ground-truth revision, and report the number of successfully scored objects alongside the score. No fixed model baseline with a run ID and date is specified here.

Observed across models: models generally do well on clearly typed cards with standard layouts and worse on handwritten cards and those with non-standard layouts or abbreviations. Common errors are omitted or misparsed shelfmarks and subject classifications, small formatting differences in pages and publisher, publisher names with an added "Verlag", and variant notations of format and academic abbreviations.

**Validation:** Ground truths were checked by hand against the images. Scoring is deterministic; the scorer is covered by the repository's test suite. No inter-annotator agreement was measured.

**Human Baseline:** Not specified

**Judge Uses LLM:** false

**Judge Num:** Not specified

**Judge Models:** Not specified

**Judge Score Consolidation:** Not specified

**Validity Justification:** Field-level F1 reflects the downstream use: each field becomes a value in a catalogue record, so a field is either usable or needs correction. Not specified beyond that.

## Ethical and Legal Considerations

**Privacy and Anonymity:** The cards name the authors of dissertations together with the title, place and year of the work. These are published works and the same data is in the library's public catalogue. The cards are not anonymised: they hold metadata of published works, not personal data beyond the authorship that the publications themselves state.

**Data Licensing:** CC0

**Consent Procedures:** Not specified

**Compliance with Regulations:** The cards are bibliographic records of published works, so no personal-rights issue arises. The University Library Basel provided the card images and granted their use under CC0; no licence is published with the catalogue itself. No separate reuse terms are stated for the ground truths. No ethical review was carried out.

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

- Domain Expert: Gabriel Müller
- Data Curator: Gabriel Müller
- Annotator: Maximilian Hindermann, Gabriel Müller
- Analyst: Maximilian Hindermann
- Engineer: Maximilian Hindermann
