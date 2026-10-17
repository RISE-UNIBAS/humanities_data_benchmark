# Fraktur Adverts

This README is a BenchmarkCard (Sokol et al., NeurIPS 2025, arXiv 2410.12974), schema as in evaleval/auto-benchmarkcard v0.2.0.

<!-- Every field stays, in this order; write 'Not specified' when unknown. Fields marked
     (generated) are filled from meta.json and the benchmark's files by
     `python scripts/benchmark_cards.py <name>`; edit meta.json, not the README, to change them. -->

The scorer is in [benchmark.py](benchmark.py), the output schema in [dataclass.py](dataclass.py) and the prompts in [prompts/](prompts/).

To run it, call `python scripts/run_single_test.py --adhoc` from the repository root and select `fraktur_adverts`. Provider setup is described in the [root README](../../README.md#quick-start); the configured tests (model, prompt, rules) are in [benchmarks_tests.csv](../benchmarks_tests.csv). Runs against a provider incur API charges.

## Benchmark Details

**Name:** Fraktur Adverts

**Overview:** Tests models on transcribing 18th-century adverts printed in German Fraktur from the Basler Avisblatt, splitting each page into its numbered adverts under their section headings.

**Data Type:** image

**Domains:**

- history
- newspaper studies
- economic history

**Languages:**

- German

**Similar Benchmarks:** Not specified

**Resources:**

- https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/fraktur_adverts
- https://github.com/RISE-UNIBAS/humanities_data_benchmark/tree/main/benchmarks/fraktur_adverts

**Authors:**

- Ina Serif
- Maximilian Hindermann

## Purpose and Intended Users

**Goal:** Measure how well vision-language models read 18th-century German Fraktur print and split a newspaper page of classified advertisements into its individual, numbered adverts, each assigned to its section heading and transcribed with its historical spelling intact. The results are meant for AI researchers and model developers comparing models on early modern print, and for practitioners in historical and newspaper research and digital humanities choosing a model to transcribe advertisement papers.

**Audience:**

- AI researchers
- model developers
- industry practitioners

**Tasks:**

- transcription of Fraktur print from page images
- segmentation of a page into numbered advertisements
- assignment of each advertisement to its section heading

**Limitations:** Five pages from two issues of a single newspaper, the Basler Avisblatt (2 January 1731 and 11 February 1762), so scores rest on 91 scored adverts and do not transfer automatically to other papers, typefaces or periods. The two 1731 pages are high-resolution scans and the three 1762 pages much smaller (see Format), so the score mixes two image qualities. The transcription follows the conventions of `prompt_optimized.txt`: long s (ſ) as `s` and the virgule (`/`) as a comma, so a model that keeps ſ or `/` is penalised for following the original more closely.

Several scoring properties bias results (see Calculation). An entry without a number prefix is never scored: nine of the twelve entries on `image_2` (news items and burial notices) and three entries on `image_5` drop out, so 91 of 103 ground-truth entries count. Adverts the model invents or splits off wrongly carry no penalty; only missing or mistranscribed adverts lower the score. If a model writes a section heading that falls below the 0.95 fuzzy threshold, every advert in that section counts as missing even if its text is perfect. The publication date the prompt asks for is not scored.

**Out-of-Scope Uses:**

- evaluating OCR of Fraktur running text (books, articles) without numbered entries
- evaluating the detection of advert boundaries or of unnumbered items
- drawing conclusions about the persons or goods named in the adverts

## Data

**Source:** Pages of the Basler Avisblatt, an advertisement newspaper published in Basel from 1729 to 1844 (Universitätsbibliothek Basel, UBH Ztg 1), as digitised for the project at https://avisblatt.dg-basel.hasdai.org (hosting institution Universitätsbibliothek Basel). The pages come from two issues: [Avis-Blättlein (1731), issue 1](https://avisblatt.dg-basel.hasdai.org/records/zr4m9-68q93) and [Wochentliche Nachrichten aus dem Bericht-Haus zu Basel (1762), issue 6](https://avisblatt.dg-basel.hasdai.org/records/st1gf-t4m41). The paper appeared about weekly, with 1 to 16 pages per issue, and carries mainly numbered classified adverts grouped under standing section headings (things for sale, wanted, to let, lost and found, servants seeking positions), alongside occasional news, price lists and announcements.

**Size:** 5 evaluated objects

**Format:** One JPG per page, printed in two columns in Fraktur type. `image_1` and `image_2` (issue of 1731-01-02) are about 5000×8250 px and 11–13 MB; `image_3` to `image_5` (issue of 1762-02-11) are about 920×1160 px and 0.5 MB. `image_4` is a continuation page with no section heading on it.

The ground truth is one JSON file per page: a list of adverts, or (for the 1731 pages) a dict whose keys are advert ids and whose values are one-element lists of adverts. Each advert follows the `Advertisement` dataclass in `dataclass.py`:

```json
{
  "date": "1731-01-02",
  "tags_section": "Es werden zum Verkauff offerirt",
  "text": "1. Ein Stücklein von in circa 20. Saum extra schön und guter rother Marggräffer-Wein von Anno 1728. in raisonnablem Preiß."
}
```

- `date`: publication date of the issue, ISO 8601
- `tags_section`: the section heading the advert is printed under
- `text`: the advert text as printed, including its number prefix

The model returns the same objects in a `Document` with a list `advertisements`.

**Annotation:** Transcribed by Ina Serif (domain expert) and structured by section and advert number, keeping historical spelling, typographical errors and punctuation, and listing adverts column by column from left to right. Long s is written `s`. The ground truth originally also held an `ntokens` word count per advert; it was removed.

**Size Breakdown:**

- image files: 5

**Collection Date:** Source documents: 2 January 1731 (two pages) and 11 February 1762 (three pages). Added to the benchmark: March 2025 (the 1731 pages) and May 2025 (the 1762 pages).

**Contamination Controls:** None. The images, prompts and ground truth have been public in this repository since March 2025 (the 1731 pages) and May 2025 (the 1762 pages).

## Methodology

**Methods:**

- one page image per request; the prompts include illustrative output examples, and no benchmark page is supplied as a demonstration
- [`prompt_optimized.txt`](prompts/prompt_optimized.txt) for all current tests; the original [`prompt.txt`](prompts/prompt.txt), which has no transcription rules for ſ and `/` and asks for an unscored `ntokens` count, is used by one legacy test only
- all tests use temperature 0
- structured JSON output requested with the `Document` dataclass
- output capped at the repository default of 16,384 tokens per request, adjusted per model in `scripts/benchmark_base.py`

**Metrics:**

- Character error rate (`cer`, used for ranking; lower is better)
- Fuzzy similarity (`fuzzy`; higher is better)

**Calculation:** Adverts in the ground truth and in the response are grouped by `tags_section` and by the number at the start of `text` (`^\s*(\d+)\.`); entries with no section or no number prefix are left out, and of several entries with the same section and number only the last is kept. Each ground-truth section is looked up in the response by exact name, and failing that by the first response section with a fuzzy similarity of 0.95 or above. Within the section, the advert with the same number is the match. On `image_4`, which has no heading, adverts without a section are assigned the default section `Es wird zum Verkauf angetragen`, and a ground-truth advert may match a response advert with the same number in any section.

For each ground-truth advert:

- matched: the fuzzy score is the rapidfuzz `ratio` of the two texts divided by 100, rounded to three decimals, case-sensitive and unnormalised; the CER is the Levenshtein distance divided by the length of the ground-truth text, both lower-cased and with whitespace collapsed, capped at 1.0
- not matched: fuzzy 0.0, CER 1.0

Adverts in the response that match no ground-truth advert are ignored.

A page's fuzzy score is the mean over its ground-truth adverts, rounded to two decimals; its CER is the mean rounded to three decimals. The benchmark scores are the means of the page scores, rounded to three decimals, so each page weighs the same however many adverts it holds. A response that is not parseable JSON is left out of the means rather than scored as zero.

**Interpretation:** CER runs from 0 (identical after normalisation) to the cap of 1, lower is better; an edit distance at least as large as the ground-truth length reaches the cap even if some text is correct. Fuzzy runs from 0 to 1, higher is better. Because CER ignores case and whitespace and fuzzy does not, a model that normalises capitalisation or line breaks does noticeably better on CER than its fuzzy score suggests. Both are page averages: `image_2`, with only three scored adverts, counts as much as `image_1` with 31. A score covers only the pages with a parseable response; report the number of scored pages with it.

**Baseline Results:** Model results are on the [benchmark page](https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/fraktur_adverts) and in `results/<date>/<test_id>/` at the repository root. Compare runs with the same prompt, scoring rules and ground-truth revision. No fixed model baseline is defined.

**Validation:** The ground truth was created by Ina Serif as domain expert and annotator; no second check by another person is recorded. Scoring is deterministic; the CER calculation, number-prefix extraction and advert matching are covered by `tests/test_fraktur_adverts_scoring.py`.

**Human Baseline:** Not specified

**Judge Uses LLM:** false

**Judge Num:** Not specified

**Judge Models:** Not specified

**Judge Score Consolidation:** Not specified

**Validity Justification:** Matching by section and advert number mirrors how adverts in the Avisblatt are cited and catalogued, and character-level error is the standard measure of transcription quality.

## Ethical and Legal Considerations

**Privacy and Anonymity:** The adverts name private persons (sellers, buyers, servants seeking positions, the recently deceased) of Basel in 1731 and 1762. They are not anonymised. Everyone named has been dead for more than two centuries, so no living person is concerned.

**Data Licensing:** CC BY 4.0

**Consent Procedures:** Not specified

**Compliance with Regulations:** The pages are printed matter published in 1731 and 1762, long out of copyright; the persons named are long dead, so data protection law does not apply. The Avisblatt repository licenses the digitised issues under CC BY 4.0, so reuse requires attribution to the source records. No separate reuse terms are stated for the ground truth. No ethical review was carried out.

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

> Serif, I., & Hindermann, M. (2025). Fraktur Adverts (benchmark version 1.0.0). In *RISE Humanities Data Benchmark*. Zenodo. https://doi.org/10.5281/zenodo.16941752

Source:

> Universitätsbibliothek Basel, UBH Ztg 1, 1731–1762. Licence: CC BY 4.0. https://avisblatt.dg-basel.hasdai.org

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
