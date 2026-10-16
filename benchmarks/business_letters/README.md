# Business Letters

This README is a BenchmarkCard (Sokol et al., NeurIPS 2025, arXiv 2410.12974), schema as in evaleval/auto-benchmarkcard v0.2.0.

<!-- Every field stays, in this order; write 'Not specified' when unknown. Fields marked
     (generated) are filled from meta.json and the benchmark's files by
     `python scripts/benchmark_cards.py <name>`; edit meta.json, not the README, to change them. -->

The scoring implementation is in [benchmark.py](benchmark.py), the requested output schema in [dataclass.py](dataclass.py), and the instructions in [prompts/](prompts/).

To run this benchmark, use `python scripts/run_single_test.py --adhoc` from the repository root and select `business_letters`. Provider setup is described in the [root README](../../README.md#quick-start); configured prompts, models and scoring rules are recorded in [benchmarks_tests.csv](../benchmarks_tests.csv). Provider-backed runs incur API charges.

## Benchmark Details

**Name:** Business Letters

**Overview:** Tests models on extracting correspondence metadata (send date, sender and receiver persons) from 20th century Swiss business letters, resolving names to a reference list of persons.

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

**Goal:** Measure how well vision-language models extract correspondence metadata (send date, sender persons, receiver persons) from multi-page business letters, and resolve the names they find to the normalised persons of a reference list. The results are meant to guide historians, archivists and digital humanities projects in choosing a model for cataloguing letters and building correspondence networks from them.

**Audience:**

- AI researchers
- model developers
- industry practitioners

**Tasks:**

- metadata extraction from multi-page letter images
- date normalisation to ISO 8601
- identification of sender and receiver persons
- matching person names to a normalised name form

**Limitations:** 57 letters from a single collection of one company, written in German between 1926 and 1935 and mostly typewritten; results do not transfer automatically to other archives, hands or languages. Only exact matches count: a date scores only if it equals the ground truth string, and a name scores only if it equals the normalised form (`Surname, Given name`) or one of the variants recorded for that person in `ground_truths/persons.json`. The prompt does not ask for the normalised form, so a correct name spelled in a form nobody recorded counts as wrong. Persons the annotators inferred from function or correspondence history are left out of the ground truth, so a model that names them is penalised. The letter title is requested but not scored. The current prompt and schema do not request organisation fields.

**Out-of-Scope Uses:**

- drawing conclusions about the persons and firms named in the letters
- evaluating full-text transcription of letters
- ranking models on languages other than German

## Data

**Source:** Letters from the collection "Basler Rheinschifffahrt-Aktiengesellschaft, insbesondere über die Veräusserung des Dieselmotorbootes 'Rheinfelden' und die Gewährung eines Darlehens zur Finanzierung der Erstellung des Dieselmotorbootes 'Rhyblitz' an diese Firma" of the Swiss Economic Archives (Schweizerisches Wirtschaftsarchiv), shelf mark CH SWA HS 191 V 10, digitised on e-manuscripta: http://dx.doi.org/10.7891/e-manuscripta-54917. The collection holds 68 letters, mostly of one to three pages, on business transactions, shipping and personnel matters; 57 of them have a ground truth.

**Size:** 57 evaluated objects

**Format:** JPG scans of the letter pages, 2479×3508 px and about 500 KB each. A letter is one evaluated object; its pages are named `letter<NN>_p<N>.jpg` and sent together in one request. 33 letters have one page, 15 two, 4 three, 3 four, one five and one six. The ground truth is one JSON file per letter:

```json
{
    "letter_title": ["None"],
    "send_date": ["1926-02-16"],
    "sender_persons": ["Groschupf-Jaeger, Louis", "Ritter-Dreier, Fritz"],
    "receiver_persons": ["Christ-Wackernagel, Paul"],
    "has_signatures": "TRUE"
}
```

- `send_date`: the date in ISO 8601 form
- `sender_persons`, `receiver_persons`: normalised names; `None` when the letter names nobody
- `letter_title`: the title as written, or `None`; not scored
- `has_signatures`: whether the letter is signed; used only to select letters for the test variants

`<Name>` marks a person inferred from function and date, `<<Name>>` one inferred from the correspondence history. `ground_truths/persons.json` lists 24 persons with their normalised name and the variants found in the letters (`alternateName`), plus life dates, occupations and sources in Schema.org form.

**Annotation:** Annotators recorded the letters in a shared spreadsheet with a persons tab (normalised names, inscribed variants, identifiers such as GND) and a letters tab, following the conventions in [ground_truth_persons_organizations.md](ground_truth_persons_organizations.md). The persons reference list is used by the scorer; it is not supplied to the model as context. Both tabs are exported to `ground_truths/persons.csv` and `ground_truths/letters.csv`; every run regenerates the JSON files from these CSV files.

**Size Breakdown:**

- images files: 98

**Collection Date:** Not specified for benchmark collection or digitisation. Source-document dates: The letters are dated 1926-02-16 to 1935-08-17.

**Contamination Controls:** No held-out private split, training-data audit or other contamination control is documented. Inputs, prompts and ground truths are distributed together in this public repository. Whether any evaluated model saw these materials during training is unknown.

## Methodology

**Methods:**

- zero-shot structured extraction from all pages of a letter in one request
- structured JSON output requested using the `Document` dataclass (`metadata` with list-valued `send_date`, `letter_title`, `sender_persons`, `receiver_persons`)

**Metrics:**

- F1 macro (`f1_macro`, used for ranking)
- F1 micro (`f1_micro`)

**Calculation:** Three categories are scored per letter: `send_date`, `sender_persons` and `receiver_persons`. Each side is turned into a set and compared exactly.

- `send_date`: only the first date of each list is used. The response date is dropped if it is `null`.
- persons: ground truth persons marked as inferred (`<…>`, `<<…>>`) and `None` are removed. A response name counts as the ground truth person's name if it equals it or appears in that person's `alternateName` list in `persons.json`. `null`, `None` and empty names are dropped.
- TP: in both sets
- FP: only in the response set
- FN: only in the ground truth set

A parsed response that reaches this scorer but cannot be converted into a letter scores no TP and every ground-truth item as FN. In a normal schema-configured run, an unparseable response (`answer.parsed is None`) is skipped by the shared runner before this scorer is called, and does not enter either F1 aggregate. TP, FP and FN are summed over all letters per category. F1 micro pools the three categories before computing F1; F1 macro averages the F1 of the three categories. Both are rounded to two decimals.

The `rules` column of `benchmarks_tests.csv` defines three test variants:

- no rules: all 57 letters
- `{"skip_signatures": true, "skip_non_signatures": false}`: only the 25 letters without signatures
- `{"skip_signatures": false, "skip_non_signatures": true}`: only the 32 letters with signatures

**Interpretation:** Scores range from 0 to 1; higher is better. F1 macro, the ranking metric, gives the send date, which is a single item per letter, the same weight as the sender and receiver persons; F1 micro weights categories by their number of items, so persons dominate. Scores of the three variants are computed on different letters and are not directly comparable with each other.

**Baseline Results:** Model results are available on the [benchmark page](https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/business_letters) and in `results/<date>/<test_id>/` at the repository root. Compare runs with the same prompt, scoring rules and ground-truth revision, and report the number of successfully scored objects alongside the score. No fixed model baseline with a run ID and date is specified here.

**Validation:** Each letter's ground truth names the annotator responsible for it in the source spreadsheet; the current CSV-to-JSON exporter writes every row of `letters.csv` and does not itself filter a completion-status column. Scoring is deterministic; the scorer is covered by the repository's test suite.

**Human Baseline:** Not specified

**Judge Uses LLM:** false

**Judge Num:** Not specified

**Judge Models:** Not specified

**Judge Score Consolidation:** Not specified

**Validity Justification:** Set-based F1 on dates and normalised names reflects the downstream use: a catalogue record or network edge needs the correct date and the correct person, not a near spelling. Not specified beyond that.

## Ethical and Legal Considerations

**Privacy and Anonymity:** The letters name business people, mostly board members and officers of Basel shipping and trading firms, and `persons.json` adds their life dates, occupations and sources. Nothing is anonymised. Where known, the persons were born between 1857 and 1891, and the latest letter dates from 1935.

**Data Licensing:** Public Domain Mark 1.0

**Consent Procedures:** Not specified

**Compliance with Regulations:** The letters are records of a private company held by the Swiss Economic Archives, which publishes the scans on e-manuscripta under the Public Domain Mark 1.0. No separate reuse terms are stated for the ground truths. No ethical review was carried out.

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

- Domain Expert: Eric Decker, Maximilian Hindermann, Lea Kasper
- Data Curator: Anthea Alberto, Eric Decker, Maximilian Hindermann
- Annotator: Anthea Alberto, Eric Decker, Pema Frick, Maximilian Hindermann, Lea Kasper, José Luis Losada Palenzuela, Sorin Marti, Elena Spadini
- Analyst: Maximilian Hindermann
- Engineer: Maximilian Hindermann
