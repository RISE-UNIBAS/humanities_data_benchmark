# General Meeting Minutes

This README is a BenchmarkCard (Sokol et al., NeurIPS 2025, arXiv 2410.12974), schema as in evaleval/auto-benchmarkcard v0.2.0.

<!-- Every field stays, in this order; write 'Not specified' when unknown. Fields marked
     (generated) are filled from meta.json and the benchmark's files by
     `python scripts/benchmark_cards.py <name>`; edit meta.json, not the README, to change them. -->

The scoring implementation is in [benchmark.py](benchmark.py), the requested output schema in [dataclass.py](dataclass.py), and the instructions in [prompts/](prompts/).

To run this benchmark, use `python scripts/run_single_test.py --adhoc` from the repository root and select `general_meeting_minutes`. Provider setup is described in the [root README](../../README.md#quick-start); configured prompts, models and scoring rules are recorded in [benchmarks_tests.csv](../benchmarks_tests.csv). Provider-backed runs incur API charges.

## Benchmark Details

**Name:** General Meeting Minutes

**Overview:** Evaluates models' ability to extract shareholder rows (names, addresses, share counts, votes and signatures) and page totals from the attendance registers of the general meetings of Mines de Costano S.A., 1951–1968.

**Data Type:** image

**Domains:**

- business history
- economic history
- archival science

**Languages:**

- Italian
- French
- German

**Similar Benchmarks:** Not specified

**Resources:**

- https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/general_meeting_minutes
- https://github.com/RISE-UNIBAS/humanities_data_benchmark/tree/main/benchmarks/general_meeting_minutes

**Authors:**

- Alexandra Binnenkade
- Sven Lienhard
- Sorin Marti

## Purpose and Intended Users

**Goal:** Measure how well vision-language models turn the attendance registers of a company's general meetings, printed forms filled in by typewriter and by hand, into structured records: one row per shareholder with name and address split apart, share counts by class, votes, and the presence and text of a signature, plus the carried-forward totals. The results are meant to guide historians, archivists and digital humanities projects in choosing a model for digitising tabular business records.

**Audience:**

- AI researchers
- model developers
- industry practitioners

**Tasks:**

- table extraction from page images
- splitting a combined name-and-address cell into two fields
- detection and transcription of handwritten signatures
- transcription of share counts and page totals

**Limitations:** Nine pages from the registers of a single company, 1951–1968, 85 rows in all; results do not transfer automatically to other forms, hands or record types. Several images are two-page spreads, so the number of rows per image varies from 6 to 20.

The scorer has several blind spots:

- Rows are compared by position (`entries[0]` with `entries[0]`), not by row number or name. A model that skips or inserts one row is scored against the wrong ground-truth row for every row after it.
- Only fields present in the ground truth are scored. Rows the model adds beyond the last ground-truth row cost nothing.
- About a fifth of the scored fields are empty strings (empty share columns, missing totals, absent signatures); a model that returns `""` there scores 1.0 for them.
- `document` and `page_number` are given in the prompt, so they are close to free points.
- A wrong `signature_present` value scores 0.22, not 0, because the booleans are compared as the strings `True` and `False`.
- Scores are similarities, not matches: a field that is 80% similar contributes 0.8, so mean scores look higher than a thresholded F1 would.

Some ground-truth files write the degree sign as the literal text `U+00B0` (15 times on four pages), so a model that writes `°` loses a little similarity in those addresses.

**Out-of-Scope Uses:**

- evaluating signature verification or writer identification
- evaluating arithmetic on the share columns (totals must be transcribed, not computed)
- drawing conclusions about the shareholders named in the registers

## Data

**Source:** Attendance registers of the general meetings of Mines de Costano S.A., the company that operated the gold mine of Sessa (Malcantone, Ticino) from 1933, from the company's private archive. Each page is a printed form with the columns *N° d'ordre*, *Nom, prénoms et domicile des actionnaires*, *Actions* (two columns, *de priorité* and *ordinaire*, whose order varies between forms), *Nombre de voix* and *Signature des actionnaires ou des mandataires*, with a carried-forward total (*report*, *à reporter*). Names and addresses are typed; share counts and totals are typed or handwritten; signatures are handwritten.

**Size:** 9 evaluated objects

**Format:** One JPG per page or two-page spread, 2,263–2,480 px wide, 2,975–3,509 px high and 0.9–2 MB. The ground truth is one JSON file per image, following the `MinutesPage` dataclass in `dataclass.py`:

```json
{
  "document": "Se_19_Assemblée Mine d. Costano_2.9_12.1962_page_4",
  "page_number": 4,
  "entries": [
    {
      "number": "1",
      "name": "M. BREHAM Alain",
      "address": "45 Boulevard Charcot - Neuilly s/Seine (Seine",
      "actions_o": "179",
      "actions_p": "520",
      "no_de_voix": "699",
      "signature_present": true,
      "signature": "Pa"
    }
  ],
  "total_actions": {"total_o": "659", "total_p": "2310", "total_voix": "2964"}
}
```

- `document`, `page_number`: taken from the file name and passed to the model in the prompt
- `entries`: one object per table row; `name` and `address` come from the same cell and are split into two fields; every value except `signature_present` is a string, empty when the cell is empty
- `total_actions`: the totals written at the foot of the page, empty strings where none are written

**Annotation:** Sven Lienhard (annotator) transcribed and curated the ground truth by hand: diplomatic transcription without added accents, line breaks inside addresses kept, the dash separating name and address removed, totals transcribed only where written on the page.

**Size Breakdown:**

- image files: 9

**Collection Date:** Source documents: 1951–1968 (the file names give 1951, 1961, 1962, 1965, 1967 and 1968; for the `Bilanz` files the year may be that of the balance sheet rather than of the meeting). Added to the benchmark: March 2026.

**Contamination Controls:** None. The images, prompts and ground truth have been public in this repository since March 2026.

## Methodology

**Methods:**

- zero-shot structured extraction from a single page image per request, with the file name and page number given in the prompt
- structured JSON output requested using the `MinutesPage` dataclass
- benchmark default output cap of 40,960 tokens; test rules can override it and model-specific ceilings can lower it
- five prompt variants: `prompt.txt` (short instructions on splitting name and address) is the main cross-model variant; `extended_prompt.txt`, `prompt_first_reformulated.txt`, `updated_prompt.txt` and `updated_prompt_steps.txt` (longer rules on transcription fidelity, column order, totals and signatures) each have three configured tests. The variants have not been compared under controlled conditions, and scores are comparable across models only within one prompt
- no shared context: nothing in `context/` is sent, and signatures are scored as ordinary fields

**Metrics:**

- Fuzzy similarity (`fuzzy`, used for ranking)

**Calculation:** For each page, every terminal field of the ground-truth JSON is enumerated (`document`, `page_number`, `entries[i].*`, `total_actions.*`) and the response value at the same path is compared with it:

- identical values (including two empty strings, or the same number as integer and string) score 1.0
- a value missing from the response (path absent or `null`) scores 0.0
- otherwise the score is the rapidfuzz `ratio` of the two values as strings, divided by 100, case-sensitive and unnormalised

The page score is the unrounded mean over its fields; the benchmark score is the mean of the page scores, so every page weighs the same whatever its number of rows. A response that is not parseable JSON is left out of the mean rather than scored as zero.

**Interpretation:** Scores range from 0 to 1; higher is better. Partial credit and free empty fields (see Limitations) make absolute scores run high, so compare models with each other rather than against a fixed bar. A low score on one page often means a skipped or inserted row rather than poor reading, because the rows after it are misaligned.

**Baseline Results:** Model results are available on the [benchmark page](https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/general_meeting_minutes) and in `results/<date>/<test_id>/` at the repository root. Compare runs with the same prompt, scoring rules and ground-truth revision, and report the number of successfully scored objects alongside the score. There is no fixed model baseline with a run ID and date.

**Validation:** The ground truth was created by Sven Lienhard, annotator and domain expert; no second check is recorded. Scoring is deterministic; the scorer has no dedicated test.

**Human Baseline:** Not specified

**Judge Uses LLM:** false

**Judge Num:** Not specified

**Judge Models:** Not specified

**Judge Score Consolidation:** Not specified

**Validity Justification:** Not specified

## Ethical and Legal Considerations

**Privacy and Anonymity:** The registers name shareholders and their proxies, private persons and companies, with their home addresses, share holdings and signatures, 1951–1968. They are not anonymised. They are company records of shareholdings, and publishing them raises no personal-rights issue.

**Data Licensing:** Free use

**Consent Procedures:** Not specified

**Compliance with Regulations:** The registers come from the company's private archive, so no public archival law sets a protection period for them; they are used under the archive's grant of free use. No separate reuse terms are stated for the ground truth. No ethical review was carried out.

## Beyond the BenchmarkCard

This section is not part of the BenchmarkCard schema and is not exported to `benchmark_card.json`.

<!-- Versions use semantic versioning, newest first, one line each: `- MAJOR.MINOR.PATCH — what
     changed and why`.
     MAJOR: scores before and after are not comparable (ground truth corrected, scoring or
            ranking metric changed, objects added or removed).
     MINOR: something added that leaves existing scores unchanged (e.g. a new prompt variant).
     PATCH: a fix that changes no score (e.g. a better scan of the same image). -->

**Versions:**

- 1.0.0 — initial versioned state

**How to Cite:** This benchmark:

> Binnenkade, A., Lienhard, S., & Marti, S. (2026). General Meeting Minutes (benchmark version 1.0.0). In *RISE Humanities Data Benchmark*. Zenodo. https://doi.org/10.5281/zenodo.16941752

Source:

> Mines de Costano S.A., private archive, 1951–1968. Licence: Free use.

The benchmark suite:

> Hindermann, M., Marti, S., Kasper, L. K., & Bosse, A. (2026). The RISE Humanities Data Benchmark: A Framework for Evaluating Large Language Models for Humanities Tasks. *Journal of Open Humanities Data*, *12*(1), 24. https://doi.org/10.5334/johd.481
>
> Hindermann, M., Kasper, L. K., Marti, S., & Bosse, A. (2026). From Experiments to Epistemic Practice: The RISE Humanities Data Benchmark. *Journal of Open Humanities Data*, *12*(1), 38. https://doi.org/10.5334/johd.470

**Contributors by Role:**

- Domain Expert: Alexandra Binnenkade, Sven Lienhard
- Data Curator: Sven Lienhard
- Annotator: Sven Lienhard
- Analyst: Sven Lienhard, Sorin Marti
- Engineer: Sorin Marti
