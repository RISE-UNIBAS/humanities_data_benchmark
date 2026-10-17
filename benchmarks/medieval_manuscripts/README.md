# Medieval Manuscripts

This README is a BenchmarkCard (Sokol et al., NeurIPS 2025, arXiv 2410.12974), schema as in evaleval/auto-benchmarkcard v0.2.0.

<!-- Every field stays, in this order; write 'Not specified' when unknown. Fields marked
     (generated) are filled from meta.json and the benchmark's files by
     `python scripts/benchmark_cards.py <name>`; edit meta.json, not the README, to change them. -->

The scorer is in [benchmark.py](benchmark.py), the output schema in [dataclass.py](dataclass.py) and the prompt in [prompts/](prompts/).

To run it, call `python scripts/run_single_test.py --adhoc` from the repository root and select `medieval_manuscripts`. Provider setup is described in the [root README](../../README.md#quick-start); the configured tests (model, prompt, rules) are in [benchmarks_tests.csv](../benchmarks_tests.csv). Runs against a provider incur API charges.

## Benchmark Details

**Name:** Medieval Manuscripts

**Overview:** Evaluates models on the diplomatic transcription of pages from a mid-15th-century manuscript in late medieval German, the pilgrimage accounts of Hans and Peter Rot held by the Universitätsbibliothek Basel (H V 15). The model must keep historical spelling and abbreviations, identify the folio number, and separate main text from marginal additions without being given their regions (an implicit segmentation).

**Data Type:** image

**Domains:**

- history
- medieval studies
- palaeography

**Languages:**

- German

**Similar Benchmarks:** Not specified

**Resources:**

- https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/medieval_manuscripts
- https://github.com/RISE-UNIBAS/humanities_data_benchmark/tree/main/benchmarks/medieval_manuscripts

**Authors:**

- Ina Serif
- Maximilian Hindermann

## Purpose and Intended Users

**Goal:** Measure how well vision-language models produce a diplomatic transcription of late medieval German handwriting: the main text block, the folio number and each marginal addition as separate fields, with historical spelling kept and abbreviations left unresolved. The results are meant for AI researchers and model developers comparing models on historical handwriting, and for practitioners in historical research, archives and digital humanities choosing a model to transcribe medieval manuscripts.

**Audience:**

- AI researchers
- model developers
- industry practitioners

**Tasks:**

- diplomatic transcription of handwritten text from images
- separation of main text, folio number and marginal additions

**Limitations:** 12 pages from a single manuscript, written by two scribes in one regional variety of German; results do not transfer automatically to other scripts, hands, languages or layouts. The transcription conventions (superscript letters written after the base letter, MUFI characters for abbreviation signs) are those of the prompt and the annotator, so the score measures agreement with them. Several scoring properties bias results (see Calculation): only the first entry of the response is scored, so a model that splits a page into several entries is scored on the first alone; marginal additions beyond those keyed in the ground truth are ignored; the page score weights the one- or two-character folio number as much as a main text of several hundred characters; and a response that cannot be parsed is left out of the average rather than scored as a failure, so a model's average covers only the pages it answered in valid JSON.

**Out-of-Scope Uses:**

- evaluating expansion of abbreviations or normalisation to modern German
- evaluating text in other languages or scripts
- evaluating page segmentation as a geometric task (no regions or coordinates are scored)

## Data

**Source:** Pages of Basel, Universitätsbibliothek, H V 15, "Hans and Peter Roth, Pilgrimages to Jerusalem 1440 and 1453", digitised by e-codices: https://www.e-codices.unifr.ch/en/list/one/ubb/H-V-0015. The small parchment manuscript (105 folios, 14 × 10.5 cm) contains the accounts of Hans Rot († 1452) and his son Peter Rot († 1487) of their pilgrimages to the Holy Land, possibly in their own hands. The 12 pages are folios 3r, 4v, 9v, 18r, 23v, 52v, 62v, 69r, 70v, 73r, 90r and 93r.

**Size:** 12 evaluated objects

**Format:** One JPG image per page, 1872×2808 px and 1.1–1.3 MB each. The ground truth is one JSON file per page, keyed by the folio reference, with one entry holding the folio number as written on the page (empty if none is visible), the main text with line breaks as `
`, and one field per marginal addition. The response follows the `Document` dataclass in `dataclass.py`: a list `folios` of such entries, with fields `addition1` to `addition3`.

```json
{
  "[9v]": [
    {
      "folio": "",
      "text": "vnd die insel ist bi ccc mil
 wit vnd ist der venediger
 Itꝰ von kurfun vntz gon
 ...",
      "addition1": "Candia vff
 Creta",
      "addition2": "Virum
 Malva
 ricum",
      "addition3": "Rhodꝰ."
    }
  ]
}
```

Main texts are 274–710 characters long. Five pages carry a folio number; six have at least one marginal addition. Every ground-truth file has an `addition1` field, empty where the page has no addition; only the page shown above has more than one.

**Annotation:** Transcribed by Ina Serif (domain expert) following the transcription rules in the [prompt file](prompts/prompt.txt): historical spelling kept, abbreviations not resolved, superscript letters written after the base letter (e.g. `uo`), abbreviation signs as MUFI characters such as `ꝛ` and `ꝰ`.

**Size Breakdown:**

- image files: 12

**Collection Date:** Source documents: mid-15th century; the pilgrimages described took place in 1440 and 1453. Added to the benchmark: October 2025.

**Contamination Controls:** None. The images, prompt and ground truth have been public in this repository since October 2025.

## Methodology

**Methods:**

- one page image per request with the prompt [`prompt.txt`](prompts/prompt.txt), the only variant; it includes an illustrative output example, and no benchmark page is supplied as a demonstration
- all tests use temperature 0 and the same system role (a historian with expertise in medieval manuscripts and palaeography)
- structured JSON output requested with the `Document` dataclass
- output capped at the repository default of 16,384 tokens per request, adjusted per model in `scripts/benchmark_base.py`

**Metrics:**

- Character Error Rate (`cer`, used for ranking)
- fuzzy similarity (`fuzzy`)

**Calculation:** Ground-truth entries are sorted by folio reference and matched by position to the entries of the response's `folios` list; every page has one entry, so it is matched to the first response entry. If the response has no entry, every compared field of the page gets fuzzy 0 and CER 1. Within the entry, these fields are compared:

- `folio`, when the ground truth or the response has a value
- `text`, always
- consecutive `addition1` through at most `addition9`, stopping at the first missing or null ground-truth addition; a visited addition is scored when either side has a value

None, empty and whitespace-only values are treated as empty. For each compared field two values are computed, each rounded to three decimals:

- fuzzy: the rapidfuzz ratio of the two strings divided by 100, case- and whitespace-sensitive; 1.0 for identical strings
- CER: both strings are lowercased and runs of whitespace (including line breaks) collapsed to one space, then the Levenshtein distance is divided by the length of the normalised ground truth and capped at 1.0. Two empty strings give 0, one empty string gives 1.

The page fuzzy and CER are the unweighted means over the rounded field scores, then rounded to three decimals. The benchmark scores are the unweighted means over pages, rounded to three decimals; pages whose response could not be parsed are left out.

Example: ground truth `Vnd ein pferit die mir vnd`, response `und ein pferit die mir vnd`: fuzzy 0.962, CER 1/26 = 0.038.

**Interpretation:** Both scores range from 0 to 1; lower CER is better, higher fuzzy is better. CER ignores case and line breaks, while fuzzy counts them, so a model that reads the letters correctly but merges lines or changes capitalisation loses fuzzy score but not CER. CER is capped at 1 per field, so a field at 1 is not necessarily wrong in every character. A score covers only the pages with a parseable response (see Limitations); report the number of scored pages with it.

**Baseline Results:** Model results are on the [benchmark page](https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/medieval_manuscripts) and in `results/<date>/<test_id>/` at the repository root. Compare runs with the same prompt, scoring rules and ground-truth revision. No fixed model baseline is defined.

**Validation:** The ground truth was produced by the domain expert (see Annotation). Scoring is deterministic; the CER calculation and page averaging are covered by `tests/test_medieval_manuscripts_scoring.py`.

**Human Baseline:** Not specified

**Judge Uses LLM:** false

**Judge Num:** Not specified

**Judge Models:** Not specified

**Judge Score Consolidation:** Not specified

**Validity Justification:** CER is the standard measure for handwritten text recognition and reflects the correction effort needed to turn a model transcription into an edition-ready one.

## Ethical and Legal Considerations

**Privacy and Anonymity:** The manuscript dates from the mid-15th century. Its authors, Hans Rot and Peter Rot, died in 1452 and 1487, and every person it mentions died centuries ago. It contains no data about living persons.

**Data Licensing:** Source material: Public Domain. Ground truth, prompts and other data created for this benchmark: CC BY 4.0.

**Consent Procedures:** Not specified

**Compliance with Regulations:** No data-protection rules apply to a 15th-century manuscript. e-codices marks the images of H V 15 as public domain, usable without restriction. No ethical review was carried out.

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

> Serif, I., & Hindermann, M. (2025). Medieval Manuscripts (benchmark version 1.0.0). In *RISE Humanities Data Benchmark*. Zenodo. https://doi.org/10.5281/zenodo.16941752

Source:

> Universitätsbibliothek Basel, H V 15, mid-15th century. Licence of the source material: Public Domain. https://www.e-codices.unifr.ch/en/list/one/ubb/H-V-0015

The benchmark suite:

> Hindermann, M., Marti, S., Kasper, L. K., & Bosse, A. (2026). The RISE Humanities Data Benchmark: A Framework for Evaluating Large Language Models for Humanities Tasks. *Journal of Open Humanities Data*, *12*(1), 24. https://doi.org/10.5334/johd.481
>
> Hindermann, M., Kasper, L. K., Marti, S., & Bosse, A. (2026). From Experiments to Epistemic Practice: The RISE Humanities Data Benchmark. *Journal of Open Humanities Data*, *12*(1), 38. https://doi.org/10.5334/johd.470

**Contributors by Role:**

- Domain Expert: Ina Serif
- Data Curator: Ina Serif
- Annotator: Ina Serif
- Analyst: Maximilian Hindermann
- Engineer: Maximilian Hindermann, Ina Serif
