# Magazine Pages

This README is a BenchmarkCard (Sokol et al., NeurIPS 2025, arXiv 2410.12974), schema as in evaleval/auto-benchmarkcard v0.2.0.

<!-- Every field stays, in this order; write 'Not specified' when unknown. Fields marked
     (generated) are filled from meta.json and the benchmark's files by
     `python scripts/benchmark_cards.py <name>`; edit meta.json, not the README, to change them. -->

The scorer is in [benchmark.py](benchmark.py), the requested output schema in [dataclass.py](dataclass.py) and the prompts in [prompts/](prompts/).

To run this benchmark, use `python scripts/run_single_test.py --adhoc` from the repository root and select `magazine_pages`. Provider setup is described in the [root README](../../README.md#quick-start); configured prompts, models and scoring rules are recorded in [benchmarks_tests.csv](../benchmarks_tests.csv). Provider-backed runs incur API charges.

## Benchmark Details

**Name:** Magazine Pages

**Overview:** Models locate the advertisements on printed pages of the journal of the British Chamber of Commerce for Switzerland, 1921–1950, and return one pixel bounding box per advertisement.

**Data Type:** image

**Domains:**

- history
- economic history
- periodicals

**Languages:**

- English

**Similar Benchmarks:** Not specified

**Resources:**

- https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/magazine_pages
- https://github.com/RISE-UNIBAS/humanities_data_benchmark/tree/main/benchmarks/magazine_pages

**Authors:**

- Lea Kasper
- Sorin Marti
- Arno Bosse

## Purpose and Intended Users

**Goal:** Measure how well vision-language models locate advertisements on printed pages of an English-language Anglo-Swiss trade journal, returning one pixel bounding box per advertisement. Separating advertisements from editorial content is a first step in using periodicals as sources for economic and business history. The results are meant to guide historians, archivists and digital humanities projects in choosing a model, or a non-LLM detector, for segmenting advertisements in historical periodicals.

**Audience:**

- humanities researchers
- archivists and librarians
- AI researchers
- model developers

**Tasks:**

- advertisement detection on printed magazine pages
- bounding-box localisation in pixel coordinates

**Limitations:** The 46 pages come from one journal under three successive titles, 1921–1950, all in English and all scanned at the same size; results do not transfer to other periodicals, layouts or scan conditions. Every page contains at least one advertisement, so the benchmark never tests whether a model correctly returns nothing. The prompts do not define what counts as an advertisement or how tightly a box should fit it, so the score measures agreement with the annotators' reading of both. A box counts only at an IoU of 0.5 or more with a ground-truth box (see Calculation), so a roughly placed box scores the same as no box. Part of the ground truth was derived from the output of the OpenCV contour detector that also runs as a baseline (see Annotation), which biases the reference towards that detector and towards border-aligned boxes; the size of this bias has not been measured. Scores of the two prompt variants are not comparable (see Interpretation).

**Out-of-Scope Uses:**

- evaluating text recognition or the content of advertisements (no text is scored)
- evaluating general document layout analysis beyond advertisements
- comparing scores obtained with `prompt.txt` against scores obtained with `prompt_explicit-json.txt`

## Data

**Source:** Pages from the official journal of the British Chamber of Commerce for Switzerland, an English-language trade journal for Anglo-Swiss commerce, published under three successive titles: "The Anglo-Swiss Review" (September 1921), "The Commercial Gazette" (1923–1926) and "Anglo-Swiss Trade Review" (1945–1950). The pages mix editorial columns, trade news and bordered or free-standing advertisements of banks, shipping agents and manufacturers. The holding institution of the scans is not specified. The journals are described as sources by the NOISE project at the University of Basel (https://noise.europa.unibas.ch/p/sources/adverts/), and an advertisement corpus cut from them is published on Zenodo by Lea Kasper under CC BY 4.0 (https://doi.org/10.5281/zenodo.20172648).

**Size:** 46 evaluated objects

**Format:** One JPG scan per page, 2479×3508 px (A4 at 300 dpi) and 0.7–1.9 MB each. The ground truth is one JSON file per page, following the `MagazinePage` dataclass in `dataclass.py`, with one `[x0, y0, x1, y1]` box per advertisement in original-image pixel coordinates, (x0, y0) the top-left and (x1, y1) the bottom-right corner:

```json
{
  "advertisements": [
    {"box": [265, 1730, 2344, 3235]},
    {"box": [300, 187, 2331, 1703]}
  ]
}
```

The 46 pages hold 126 advertisements, between 1 and 7 per page.

**Annotation:** The annotators Lea Kasper and Sorin Marti drew and checked the boxes, with Lea Kasper as domain expert. Part of the ground truth was created from the output of the OpenCV contour detector in `local/backends/contour.py` and then verified by hand. No written annotation guideline defines what counts as an advertisement.

**Size Breakdown:**

- image files: 46

**Collection Date:** Source documents: 1921–1950. Added to the benchmark: March 2026.

**Contamination Controls:** None. The scans, prompts and ground truth have been public in this repository since March 2026.

## Methodology

**Methods:**

- zero-shot bounding-box detection from a single image per request, temperature 0.0 (1.0 for OpenAI models)
- the prompt states the page size in pixels, filled in from the image (`{width}`, `{height}`)
- structured JSON output requested using the `MagazinePage` dataclass
- output cap: the repository default of 16,384 tokens per request
- two prompt variants: [prompt.txt](prompts/prompt.txt) names no output format and is used by the tests created before the variant existed; [prompt_explicit-json.txt](prompts/prompt_explicit-json.txt) adds the exact JSON shape and the `box` key and is used by newer tests
- a rule-based baseline: the OpenCV contour detector (`provider=contour_local`), which finds rectangular printed borders without any model

**Metrics:**

- F1 (`f1`, used for ranking)
- precision (`precision`)
- recall (`recall`)
- mean IoU of matched boxes (`mean_iou`)

**Calculation:** For each page, boxes are read from `advertisements[].box` (or `detections[].box` for local backends); entries without a `box` key are ignored. The Intersection-over-Union (IoU) is computed for every pair of predicted and ground-truth box. Pairs with IoU of 0.5 or more are sorted by IoU, highest first, and assigned greedily so that each box is matched at most once.

- TP: a predicted box matched to a ground-truth box
- FP: a predicted box that matched nothing
- FN: a ground-truth box that no prediction matched

Per page, precision = TP / (TP + FP), recall = TP / (TP + FN) and F1 is their harmonic mean (0 when undefined); mean IoU averages the IoU of the matched pairs (0 when there are none). Each is rounded to three decimals. If both the page and the response have no boxes, every metric is 1.0; no page in the dataset is of that kind. A response that cannot be parsed as JSON is scored as an answer with no boxes, i.e. F1 0 on the page, rather than skipped.

The benchmark scores are the unweighted means of the per-page values, rounded to three decimals; TP, FP and FN are also summed over all pages.

**Interpretation:** Scores range from 0 to 1; higher is better. Because the benchmark F1 averages per-page F1, every page counts equally regardless of how many advertisements it holds. Precision and recall separate invented boxes from missed ones; mean IoU shows how tightly the matched boxes fit. Compare models only within one prompt variant: a model without a forced-tool path tends to answer `prompt.txt` in prose, which yields no boxes and scores zero, so a low score under `prompt.txt` can reflect the answer format rather than a failure to find the advertisements.

**Baseline Results:** Results are on the [benchmark page](https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/magazine_pages) and in `results/<date>/<test_id>/` at the repository root. No fixed baseline is recorded beyond the contour detector (see Methods). Compare runs only with the same prompt, rules and ground-truth revision.

Observed across models: the prompt decides much of the result. Under `prompt.txt`, 23 of the 88 active test configurations score F1 0, because the model answers without boxes, and the median is 0.21; under `prompt_explicit-json.txt` none of the 7 scores 0 and the median is 0.86. The best models reach F1 0.97 under either prompt, with matched boxes fitting at a mean IoU of 0.90–0.97. The rule-based contour detector scores F1 0.80: its matched boxes fit closely (mean IoU 0.91), but it also frames bordered editorial content (precision 0.77). Its fit partly reflects how the ground truth was made (see Limitations).

**Validation:** The ground truth was checked by the annotators named under Annotation. Scoring is deterministic; the scorer is covered by `tests/test_magazine_pages_scoring.py`.

**Human Baseline:** Not specified

**Judge Uses LLM:** false

**Judge Num:** Not specified

**Judge Models:** Not specified

**Judge Score Consolidation:** Not specified

**Validity Justification:** An IoU of 0.5 is the PASCAL VOC threshold for a correct detection, and one-to-one matching rewards finding each advertisement exactly once. The score is not confidence-ranked average precision, because responses carry no confidence values. Whether accepted boxes yield adequate crops for downstream research has not been validated.

## Ethical and Legal Considerations

**Privacy and Anonymity:** The pages are published trade journal pages, 1921–1950. They name companies, and some articles and advertisements name individuals, mostly business people acting in a public capacity. No private records are included and nothing is anonymised. Only advertisement positions are annotated; no personal data is extracted or scored.

**Data Licensing:** Source material: CC BY 4.0. Ground truth, prompts and other data created for this benchmark: CC BY 4.0.

**Consent Procedures:** Not specified

**Compliance with Regulations:** The page images are used under CC BY 4.0, the licence of the published advertisement corpus from the same journals. The pages are published material from 1921–1950; copyright in individual articles, illustrations and advertisement designs may outlast the publication if their authors are known (in Switzerland 70 years after the author's death, Art. 29 URG). No ethical review was carried out.

## Beyond the BenchmarkCard

This section is not part of the BenchmarkCard schema and is not exported to `benchmark_card.json`.

<!-- Versions use semantic versioning, newest first, one line each:
     `- MAJOR.MINOR.PATCH (YYYY-MM-DD) — what changed and why`.
     MAJOR: scores before and after are not comparable (ground truth corrected, scoring or
            ranking metric changed, objects added or removed).
     MINOR: something added that leaves existing scores unchanged (e.g. a new prompt variant).
     PATCH: a fix that changes no score (e.g. a better scan of the same image). -->

**Versions:**

- 1.0.0 (2026-10-16) — initial versioned state, when the card was introduced; same content as 0.4.0
- 0.4.0 (2026-09-18) — an answer that cannot be parsed is scored as a miss again; prompt variant stating the JSON format
- 0.3.1 (2026-09-11) — per-field comparison recorded with each answer; scores unchanged
- 0.3.0 (2026-09-09) — answers capped at 32,768 output tokens
- 0.2.0 (2026-08-16) — an answer that cannot be parsed is left out of the average instead of scored as a miss
- 0.1.1 (2026-04-22) — a failed object is left out of the average instead of stopping the run
- 0.1.0 (2026-03-21) — first state

**How to Cite:** This benchmark:

> Kasper, L., Marti, S., & Bosse, A. (2026). Magazine Pages (benchmark version 1.0.0). In *RISE Humanities Data Benchmark*. Zenodo. https://doi.org/10.5281/zenodo.16941752

Source:

> Journal of the British Chamber of Commerce for Switzerland, 1921–1950. Licence of the source material: CC BY 4.0. https://noise.europa.unibas.ch/p/sources/adverts/

The benchmark suite:

> Hindermann, M., Marti, S., Kasper, L. K., & Bosse, A. (2026). The RISE Humanities Data Benchmark: A Framework for Evaluating Large Language Models for Humanities Tasks. *Journal of Open Humanities Data*, *12*(1), 24. https://doi.org/10.5334/johd.481
>
> Hindermann, M., Kasper, L. K., Marti, S., & Bosse, A. (2026). From Experiments to Epistemic Practice: The RISE Humanities Data Benchmark. *Journal of Open Humanities Data*, *12*(1), 38. https://doi.org/10.5334/johd.470

**Contributors by Role:**

- Domain Expert: Lea Kasper
- Data Curator: Lea Kasper, Sorin Marti
- Annotator: Lea Kasper, Sorin Marti
- Analyst: Arno Bosse
- Engineer: Sorin Marti
