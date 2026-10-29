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

**Limitations:** 50 adverts from one newspaper and one tagging scheme. The reference makes one repair where a malformation allows several; the scorer accepts two alternatives (see Calculation): which tag of a mismatched `PRIZE`/`PRICE` pair is renamed, and where in the plain text after an element a closing tag is placed. Every other choice, such as where an unclosed `TITLE` ends or which tags to add, is scored against the reference only, and the prompt's invitation to add tags "where it makes sense" costs precision whenever the reference adds none.

The data keeps two features of the source as real-world noise. 49 of 50 texts carry the same encoding damage (UTF-8 read as Mac Roman, e.g. `B√ºcher` for "Bücher"); the scorer repairs it on both sides, so a model that also repairs it neither gains nor loses. Prices are tagged `PRIZE` in most adverts and `PRICE` in some; consistent pairs stay as they are.

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

The ground truth is one JSON file per advert with the repaired string:

```json
{
  "fixed_xml": "<ITEM>11. Bey Herrn Daniel Hag dem Buchbinder sind folgende B√ºcher ... <BIBL><AUTHOR>Ejusd.</AUTHOR> <TITLE>Politicorum Libri</TITLE>. </BIBL><BIBL><TITLE>Monita</TITLE> ... </ITEM>"
}
```

Elements used: `ITEM` (one per advert), `BIBL`, `TITLE`, `AUTHOR`, `FORMAT`, `VOLUME`, `YEAR`, `PLACE`, and `PRIZE` or `PRICE` for prices, with single uses of `DAY`, `DATE`, `DESCRIPTION` and `AVAILABILITY`. The reference differs from the input by 1–14 token edits per advert (one in 18 adverts), mostly unclosed `BIBL` or `TITLE` elements, mismatched `PRIZE`/`PRICE` pairs and unescaped `&`.

**Annotation:** The repaired ground truth was drafted by a language model and reviewed by the annotator, Sorin Marti, with Ina Serif as domain expert (see Contributors by Role). For version 2.0.0 it was curated to the input text plus markup repairs: text the draft had deleted or changed was restored (a French title block in `line_14`, `à` before prices, commas, OCR corrections such as `Parabieses` to `Paradieses`); renames of already consistent `PRIZE` pairs to `PRICE` were undone; unescaped `&` became `&amp;`; six unclosed `BIBL` elements were closed after their last child and five stray `</TITLE>` in `line_49` removed. The draft's `number_of_fixes` and `explanation` were dropped. The source of the malformations (the project's tagging pipeline or deliberate corruption) is not documented.

**Size Breakdown:**

- text files: 50

**Collection Date:** Source documents: the Avisblatt appeared 1729–1844; the years named in the 50 adverts run up to 1748. Added to the benchmark: December 2025.

**Contamination Controls:** None. The texts, prompt and ground truth have been public in this repository since December 2025.

## Methodology

**Methods:**

- zero-shot repair of one advert per request: the prompt [`prompt.txt`](prompts/prompt.txt) with the advert's JSON file attached; new tests use [`prompt_v2.txt`](prompts/prompt_v2.txt), which names the schema's keys
- structured JSON output requested with the `CorrectedAdvert` dataclass in all tests but one, which requests no schema; `prompt.txt` names the count key `number_of_fixes`, the schema `number_of_corrections`, and neither is scored
- temperature 0 in 113 tests and 1 in 15
- output capped at the repository default of 16,384 tokens per request, adjusted per model in `scripts/benchmark_base.py`

**Metrics:**

- Edit F1, mean over adverts (`f1_macro`, used for ranking)
- Edit F1 over pooled edits (`f1_micro`), with `micro_precision` and `micro_recall`

**Calculation:** The input `xml_string`, the reference `fixed_xml` and the response's `fixed_xml` are normalised alike: all whitespace removed, UTF-8 read as Mac Roman repaired, and every closing tag that follows plain text which itself follows a closing tag moved up to that closing tag. The strings are split into tokens (whole tags, character references such as `&amp;`, single characters) and diffed against the input with Python's `difflib`. Each deleted, inserted or substituted token at an input position is one edit; renaming either tag of a mismatched `PRIZE`/`PRICE` pair to match the other is one edit, whichever tag is renamed. The advert score is the F1 of the edits shared by response and reference (precision over the response's edits, recall over the reference's). A response without a string `fixed_xml`, or that cannot be parsed, makes no edits and scores 0. `f1_macro` is the mean advert score; `f1_micro` pools the edit counts.

**Interpretation:** Scores range from 0 to 1; higher is better. 1 means the response makes exactly the reference's repairs and nothing else; returning the input unchanged scores 0. Low precision means edits the reference does not make: changed or dropped text, added or renamed tags. Low recall means missed repairs. A changed character counts as much as a changed tag, so `f1_micro` is dominated by the few responses that rewrite or drop whole adverts; rank by `f1_macro`. A score does not show that the response is well-formed XML.

**Baseline Results:** Model results are on the [benchmark page](https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/book_advert_xml) and in `results/<date>/<test_id>/` at the repository root. Compare runs with the same prompt, scoring rules and ground-truth revision. No fixed model baseline is defined. Copying each input `xml_string` unchanged into `fixed_xml` scores 0. Across the latest run of each of the 100 non-legacy tests, `f1_macro` has a median of 0.27 and a best of 0.61 (claude-fable-5-1).

Observed across models: most answers make the reference's repairs only in part and add edits of their own, such as further tags or corrected spellings; the median test makes exactly the reference's repairs in about 4% of adverts that need them. The task combines syntactic repair, structural reconstruction (adding missing tags) and implicit interpretation (deciding what should be tagged); separate variants for repair only and for enrichment would allow more controlled comparisons.

**Validation:** The model-drafted ground truth was reviewed by Sorin Marti and curated for version 2.0.0 (see Annotation): every reference keeps its input's text apart from repaired malformed tags, and all 50 parse with `xml.etree.ElementTree.fromstring`. Scoring is deterministic; the scorer is covered by `tests/test_book_advert_xml_scoring.py`, including a check that every reference scores 1 against itself.

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

- 2.0.0 (2026-10-18) — scored by edits (F1 of the response's edits against the reference's, `f1_macro`) instead of fuzzy similarity, which an unchanged input won at 99; ground truth curated to the input text plus markup repairs and made well-formed; a response that cannot be parsed is scored as a miss; `prompt_v2.txt` for new tests; all stored runs re-scored
- 1.0.0 (2026-10-16) — initial versioned state, when the card was introduced; same content as 0.4.0
- 0.4.0 (2026-09-18) — answers capped at 16,384 output tokens instead of 32,768
- 0.3.1 (2026-09-11) — per-field comparison recorded with each answer; scores unchanged
- 0.3.0 (2026-09-09) — answers capped at 32,768 output tokens
- 0.2.0 (2026-08-16) — an answer that cannot be parsed is left out of the average instead of scored as a miss
- 0.1.1 (2026-04-22) — a failed object is left out of the average instead of stopping the run
- 0.1.0 (2025-12-07) — first state

**How to Cite:** This benchmark:

> Serif, I., & Marti, S. (2025). Book Advert XML Repair (benchmark version 2.0.0). In *RISE Humanities Data Benchmark*. Zenodo. https://doi.org/10.5281/zenodo.16941752

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
