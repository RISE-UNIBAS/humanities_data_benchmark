# Magazine Pages - Anglo Swiss Trade Review

This README is a BenchmarkCard (Sokol et al., NeurIPS 2025, arXiv 2410.12974), schema as in evaleval/auto-benchmarkcard v0.2.0.

<!-- Every field stays, in this order; write 'Not specified' when unknown. Fields marked
     (generated) are filled from meta.json and the benchmark's files by
     `python scripts/benchmark_cards.py <name>`; edit meta.json, not the README, to change them. -->

The scoring implementation is in [benchmark.py](benchmark.py), the requested output schema in [dataclass.py](dataclass.py), and the instructions in [prompts/](prompts/).

To run this benchmark, use `python scripts/run_single_test.py --adhoc` from the repository root and select `magazine_pages`. Provider setup is described in the [root README](../../README.md#quick-start); configured prompts, models and scoring rules are recorded in [benchmarks_tests.csv](../benchmarks_tests.csv). Provider-backed runs incur API charges.

## Benchmark Details

**Name:** Magazine Pages - Anglo Swiss Trade Review

**Overview:** Examines a model's ability to extract bounding boxes of advertisements from magazine pages.

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

- AI researchers
- model developers
- industry practitioners

**Tasks:**

- advertisement detection on printed magazine pages
- bounding-box localisation in pixel coordinates

**Limitations:** 46 pages from one journal series (three successive titles, 1921-1950), all in English and all scanned at the same size; results do not transfer automatically to other periodicals, layouts or scan conditions. Every page contains at least one advertisement, so the benchmark never tests whether a model correctly returns nothing. The prompt does not define what counts as an advertisement or how tightly a box should fit it, so the score measures agreement with the annotators' reading of both. A box counts only at an IoU of 0.5 or more with a ground-truth box, so a roughly placed box scores the same as no box. The ground truth was partly derived from the output of the OpenCV contour detector that also runs as a baseline (see Annotation), which creates a risk of reference bias towards that detector and border-aligned boxes. Its magnitude has not been measured with independently annotated boxes. The benchmark has two prompt variants whose scores are not comparable (see Methods).

**Out-of-Scope Uses:**

- evaluating text recognition or the content of advertisements (no text is scored)
- evaluating general document layout analysis beyond advertisements
- comparing scores obtained with `prompt.txt` against scores obtained with `prompt_explicit-json.txt`

## Data

**Source:** Pages from the official journal of the British Chamber of Commerce for Switzerland, an English-language trade journal for Anglo-Swiss commerce, published under three successive titles: "The Anglo-Swiss Review" (September 1921), "The Commercial Gazette" (1923-1926) and "Anglo-Swiss Trade Review" (1945-1950). The pages mix editorial columns, trade news and bordered or free-standing advertisements of banks, shipping agents and manufacturers. The holding institution of the scans is not specified. The journals are described as sources by the NOISE project at the University of Basel (https://noise.europa.unibas.ch/p/sources/adverts/), and an advertisement corpus cut from them is published on Zenodo by Lea Kasper under CC BY 4.0 (https://doi.org/10.5281/zenodo.20172648).

**Size:** 46 evaluated objects

**Format:** One JPG scan per page, 2479×3508 px (A4 at 300 dpi) and about 0.7-1.9 MB each. The ground truth is one JSON file per page, following the `MagazinePage` dataclass in `dataclass.py`, with one `[x0, y0, x1, y1]` box per advertisement in original-image pixel coordinates, (x0, y0) the top-left and (x1, y1) the bottom-right corner:

```json
{
  "advertisements": [
    {"box": [265, 1730, 2344, 3235]},
    {"box": [300, 187, 2331, 1703]}
  ]
}
```

The 46 pages hold 126 advertisements, between 1 and 7 per page.

**Annotation:** Boxes were drawn and checked by the domain expert and the data curator listed under Authors. Part of the ground truth was created from the output of the OpenCV contour detector in `local/backends/contour.py` and then verified by hand. No written annotation guideline defines what counts as an advertisement.

**Size Breakdown:**

- images files: 46

**Collection Date:** Not specified for benchmark collection or digitisation. Source-document dates: The pages date from 1921-1950.

**Contamination Controls:** No held-out private split, training-data audit or other contamination control is documented. Inputs, prompts and ground truths are distributed together in this public repository. Whether any evaluated model saw these materials during training is unknown.

## Methodology

**Methods:**

- zero-shot bounding-box detection from a single image per request
- the prompt states the page size in pixels, filled in from the image (`{width}`, `{height}`)
- structured JSON output requested using the `MagazinePage` dataclass
- two prompt variants: `prompt.txt` names no output format and is used by all tests created before the variant existed; `prompt_explicit-json.txt` adds the exact JSON shape and the `box` key and is used by new tests. A model without a forced-tool path tends to answer `prompt.txt` in prose, which yields no boxes and scores zero, so the two variants measure different things and their scores are not comparable
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

**Interpretation:** Scores range from 0 to 1; higher is better. Because the benchmark F1 averages per-page F1, every page counts equally regardless of how many advertisements it holds. Precision and recall separate invented boxes from missed ones; mean IoU shows how tightly the matched boxes fit. Compare models only within one prompt variant: a low score under `prompt.txt` can mean the model answered in prose rather than that it failed to find the advertisements.

**Baseline Results:** Model results are available on the [benchmark page](https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/magazine_pages) and in `results/<date>/<test_id>/` at the repository root. Compare runs with the same prompt, scoring rules and ground-truth revision, and report the number of successfully scored objects alongside the score. No fixed model baseline with a run ID and date is specified here.

Observed across models: the rule-based contour detector places its boxes very precisely, but its advantage partly reflects how the ground truth was made (see Limitations).

**Validation:** Ground truths were checked by the annotators. Scoring is deterministic; the scorer has no dedicated unit tests.

**Human Baseline:** Not specified

**Judge Uses LLM:** false

**Judge Num:** Not specified

**Judge Models:** Not specified

**Judge Score Consolidation:** Not specified

**Validity Justification:** The implementation uses an IoU threshold of 0.5 and greedy assignment by overlap. It does not compute confidence-ranked average precision or a PASCAL VOC evaluation score. Whether accepted boxes yield adequate crops for downstream research has not been independently validated.

## Ethical and Legal Considerations

**Privacy and Anonymity:** The pages are published trade journal pages, 1921-1950. They name companies, and some articles and advertisements name individuals, mostly business people acting in a public capacity. No private records are included and nothing is anonymised. Only advertisement positions are annotated; no personal data is extracted or scored.

**Data Licensing:** CC BY 4.0

**Consent Procedures:** Not specified

**Compliance with Regulations:** The page images are used under CC BY 4.0, the licence of the published advertisement corpus from the same journals. The pages are published material from 1921-1950; copyright in individual articles, illustrations and advertisement designs may outlast the publication if their authors are known (in Switzerland 70 years after the author's death, Art. 29 URG). No separate reuse terms are stated for the ground truths. No ethical review was carried out.

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

- Domain Expert: Lea Kasper
- Data Curator: Lea Kasper, Sorin Marti
- Annotator: Lea Kasper, Sorin Marti
- Analyst: Arno Bosse
- Engineer: Sorin Marti
