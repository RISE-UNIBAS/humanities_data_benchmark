# Business Letters

This README is a BenchmarkCard (Sokol et al., NeurIPS 2025, arXiv 2410.12974), schema as in evaleval/auto-benchmarkcard v0.2.0.

<!-- Every field stays, in this order; write 'Not specified' when unknown. Fields marked
     (generated) are filled from meta.json and the benchmark's files by
     `python scripts/benchmark_cards.py <name>`; edit meta.json, not the README, to change them. -->

The scorer is in [benchmark.py](benchmark.py), the requested output schema in [dataclass.py](dataclass.py) and the prompt in [prompts/](prompts/).

To run this benchmark, use `python scripts/run_single_test.py --adhoc` from the repository root and select `business_letters`. Provider setup is described in the [root README](../../README.md#quick-start); configured prompts, models and scoring rules are recorded in [benchmarks_tests.csv](../benchmarks_tests.csv). Provider-backed runs incur API charges.

## Benchmark Details

**Name:** Business Letters

**Overview:** Models extract the send date and the sender and receiver persons from scanned German-language business letters of 1926–1935 held by the Swiss Economic Archives; a name counts when it matches a person's normalised form or one of the spellings recorded for that person.

**Data Type:** image

**Domains:**

- history
- economic history
- correspondence

**Languages:**

- German

**Similar Benchmarks:** Not specified

**Resources:**

- https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/business_letters
- https://github.com/RISE-UNIBAS/humanities_data_benchmark/tree/main/benchmarks/business_letters

**Authors:**

- Eric Decker
- Maximilian Hindermann
- Lea Kasper
- Anthea Alberto
- Pema Frick
- José Luis Losada Palenzuela
- Sorin Marti
- Elena Spadini

## Purpose and Intended Users

**Goal:** Measure how well vision-language models extract correspondence metadata (send date, sender persons, receiver persons) from multi-page business letters, with each name read correctly enough to identify the person. The results are meant to guide historians, archivists and digital humanities projects in choosing a model for cataloguing letters and building correspondence networks from them.

**Audience:**

- humanities researchers
- archivists and librarians
- AI researchers
- model developers

**Tasks:**

- metadata extraction from multi-page letter images
- date normalisation to ISO 8601
- identification of sender and receiver persons
- matching person names to a normalised name form

**Limitations:** The 57 letters come from a single collection on one company, are written in German between 1926 and 1935 and are mostly typewritten; results do not transfer to other archives, hands or languages. Only exact matches count (see Calculation), and the prompt does not ask for the normalised form, so a correct name spelled in a form not recorded in `ground_truths/persons.json` counts as wrong. Persons the annotators inferred from function or from the correspondence history can only be identified from the whole corpus, not from the single letter a request contains; they are excluded from the ground truth, so a model that names one is penalised. The letter title is requested but not scored; organisations and locations are not requested.

**Out-of-Scope Uses:**

- drawing conclusions about the persons and firms named in the letters
- evaluating full-text transcription of letters
- ranking models on languages other than German

## Data

**Source:** Letters from the collection "Basler Rheinschifffahrt-Aktiengesellschaft, insbesondere über die Veräusserung des Dieselmotorbootes 'Rheinfelden' und die Gewährung eines Darlehens zur Finanzierung der Erstellung des Dieselmotorbootes 'Rhyblitz' an diese Firma" of the Swiss Economic Archives (Schweizerisches Wirtschaftsarchiv), shelf mark CH SWA HS 191 V 10, digitised on e-manuscripta: http://dx.doi.org/10.7891/e-manuscripta-54917. The collection holds 68 letters, mostly of one to three pages, on business transactions, shipping and personnel matters; 57 of them have a ground truth and form the benchmark.

**Size:** 57 evaluated objects

**Format:** 98 JPG scans of the letter pages, 2479×3508 px (3 pages in landscape orientation) and about 525 KB each. A letter is one evaluated object; its pages are named `letter<NN>_p<N>.jpg` and sent together in one request. 33 letters have one page, 15 have two, 4 three, 3 four, 1 five and 1 six. The ground truth is one JSON file per letter:

```json
{
    "transkribus_id": "1932319",
    "letter_title": ["None"],
    "send_date": ["1926-02-16"],
    "sender_persons": ["Groschupf-Jaeger, Louis", "Ritter-Dreier, Fritz"],
    "receiver_persons": ["Christ-Wackernagel, Paul"],
    "has_signatures": true
}
```

- `send_date`: the date in ISO 8601 form
- `sender_persons`, `receiver_persons`: normalised names (`Surname, Given name`); `None` when the letter names nobody
- `letter_title`: the title as written, or `None`; not scored
- `transkribus_id`: the letter's document in Transkribus; not used in scoring
- `has_signatures`: whether the letter carries handwritten signatures; used only to select letters for the test variants

`<Name>` marks a person inferred from function and date, `<<Name>>` one inferred from the correspondence history. `ground_truths/persons.json` lists 24 persons with their normalised name and the variants found in the letters (`alternateName`), plus identifiers, life dates, occupations and sources, as [Schema.org Person](https://schema.org/Person) records.

**Annotation:** Anthea Alberto, Eric Decker, Pema Frick, Maximilian Hindermann, Lea Kasper, José Luis Losada Palenzuela, Sorin Marti and Elena Spadini recorded the letters and persons in the [RSF Letters Ground Truth sheet](https://docs.google.com/spreadsheets/d/1qGMVvGZV7GpU11uy0grIffDbGS2rSOj85ziFWZGyuBI/edit?usp=sharing), exported once to the JSON files in `ground_truths/`. These files are now the ground truth and are edited directly: a letter names its persons by their `name` in `persons.json`, and every spelling of a person found in the letters belongs in that person's `alternateName`, since a response name is matched against both. The persons reference list is used by the scorer only; it is not supplied to the model.

**Size Breakdown:**

- image files: 98

**Collection Date:** Source documents: 1926–1935 (16 February 1926 to 17 August 1935). Added to the benchmark: February 2025.

**Contamination Controls:** None. The scans, prompt and ground truth have been public in this repository since February 2025.

## Methodology

**Methods:**

- zero-shot structured extraction from all pages of a letter in one request, prompt `prompts/prompt.txt`, temperature 0.0
- structured JSON output requested using the `Document` dataclass (`metadata` with list-valued `send_date`, `letter_title`, `sender_persons`, `receiver_persons`)
- output cap: the repository default of 16,384 tokens per request
- three test variants, set in the `rules` column of `benchmarks_tests.csv`: no rules (all 57 letters); `{"skip_signatures": true, "skip_non_signatures": false}` (the 25 unsigned letters); `{"skip_signatures": false, "skip_non_signatures": true}` (the 32 signed letters)

**Metrics:**

- F1 macro (`f1_macro`, used for ranking)
- F1 micro (`f1_micro`)

**Calculation:** Three categories are scored per letter: `send_date`, `sender_persons` and `receiver_persons`. Ground truth and response are each turned into a set and compared by exact string equality.

- `send_date`: only the first date of each list is used; a `null` response date is dropped.
- persons: ground-truth persons marked as inferred (`<…>`, `<<…>>`) and `None` are removed. A response name counts as a ground-truth person if it equals the normalised name or appears in that person's `alternateName` list in `persons.json`. `null`, `None` and empty names are dropped.
- TP: in both sets
- FP: only in the response set
- FN: only in the ground-truth set

A response that parses but does not fit the letter structure scores no TP and counts every ground-truth item as FN. A response that cannot be parsed is scored as a miss, like a response that does not fit the letter structure: every ground-truth item counts as FN. TP, FP and FN are summed over all letters per category. F1 micro pools the three categories before computing F1; F1 macro averages the F1 of the three categories. Both are rounded to two decimals.

**Interpretation:** Scores range from 0 to 1; higher is better. F1 macro, the ranking metric, gives the send date, a single item per letter, the same weight as the sender and receiver persons; F1 micro weights categories by their number of items, so persons dominate. The three test variants are scored on different letters, and their scores are not comparable with each other. A low person score can reflect a spelling not recorded in `persons.json` rather than a wrong person (see Limitations). Across the 96 active configurations of each variant, F1 macro has a median of 0.55 (interquartile range 0.51–0.59) on all letters, 0.53 (0.47–0.59) on the unsigned and 0.59 (0.54–0.63) on the signed letters.

**Baseline Results:** Results are on the [benchmark page](https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/business_letters) and in `results/<date>/<test_id>/` at the repository root. No fixed baseline is recorded. Compare runs only with the same prompt, rules and ground-truth revision, and report the number of scored letters with the score.

**Validation:** The source spreadsheet records for each letter who annotated it and who checked it. Scoring is deterministic; the scorer is covered by `tests/test_business_letters_scoring.py`.

**Human Baseline:** Not specified

**Judge Uses LLM:** false

**Judge Num:** Not specified

**Judge Models:** Not specified

**Judge Score Consolidation:** Not specified

**Validity Justification:** Set-based F1 on dates and normalised names reflects the downstream use: a catalogue record or network edge needs the correct date and the correct person, not a near spelling.

## Ethical and Legal Considerations

**Privacy and Anonymity:** The letters name business people, mostly board members and officers of Basel shipping and trading firms, and `persons.json` adds their life dates, occupations and sources. Nothing is anonymised. Where known, the persons were born between 1857 and 1891; the latest letter dates from 1935.

**Data Licensing:** Source material: Public Domain Mark 1.0. Ground truth, prompts and other data created for this benchmark: CC BY 4.0.

**Consent Procedures:** Not specified

**Compliance with Regulations:** The letters are records of a private company held by the Swiss Economic Archives, which publishes the scans on e-manuscripta under the Public Domain Mark 1.0. No ethical review was carried out.

## Beyond the BenchmarkCard

This section is not part of the BenchmarkCard schema and is not exported to `benchmark_card.json`.

<!-- Versions use semantic versioning, newest first, one line each:
     `- MAJOR.MINOR.PATCH (YYYY-MM-DD) — what changed and why`.
     MAJOR: scores before and after are not comparable (ground truth corrected, scoring or
            ranking metric changed, objects added or removed).
     MINOR: something added that leaves existing scores unchanged (e.g. a new prompt variant).
     PATCH: a fix that changes no score (e.g. a better scan of the same image). -->

**Versions:**

- 2.0.0 (2026-10-17) — ground truth kept as JSON only (the CSV exports and their per-run conversion removed), `has_signatures` stored as a boolean; a response that cannot be parsed is scored as a miss instead of being left out; all stored runs re-scored
- 1.0.0 (2026-10-16) — initial versioned state, when the card was introduced; same content as 0.12.0
- 0.12.0 (2026-09-18) — null entries in name lists are dropped, so answers such as `[null]` are scored instead of left out
- 0.11.1 (2026-09-11) — per-field comparison recorded with each answer; scores unchanged
- 0.11.0 (2026-09-09) — answers capped at 32,768 output tokens; an answer that cannot be read as a letter is scored as a miss
- 0.10.3 (2026-04-21) — configurations with empty rules no longer fail
- 0.10.2 (2026-03-23) — configurations without rules no longer fail
- 0.10.1 (2026-03-10) — a failed object is left out of the average instead of stopping the run
- 0.10.0 (2026-02-10) — the alternate names of 2026-02-09 removed again
- 0.9.0 (2026-02-09) — alternate names added for three persons
- 0.8.0 (2025-11-24) — renamed business_letters; answers are parsed by the API client instead of the benchmark; failed requests stop the run again; persons inferred from a job title briefly counted, then left out again
- 0.7.0 (2025-10-17) — requests that fail are saved as empty answers and scored as misses, as are answers that are not valid JSON
- 0.6.1 (2025-09-30) — answers given as encoded strings, empty lists or objects are scored instead of failing
- 0.6.0 (2025-09-24) — prompt corrected ("date" instead of a stray "completions_dir")
- 0.5.0 (2025-04-15) — empty and "None" names no longer count as false positives; F1 rounded to two decimals
- 0.4.0 (2025-04-11) — the sender of letter58 corrected; two alternate names added
- 0.3.1 (2025-04-07) — letters marked for signatures, for new test configurations; scores unchanged
- 0.3.0 (2025-03-07) — alternate names added to the persons list, so more answers match
- 0.2.0 (2025-03-05) — first scorer (F1 over date, senders and receivers); answers without a `metadata` wrapper and null names accepted
- 0.1.0 (2025-03-04) — first state, as metadata_extraction; no scorer yet

**How to Cite:** This benchmark:

> Decker, E., Hindermann, M., Kasper, L., Alberto, A., Frick, P., Losada Palenzuela, J. L., Marti, S., & Spadini, E. (2025). Business Letters (benchmark version 2.0.0). In *RISE Humanities Data Benchmark*. Zenodo. https://doi.org/10.5281/zenodo.16941752

Source:

> Schweizerisches Wirtschaftsarchiv, CH SWA HS 191 V 10, 1926–1935. Licence of the source material: Public Domain Mark 1.0. http://dx.doi.org/10.7891/e-manuscripta-54917

The benchmark suite:

> Hindermann, M., Marti, S., Kasper, L. K., & Bosse, A. (2026). The RISE Humanities Data Benchmark: A Framework for Evaluating Large Language Models for Humanities Tasks. *Journal of Open Humanities Data*, *12*(1), 24. https://doi.org/10.5334/johd.481
>
> Hindermann, M., Kasper, L. K., Marti, S., & Bosse, A. (2026). From Experiments to Epistemic Practice: The RISE Humanities Data Benchmark. *Journal of Open Humanities Data*, *12*(1), 38. https://doi.org/10.5334/johd.470

**Contributors by Role:**

- Domain Expert: Eric Decker, Maximilian Hindermann, Lea Kasper
- Data Curator: Anthea Alberto, Eric Decker, Maximilian Hindermann
- Annotator: Anthea Alberto, Eric Decker, Pema Frick, Maximilian Hindermann, Lea Kasper, José Luis Losada Palenzuela, Sorin Marti, Elena Spadini
- Analyst: Maximilian Hindermann
- Engineer: Maximilian Hindermann
