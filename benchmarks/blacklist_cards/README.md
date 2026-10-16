# Blacklist Cards

This README is a BenchmarkCard (Sokol et al., NeurIPS 2025, arXiv 2410.12974), schema as in evaleval/auto-benchmarkcard v0.2.0.

<!-- Every field stays, in this order; write 'Not specified' when unknown. Fields marked
     (generated) are filled from meta.json and the benchmark's files by
     `python scripts/benchmark_cards.py <name>`; edit meta.json, not the README, to change them. -->

The scoring implementation is in [benchmark.py](benchmark.py), the requested output schema in [dataclass.py](dataclass.py), and the instructions in [prompts/](prompts/).

To run this benchmark, use `python scripts/run_single_test.py --adhoc` from the repository root and select `blacklist_cards`. Provider setup is described in the [root README](../../README.md#quick-start); configured prompts, models and scoring rules are recorded in [benchmarks_tests.csv](../benchmarks_tests.csv). Provider-backed runs incur API charges.

## Benchmark Details

**Name:** Blacklist Cards

**Overview:** Index cards of companies on a British 'black list' in the 1940s. Assesses models' capability to recognize typed and handwritten information from index cards.

**Data Type:** image

**Domains:**

- history
- economic history
- archival science

**Languages:**

- German

**Similar Benchmarks:** Not specified

**Resources:**

- https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/blacklist_cards
- https://github.com/RISE-UNIBAS/humanities_data_benchmark/tree/main/benchmarks/blacklist_cards

**Authors:**

- Lea Kasper
- Sorin Marti

## Purpose and Intended Users

**Goal:** Measure how well vision-language models extract the fields of a uniform, mostly typewritten index card into a structured record: separating company name from location, reading the identification number, normalising a stamped date, and transcribing the text blocks that record when a firm was put on and taken off the British blacklist. The results are meant to guide historians, archivists and digital humanities projects in choosing a model for digitising large series of uniform index cards.

**Audience:**

- AI researchers
- model developers
- industry practitioners

**Tasks:**

- field extraction from index card images
- transcription of typed and handwritten text blocks
- date normalisation to `YYYY-MM-DD`

**Limitations:** 33 cards from one record series of one archive, all following the same layout; results do not transfer automatically to other card types. The ground truth was drafted by a model and then corrected by hand, so it may lean towards that model's reading where the card is ambiguous. Blocks in `information` are compared by position, so a merged, split or reordered block lowers the score of every block after it; blocks beyond those in the ground truth cost nothing. Empty fields are scored too: 27 of 33 cards have no stamped date, and a response that also leaves `date` empty gets full marks for it, so an all-empty response already scores about 0.15. The split of company and location, and the omitted commas and periods, follow the annotators' conventions rather than a stated standard. The test CSV requests temperature 0.5, but the runner overrides or omits temperature for some models. Repeated-run uncertainty is not reported here.

**Out-of-Scope Uses:**

- drawing conclusions about the firms or persons named on the cards
- assessing the historical blacklisting itself
- evaluating handwriting recognition on free-form documents

## Data

**Source:** Index cards from the Swiss Federal Archives (Schweizerisches Bundesarchiv), signature E2001E#1968/78#7508*: https://www.recherche.bar.admin.ch/recherche/#/de/archiv/einheit/31240458. The record documents Swiss firms and individuals put on the British trade blacklist during the Second World War; it comprises over 1,000 cards. Each card gives the name and location in the top left, an identification number (`B.51.322.GB.…`) in the top right, and in the body the amendment of the blacklist that added the entry and the one that removed it ("gestrichen"), sometimes with notes on the French list.

**Size:** 33 evaluated objects

**Format:** One JPG scan per card, about 1780–1860 × 1290–1320 px and 590 KB on average, mostly typewritten in German. Handwritten notes on the French blacklist ("fig. noch auf franz. Liste…") are transcribed, even where struck through; other handwritten annotations, mostly references to supplementary material, were left out. The ground truth is one JSON file per card, following the `Card` dataclass in `dataclass.py`:

```json
{
  "b_id": { "transcription": "B.51.322.GB.638" },
  "company": { "transcription": "ARIA, Automobil-Reifen-Import A.G." },
  "date": "1942-08-06",
  "information": [
    { "transcription": "Britische schwarze Liste\nAmendment 12, Juli 1942." },
    { "transcription": "gestrichen:\nAmendment 13, 23. November 1945." }
  ],
  "location": { "transcription": "Zürich" }
}
```

- `company`, `location`, `b_id`: transcribed as written; always present
- `date`: a stamped date in `YYYY-MM-DD`, or an empty string (27 of 33 cards)
- `information`: the text blocks of the card body in reading order, line breaks kept as `\n`; 0–4 blocks per card

**Annotation:** The ground truth was drafted by running the benchmark with the dataclass, most likely with one of the two models configured when the benchmark was added (Gemini 2.5 Flash preview or GPT-4.1; which one is not recorded), then reviewed and corrected item by item by the annotators listed under Contributors by Role. Commas after names and periods after locations were omitted. Dates in `information` are transcribed, not normalised.

**Size Breakdown:**

- images files: 33

**Collection Date:** Not specified for benchmark collection or digitisation. Source-document dates: The cards record blacklist amendments from 1940 to 1946.

**Contamination Controls:** No held-out private split, training-data audit or other contamination control is documented. Inputs, prompts and ground truths are distributed together in this public repository. Whether any evaluated model saw these materials during training is unknown.

## Methodology

**Methods:**

- zero-shot structured extraction from a single image per request
- structured JSON output requested using the `Card` dataclass
- configured temperature 0.5, subject to model-specific overrides in `scripts/benchmark_base.py`

**Metrics:**

- Fuzzy similarity (`fuzzy`, used for ranking)

**Calculation:** Every terminal field of the ground truth (for example `company.transcription` or `information[1].transcription`) is looked up at the same path in the response. Fields only in the response are ignored. `None` and the string `"null"` are treated as empty strings on both sides.

- identical values score 1.0, including two empty strings
- otherwise the score is the rapidfuzz `ratio` divided by 100, between 0 and 1; there is no threshold, and an empty value against a non-empty one scores 0

The card score is the mean over that card's fields. The benchmark score is the mean of the card scores. A response that cannot be parsed into the schema is not scored and does not enter the mean.

**Interpretation:** Scores range from 0 to 1; higher is better. Partial string similarity earns partial credit, so small slips (a missing period in the identification number) cost little. A response with every field empty scores about 0.15.

**Baseline Results:** Model results are available on the [benchmark page](https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/blacklist_cards) and in `results/<date>/<test_id>/` at the repository root. Compare runs with the same prompt, scoring rules and ground-truth revision, and report the number of successfully scored objects alongside the score. No fixed model baseline with a run ID and date is specified here. An empty parsed object scores 0.153535 on the 33 current ground truths because missing values are normalised to empty strings; this is a scorer diagnostic, not a schema-valid model response.

Observed across models: models separate company name and location, extract the identification number and transcribe the two dated lines reliably. The transcribed dates are not yet normalised, which can be done in a later processing step to turn them into structured dates for analysis.

**Validation:** Every ground truth item was reviewed and corrected by hand after the model draft. Scoring is deterministic; the scorer is covered by the repository's test suite.

**Human Baseline:** Not specified

**Judge Uses LLM:** false

**Judge Num:** Not specified

**Judge Models:** Not specified

**Judge Score Consolidation:** Not specified

**Validity Justification:** Field-level similarity reflects the downstream use: each card becomes a database record, and near-misses need less correction than wrong values. Not specified beyond that.

## Ethical and Legal Considerations

**Privacy and Anonymity:** The cards name the firms and, on 13 of the 33 cards, individuals (some with business addresses) who were placed on the British blacklist in 1940–1946. They are not anonymised. Firms are not natural persons. Birth dates are not on the cards, but anyone economically active in 1940–1946 was very likely born before 1926 and would be at least 100 years old in 2026. The Swiss Federal Archives have made the record freely accessible since 1978.

**Data Licensing:** Public Domain

**Consent Procedures:** Not specified

**Compliance with Regulations:** The cards are federal archival records held by the Swiss Federal Archives and fall under the Federal Act on Archiving (BGA, SR 152.1). The archive's record assigns them the ordinary protection period of 30 years (Art. 9 para. 1 BGA), which ended in 1978; no extended protection for personal data applies. As official records they carry no copyright and are used as public domain. No separate reuse terms are stated for the ground truths. No ethical review was carried out.

## Beyond the BenchmarkCard

This section is not part of the BenchmarkCard schema and is not exported to `benchmark_card.json`.

**Versions:**

- 1.0.0 — initial versioned state

**Contributors by Role:**

- Domain Expert: Lea Kasper
- Data Curator: Sorin Marti
- Annotator: Lea Kasper, Sorin Marti
- Analyst: Lea Kasper, Sorin Marti
- Engineer: Sorin Marti
