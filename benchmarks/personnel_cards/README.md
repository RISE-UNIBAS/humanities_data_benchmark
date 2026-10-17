# Personnel Cards

This README is a BenchmarkCard (Sokol et al., NeurIPS 2025, arXiv 2410.12974), schema as in evaleval/auto-benchmarkcard v0.2.0.

<!-- Every field stays, in this order; write 'Not specified' when unknown. Fields marked
     (generated) are filled from meta.json and the benchmark's files by
     `python scripts/benchmark_cards.py <name>`; edit meta.json, not the README, to change them. -->

The scoring implementation is in [benchmark.py](benchmark.py), the requested output schema in [dataclass.py](dataclass.py), and the instructions in [prompts/](prompts/).

To run this benchmark, use `python scripts/run_single_test.py --adhoc` from the repository root and select `personnel_cards`. Provider setup is described in the [root README](../../README.md#quick-start); configured prompts, models and scoring rules are recorded in [benchmarks_tests.csv](../benchmarks_tests.csv). Provider-backed runs incur API charges.

## Benchmark Details

**Name:** Personnel Cards

**Overview:** Evaluates models' ability to transcribe and interpret personnel index cards of Swiss federal employees, 1941–1961, from the Swiss Federal Archives: typed and handwritten table entries in German and French on job title, place of service, salary class, salary and remarks.

**Data Type:** image

**Domains:**

- history
- archival science
- administrative records

**Languages:**

- German
- French

**Similar Benchmarks:** Not specified

**Resources:**

- https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/personnel_cards
- https://github.com/RISE-UNIBAS/humanities_data_benchmark/tree/main/benchmarks/personnel_cards

**Authors:**

- Tabea Wullschleger
- Maximilian Hindermann
- Eric Decker

## Purpose and Intended Users

**Goal:** Measure how well vision-language models turn tabular personnel index cards into structured records, producing in one pass both a diplomatic transcript of each cell and a normalised interpretation (resolved ditto marks, ISO dates, numeric salaries), and recognising crossed-out entries. The results are meant to guide historians, archivists and digital humanities projects in choosing a model for digitising serial administrative records.

**Audience:**

- AI researchers
- model developers
- industry practitioners

**Tasks:**

- table transcription from images
- resolution of ditto marks and normalisation of dates, salary classes and monetary values
- detection of crossed-out entries

**Limitations:** The backs of 61 cards from a single series of one archive, in German and French; the number of clerks who wrote them is unknown and may approach one per card. Results do not transfer automatically to other card layouts, hands or languages. The interpretation layer follows the conventions in the prompt (`YYYY-MM-DD` dates, numeric salary strings without currency labels, abbreviations left unexpanded), so it measures agreement with those conventions rather than with a neutral standard.

The scorer has properties that bias results (see Calculation):

- A near-match below the 0.92 threshold is penalised as heavily as a wholly wrong value.
- Rows are compared by list position, not by `row_number`; an omitted or inserted row shifts every later comparison.
- Fields the response adds beyond the ground truth count as false positives.

**Out-of-Scope Uses:**

- drawing conclusions about the employees the cards describe
- extracting the personal data on the front of the cards (name, birth, family, education, aptitude), which is not part of the benchmark
- evaluating handwriting recognition on free-form documents
- ranking models on languages other than German and French

## Data

**Source:** Personnel index cards of Swiss federal employees from the Swiss Federal Archives (Schweizerisches Bundesarchiv), series E4260D#05, "Das Dienstverhältnis der Bundesbeamten: Personaldossiers (Serie)": https://www.recherche.bar.admin.ch/recherche/#/de/archiv/einheit/3948547. The benchmark uses the back of each card, a table with one row per change in employment, recording job title, work location, pay grade, salary, date of salary change, and notes on salary supplements.

**Size:** 61 evaluated objects

**Format:** One JPG photograph per card, mostly 2,100–2,600 px wide and 1,450–1,750 px high (one card is photographed upright), 0.3–3 MB, with printed, typed and handwritten entries. The ground truth is one JSON file per card, following the `Table` dataclass in `dataclass.py`. Row 2 of `0002_20230927_105304.json`, where a ditto mark repeats the job title of row 1:

```json
{
  "rows": [
    {
      "row_number": 2,
      "dienstliche_stellung": {
        "diplomatic_transcript": "\"",
        "interpretation": "Hilfsleiter",
        "is_crossed_out": false
      },
      "dienstort": {
        "diplomatic_transcript": "",
        "interpretation": null,
        "is_crossed_out": false
      },
      "gehaltsklasse": {
        "diplomatic_transcript": "",
        "interpretation": null,
        "is_crossed_out": false
      },
      "jahresgehalt_monatsgehalt_taglohn": {
        "diplomatic_transcript": "3'750.-",
        "interpretation": "3750",
        "is_crossed_out": false
      },
      "datum_gehaltsänderung": {
        "diplomatic_transcript": "1. Jan. 1944",
        "interpretation": "1944-01-01",
        "is_crossed_out": false
      },
      "bemerkungen": {
        "diplomatic_transcript": "inkl. 600.-- techn. Z.",
        "interpretation": null,
        "is_crossed_out": false
      }
    }
  ]
}
```

Each cell has three sub-fields:

- `diplomatic_transcript`: the text exactly as written on the card, abbreviations included
- `interpretation`: the resolved ditto mark, normalised date, salary class or numeric amount, or `null`; abbreviations are never expanded
- `is_crossed_out`: whether the entry is struck through on the card

**Annotation:** Tabea Wullschleger, the domain expert, transcribed and interpreted the ground truth by hand, following the extraction and interpretation rules in the [prompt file](prompts/prompt.txt).

**Size Breakdown:**

- image files: 61

**Collection Date:** Source documents: 1941–1961. Added to the benchmark: February 2026.

**Contamination Controls:** None. The images, prompt and ground truth have been public in this repository since February 2026.

## Methodology

**Methods:**

- zero-shot structured extraction from a single image per request
- structured JSON output requested using the `Table` dataclass
- suite-wide default output cap of 16,384 tokens; a test rule can override it and model-specific settings can change it

**Metrics:**

- F1 micro (`f1_micro`, used for ranking)
- F1 macro (`f1_macro`)

**Calculation:** Every terminal field present in the response or the ground truth (for example `rows[0].dienstliche_stellung.diplomatic_transcript`) is compared at the same path; empty strings count as missing. Field values are compared with a rapidfuzz similarity score, and a field is a match at a score of 0.92 or above.

- TP: both have a value and the score is at least 0.92
- FP and FN: both have a value but the score is below 0.92 (the field counts once as each)
- FP: only the response has a value
- FN: only the ground truth has a value

F1 micro sums TP, FP and FN over all cards before computing F1. F1 macro averages the per-card F1 values, each rounded to two decimals.

The `rules` column of `benchmarks_tests.csv` selects which sub-fields are scored; an empty value scores all three:

```json
{
  "score_diplomatic_transcript": true,
  "score_interpretation": true,
  "score_is_crossed_out": true
}
```

`row_number` is never scored and is not used for alignment: rows are compared by list position. A response that does not parse as JSON is skipped rather than scored as zero, so both aggregates cover only scored cards.

**Interpretation:** Scores range from 0 to 1; higher is better. F1 micro weights cards by their number of fields, so long cards count more; F1 macro weights every card equally. The 61 cards contain 209 rows and 1,254 crossed-out flags, of which 1,252 are false. Correct `false` flags earn true positives even for empty cells, so the default combined score can mask poor transcription. Compare runs only under the same field rules.

**Baseline Results:** Model results are available on the [benchmark page](https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/personnel_cards) and in `results/<date>/<test_id>/` at the repository root. Compare runs with the same prompt, scoring rules and ground-truth revision, and report the number of successfully scored objects alongside the score. There is no fixed model baseline with a run ID and date. A diagnostic response that keeps the ground-truth row structure, blanks every transcript and interpretation, and sets every crossed-out flag to `false` scores F1 micro 0.663839 and F1 macro 0.625082 under the default rules. It borrows the row structure from the ground truth and is not an independent extraction baseline.

Observed across models: the interpretation layer, which turns ditto marks, dates, salary classes and amounts into machine-readable values, is particularly useful downstream. Models produce the diplomatic transcript and its interpretation in a single pass, so no separate normalisation step is needed; this shortens the manual post-processing that turns archival data into structured records.

**Validation:** The ground truth was checked by the domain expert, Tabea Wullschleger. Scoring is deterministic; the scorer is covered by `tests/test_f1_scoring.py`.

**Human Baseline:** Not specified

**Judge Uses LLM:** false

**Judge Num:** Not specified

**Judge Models:** Not specified

**Judge Score Consolidation:** Not specified

**Validity Justification:** Field-level F1 reflects the downstream use: each cell becomes a value in a database, so a cell is either usable or needs correction.

## Ethical and Legal Considerations

**Privacy and Anonymity:** The backs of the cards record the employment history and salaries of Swiss federal employees, 1941–1961. They carry no name; the employee's name and personal data are on the front, which is not part of the benchmark. Nothing is anonymised. The people on the cards were born between 1871 and 1926, so all would be at least 100 years old in 2026. The cards are published as made available by the Swiss Federal Archives.

**Data Licensing:** Source material: Public Domain. Ground truth, prompts and other data created for this benchmark: CC BY 4.0.

**Consent Procedures:** Not specified

**Compliance with Regulations:** The cards are federal archival records held by the Swiss Federal Archives and fall under the Federal Act on Archiving (BGA, SR 152.1). Records indexed by personal name that contain sensitive personal data have an extended protection period of 50 years (Art. 11 para. 1 BGA), which ends earlier, three years after the death of the person concerned (Art. 11 para. 2). The latest entry on any card is from 1961, so the 50-year period has expired for every card. No ethical review was carried out.

## Beyond the BenchmarkCard

This section is not part of the BenchmarkCard schema and is not exported to `benchmark_card.json`.

**Versions:**

- 1.0.0 — initial versioned state

**How to Cite:** This benchmark:

> Wullschleger, T., Hindermann, M., & Decker, E. (2026). Personnel Cards (benchmark version 1.0.0). In *RISE Humanities Data Benchmark*. Zenodo. https://doi.org/10.5281/zenodo.16941752

Source:

> Schweizerisches Bundesarchiv, E4260D#05, 1941–1961. Licence of the source material: Public Domain. https://www.recherche.bar.admin.ch/recherche/#/de/archiv/einheit/3948547

The benchmark suite:

> Hindermann, M., Marti, S., Kasper, L. K., & Bosse, A. (2026). The RISE Humanities Data Benchmark: A Framework for Evaluating Large Language Models for Humanities Tasks. *Journal of Open Humanities Data*, *12*(1), 24. https://doi.org/10.5334/johd.481
>
> Hindermann, M., Kasper, L. K., Marti, S., & Bosse, A. (2026). From Experiments to Epistemic Practice: The RISE Humanities Data Benchmark. *Journal of Open Humanities Data*, *12*(1), 38. https://doi.org/10.5334/johd.470

**Contributors by Role:**

- Domain Expert: Tabea Wullschleger
- Data Curator: Tabea Wullschleger
- Annotator: Tabea Wullschleger
- Analyst: Maximilian Hindermann, Tabea Wullschleger
- Engineer: Maximilian Hindermann, Eric Decker
