# Personnel Cards

This README is a BenchmarkCard (Sokol et al., NeurIPS 2025, arXiv 2410.12974), schema as in evaleval/auto-benchmarkcard v0.2.0.

<!-- Every field stays, in this order; write 'Not specified' when unknown. Fields marked
     (generated) are filled from meta.json and the benchmark's files by
     `python scripts/benchmark_cards.py <name>`; edit meta.json, not the README, to change them. -->

## Benchmark Details

**Name:** Personnel Cards

**Overview:** Evaluates models' ability to transcribe and interpret personnel index cards of Swiss federal employees (1941–1961), containing typed and handwritten entries on job title, work location, pay grade, salary, and related notes in German and French.

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

**Goal:** Measure how well vision-language models turn tabular personnel index cards into structured records, producing in one pass both a diplomatic transcript of each cell and a normalised interpretation (expanded abbreviations, ISO dates, numeric salaries), and recognising crossed-out entries. The results are meant to guide historians, archivists and digital humanities projects in choosing a model for digitising serial administrative records.

**Audience:**

- AI researchers
- model developers
- industry practitioners

**Tasks:**

- table transcription from images
- normalisation of abbreviations, dates and monetary values
- detection of crossed-out entries

**Limitations:** 61 cards from a single series of one archive, written in German and French by a small number of clerks; results do not transfer automatically to other card layouts, hands or languages. The interpretation layer follows the conventions in the prompt (e.g. `YYYY-MM-DD` dates, amounts in CHF), so it measures agreement with those conventions rather than a neutral standard. A cell counts as matched only above a fuzzy similarity of 0.92, so near-misses in long cells score the same as wrong answers.

**Out-of-Scope Uses:**

- drawing conclusions about the employees named on the cards
- evaluating handwriting recognition on free-form documents
- ranking models on languages other than German and French

## Data

**Source:** Personnel index cards of Swiss federal employees from the Swiss Federal Archives (Schweizerisches Bundesarchiv), series E4260D#05, "Das Dienstverhältnis der Bundesbeamten: Personaldossiers (Serie)": https://www.recherche.bar.admin.ch/recherche/#/de/archiv/einheit/3948547. Each card is a table with one row per change in employment, recording job title, work location, pay grade, salary, date of salary change, and notes on salary supplements.

**Size:** 61 evaluated objects

**Format:** One JPG photograph per card, about 2500×1700 px and 2 MB each, with typed, handwritten and printed entries. The ground truth is one JSON file per card, following the `Table` dataclass in `dataclass.py`:

```json
{
  "rows": [
    {
      "row_number": 1,
      "dienstliche_stellung": {
        "diplomatic_transcript": "Assist.",
        "interpretation": "Assistant",
        "is_crossed_out": false
      },
      "dienstort": {
        "diplomatic_transcript": "Basel",
        "interpretation": null,
        "is_crossed_out": false
      },
      "gehaltsklasse": {
        "diplomatic_transcript": "III",
        "interpretation": "3",
        "is_crossed_out": false
      },
      "jahresgehalt_monatsgehalt_taglohn": {
        "diplomatic_transcript": "Fr. 2400.-",
        "interpretation": "2400 CHF",
        "is_crossed_out": false
      },
      "datum_gehaltsänderung": {
        "diplomatic_transcript": "1.4.1920",
        "interpretation": "1920-04-01",
        "is_crossed_out": false
      },
      "bemerkungen": {
        "diplomatic_transcript": "",
        "interpretation": null,
        "is_crossed_out": false
      }
    }
  ]
}
```

Each cell has three sub-fields:

- `diplomatic_transcript`: the text exactly as written on the card, abbreviations included
- `interpretation`: the expanded or standardised form, or `null`
- `is_crossed_out`: whether the entry is struck through on the card

**Annotation:** Ground truths were transcribed and interpreted by the domain expert listed under Authors, following the extraction and interpretation rules in the [prompt file](prompts/prompt.txt).

**Size Breakdown:**

- images files: 61

**Collection Date:** The cards date from 1941-1961.

**Contamination Controls:** None. Images and ground truths have been public in this GitHub repository since February 2026.

## Methodology

**Methods:**

- zero-shot structured extraction from a single image per request
- JSON output constrained to the `Table` dataclass

**Metrics:**

- F1 micro (`f1_micro`, used for ranking)
- F1 macro (`f1_macro`)

**Calculation:** Every terminal field of the JSON (for example `rows[0].dienstliche_stellung.diplomatic_transcript`) is compared between the response and the ground truth; empty strings count as missing. Field values are compared with a rapidfuzz similarity score, and a field is a match at a score of 0.92 or above.

- TP: both have a value and the score is at least 0.92
- FP and FN: both have a value but the score is below 0.92 (the field counts once as each)
- FP: only the response has a value
- FN: only the ground truth has a value

F1 micro sums TP, FP and FN over all cards before computing F1. F1 macro averages the per-card F1, each rounded to two decimals.

The `rules` column of `benchmarks_tests.csv` selects which sub-fields are scored; an empty value scores all three:

```json
{
  "score_diplomatic_transcript": true,
  "score_interpretation": true,
  "score_is_crossed_out": true
}
```

`row_number` is never scored.

**Interpretation:** Scores range from 0 to 1; higher is better. F1 micro weights cards by their number of fields, so long cards count more; F1 macro weights every card equally.

**Baseline Results:** Current results for all tested models are on the [benchmark page](https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/personnel_cards) and in the published dataset of runs.

Observed across models: the interpretation layer, which standardises abbreviations, dates and monetary values into machine-readable form, is particularly useful downstream. Models produce the diplomatic transcript and its interpreted form in a single pass, so no separate normalisation step is needed, which shortens the manual post-processing that turns raw archival data into structured records.

**Validation:** Ground truths were checked by the domain expert. Scoring is deterministic; the scorer is covered by the repository's test suite.

**Human Baseline:** Not specified

**Judge Uses LLM:** false

**Judge Num:** Not specified

**Judge Models:** Not specified

**Judge Score Consolidation:** Not specified

**Validity Justification:** Field-level F1 reflects the downstream use: each cell becomes a value in a database, so a cell is either usable or needs correction. Not specified beyond that.

## Ethical and Legal Considerations

**Privacy and Anonymity:** The cards record the employment history and salaries of named Swiss federal employees, 1941-1961. They are not anonymised. The people on the cards were born between 1871 and 1926, so all would be at least 100 years old in 2026. They are published as made available by the Swiss Federal Archives.

**Data Licensing:** Public Domain

**Consent Procedures:** Not specified

**Compliance with Regulations:** The cards are federal archival records held by the Swiss Federal Archives and fall under the Federal Act on Archiving (BGA, SR 152.1). Records indexed by personal name that contain sensitive personal data have an extended protection period of 50 years (Art. 11 para. 1 BGA), which ends earlier, three years after the death of the person concerned (Art. 11 para. 2). The latest entry on any card is from 1961, so the 50-year period has expired for every card. No ethical review was carried out.

## Beyond the BenchmarkCard

This section is not part of the BenchmarkCard schema and is not exported to `benchmark_card.json`.

**Versions:**

- 1 — initial versioned state

**Contributors by Role:**

- Domain Expert: Tabea Wullschleger
- Data Curator: Tabea Wullschleger
- Annotator: Tabea Wullschleger
- Analyst: Maximilian Hindermann, Tabea Wullschleger
- Engineer: Maximilian Hindermann, Eric Decker
