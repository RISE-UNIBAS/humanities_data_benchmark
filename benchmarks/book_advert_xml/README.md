# Book Advert XML Repair

This README is a BenchmarkCard (Sokol et al., NeurIPS 2025, arXiv 2410.12974), schema as in evaleval/auto-benchmarkcard v0.2.0.

<!-- Every field stays, in this order; write 'Not specified' when unknown. Fields marked
     (generated) are filled from meta.json and the benchmark's files by
     `python scripts/benchmark_cards.py <name>`; edit meta.json, not the README, to change them. -->

The scorer is in [benchmark.py](benchmark.py), the output schema in [dataclass.py](dataclass.py) and the prompt in [prompts/](prompts/).

To run it, call `python scripts/run_single_test.py --adhoc` from the repository root and select `book_advert_xml`. Provider setup is described in the [root README](../../README.md#quick-start); the configured tests (model, prompt, rules) are in [benchmarks_tests.csv](../benchmarks_tests.csv). Runs against a provider incur API charges.

## Benchmark Details

**Name:** Book Advert XML Repair

**Overview:** Evaluates models on repairing malformed XML markup in transcribed adverts from the Basler Avisblatt (1729–1844), most of them book sale listings tagged for title, author, format and price, while leaving the advert text unchanged.

**Data Type:** text

**Domains:**

- book history
- history of the press
- text encoding

**Languages:**

- German

**Similar Benchmarks:** Not specified

**Resources:**

- https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/book_advert_xml
- https://github.com/RISE-UNIBAS/humanities_data_benchmark/tree/main/benchmarks/book_advert_xml

**Authors:**

- Ina Serif
- Sorin Marti

## Purpose and Intended Users

**Goal:** Measure how well language models repair broken XML markup in historical text without altering the text: closing unclosed elements, correcting mismatched tag names and restoring malformed tags, as needed when cleaning the output of automatic tagging pipelines. The results are meant for AI researchers and model developers comparing models on structured-text repair, and for practitioners in digital humanities and editing who post-process semi-structured historical text and choose a model for markup repair.

**Audience:**

- humanities researchers
- archivists and librarians
- AI researchers
- model developers

**Tasks:**

- repair of malformed XML
- preservation of the transcribed text while editing markup

**Limitations:** 50 adverts from one newspaper and one tagging scheme. The ground truth makes few changes (none in 11 adverts, one in 30), so returning the input unchanged already scores about 99 of 100 (see Baseline Results) and the range that separates models is narrow; models that repair more than the ground truth, or follow the prompt's invitation to add tags "where it makes sense", lose points.

The ground truth has known defects. Six ground-truth files contain mismatched or unclosed tags (three of them recorded as needing no fixes) and 12 contain an unescaped `&`; the scorer compares character strings, not XML structure, so these go undetected in scoring (see Validation). Mismatched `PRIZE`/`PRICE` pairs are resolved to `PRIZE` in some files and to `PRICE` in others, so the expected repair is not predictable from the input. 49 of 50 texts contain the same encoding damage (UTF-8 read as Mac Roman, e.g. `B√ºcher` for "Bücher"), kept in the ground truth, so a model that also fixes the encoding is penalised. At least one file also corrects an OCR error in the text (`Parabieses` to `Paradieses`) that the prompt does not ask for.

**Out-of-Scope Uses:**

- evaluating XML validation against a schema or DTD
- evaluating OCR correction or encoding repair
- evaluating tagging of untagged text from scratch

## Data

**Source:** Adverts from the Basler Avisblatt, the weekly advertising paper of Basel (1729–1844), digitised and processed by the SNSF project "Printed markets: information, data, and news in the Basel 'Avisblatt', 1729–1844" at the University of Basel: https://avisblatt.philhist.unibas.ch/. Most adverts announce books for sale or subscription by booksellers, printers and bookbinders; a few offer other goods. Each is tagged with elements for its bibliographic parts and made malformed.

**Size:** 50 evaluated objects

**Format:** One JSON file per advert under `texts/`, holding the malformed XML as a single string of 66–2,931 characters (median about 1,190):

```json
{
  "xml_string": "<ITEM>11. Bey Herrn Daniel Hag dem Buchbinder sind folgende B√ºcher ... <BIBL><AUTHOR>Ejusd.</AUTHOR> <TITLE>Politicorum Libri</TITLE>. <BIBL><TITLE>Monita</TITLE> ... </ITEM>"
}
```

The ground truth is one JSON file per advert with the repaired string, the number of fixes and an explanation; only `fixed_xml` is scored:

```json
{
  "fixed_xml": "<ITEM>11. Bey Herrn Daniel Hag dem Buchbinder sind folgende B√ºcher ... <BIBL><AUTHOR>Ejusd.</AUTHOR> <TITLE>Politicorum Libri</TITLE>.</BIBL><BIBL><TITLE>Monita</TITLE> ... </ITEM>",
  "number_of_fixes": 3,
  "explanation": "Three closing BIBL tags were missing after the TITLE tags ..."
}
```

Elements used: `ITEM` (one per advert), `BIBL`, `TITLE`, `AUTHOR`, `FORMAT`, `VOLUME`, `YEAR`, `PLACE`, and `PRIZE` or `PRICE` for prices, with single uses of `DAY`, `DATE`, `DESCRIPTION` and `AVAILABILITY`. The ground truth records 0–7 fixes per advert, mostly unclosed `BIBL` or `TITLE` elements and `PRIZE`/`PRICE` tag mismatches.

**Annotation:** The repaired ground truth was drafted by a language model and reviewed by the annotator, Sorin Marti, with Ina Serif as domain expert (see Contributors by Role). The source of the malformations (the project's tagging pipeline or deliberate corruption) is not documented. Defects that survived the review are listed under Limitations.

**Size Breakdown:**

- text files: 50

**Collection Date:** Source documents: the Avisblatt appeared 1729–1844; the years named in the 50 adverts run up to 1748. Added to the benchmark: December 2025.

**Contamination Controls:** None. The texts, prompt and ground truth have been public in this repository since December 2025.

## Methodology

**Methods:**

- zero-shot repair of one advert per request: the prompt [`prompt.txt`](prompts/prompt.txt) with the advert's JSON file attached
- structured JSON output requested with the `CorrectedAdvert` dataclass in all tests but one, which requests no schema; the prompt names the count key `number_of_fixes`, the schema `number_of_corrections`, and neither is scored
- temperature 0 in 113 tests and 1 in 15
- output capped at the repository default of 16,384 tokens per request, adjusted per model in `scripts/benchmark_base.py`

**Metrics:**

- Fuzzy similarity (`fuzzy`, used for ranking)

**Calculation:** From the response's `fixed_xml` and the ground truth's `fixed_xml`, all spaces, line feeds and carriage returns are removed; tabs and other whitespace are kept. The advert score is the rapidfuzz `ratio` of the two strings, from 0 to 100. A response that parses but has no `fixed_xml` scores 0. The benchmark score is the unrounded mean of the advert scores. A response that cannot be parsed into the schema is not scored and does not enter the mean.

**Interpretation:** Scores range from 0 to 100; higher is better. 100 means the strings match after whitespace removal; it does not show that the XML is well-formed. Read scores against the no-edit reference of about 99 (see Baseline Results): a score below it means the model's edits moved the text further from the ground truth than leaving it alone would have. A score covers only the adverts with a parseable response; report the number of scored adverts with it.

**Baseline Results:** Model results are on the [benchmark page](https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/book_advert_xml) and in `results/<date>/<test_id>/` at the repository root. Compare runs with the same prompt, scoring rules and ground-truth revision. No fixed model baseline is defined. Copying each input `xml_string` unchanged into `fixed_xml` scores 99.001739 across the 50 adverts (lowest single advert 84.6).

Observed across models: the task combines syntactic repair, structural reconstruction (adding missing tags) and implicit interpretation (deciding what should be tagged), which blurs what a score measures; separate variants for repair only, repair with enrichment and interpretation-heavy work would allow more controlled comparisons. A single score per advert also hides which kinds of error a model makes; component-level measures such as tag accuracy and hierarchy correctness, and per-sample diagnostics, would make strengths and weaknesses visible.

**Validation:** The model-drafted ground truth was reviewed by Sorin Marti (see Annotation); no second check is recorded. A strict `xml.etree.ElementTree.fromstring` parse rejects 16 of the 50 ground-truth `fixed_xml` strings (the defects listed under Limitations); this does not affect their string-similarity scores. Scoring is deterministic; the scorer is covered by `tests/test_simple_averagers_scoring.py`.

**Human Baseline:** Not specified

**Judge Uses LLM:** false

**Judge Num:** Not specified

**Judge Models:** Not specified

**Judge Score Consolidation:** Not specified

**Validity Justification:** Not specified

## Ethical and Legal Considerations

**Privacy and Anonymity:** The adverts name 18th-century booksellers, printers and authors; all are long dead. No living persons are concerned.

**Data Licensing:** Source material: CC BY-NC-SA 4.0. Ground truth, prompts and other data created for this benchmark: CC BY 4.0.

**Consent Procedures:** Not specified

**Compliance with Regulations:** The advert texts come from the Avisblatt project's published data (Avisdata, https://doi.org/10.5281/zenodo.8278751), used under CC BY-NC-SA 4.0, the licence in that dataset's rights field (its notes say CC BY-SA 4.0). The adverts were printed in the 18th century and the persons named are long dead, so data protection law does not apply. No ethical review was carried out.

## Beyond the BenchmarkCard

This section is not part of the BenchmarkCard schema and is not exported to `benchmark_card.json`.

**Versions:**

- 1.0.0 — initial versioned state

**How to Cite:** This benchmark:

> Serif, I., & Marti, S. (2025). Book Advert XML Repair (benchmark version 1.0.0). In *RISE Humanities Data Benchmark*. Zenodo. https://doi.org/10.5281/zenodo.16941752

Source:

> Basler Avisblatt, digitised by the SNSF project "Printed markets" (University of Basel), 1729–1844. Licence of the source material: CC BY-NC-SA 4.0. https://avisblatt.philhist.unibas.ch/

The benchmark suite:

> Hindermann, M., Marti, S., Kasper, L. K., & Bosse, A. (2026). The RISE Humanities Data Benchmark: A Framework for Evaluating Large Language Models for Humanities Tasks. *Journal of Open Humanities Data*, *12*(1), 24. https://doi.org/10.5334/johd.481
>
> Hindermann, M., Kasper, L. K., Marti, S., & Bosse, A. (2026). From Experiments to Epistemic Practice: The RISE Humanities Data Benchmark. *Journal of Open Humanities Data*, *12*(1), 38. https://doi.org/10.5334/johd.470

**Contributors by Role:**

- Domain Expert: Ina Serif
- Data Curator: Sorin Marti
- Annotator: Sorin Marti
- Analyst: Ina Serif, Sorin Marti
- Engineer: Sorin Marti
