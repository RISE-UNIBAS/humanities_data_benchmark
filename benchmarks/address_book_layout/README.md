# Address Book Layout

This README is a BenchmarkCard (Sokol et al., NeurIPS 2025, arXiv 2410.12974), schema as in evaleval/auto-benchmarkcard v0.2.0.

<!-- Every field stays, in this order; write 'Not specified' when unknown. Fields marked
     (generated) are filled from meta.json and the benchmark's files by
     `python scripts/benchmark_cards.py <name>`; edit meta.json, not the README, to change them. -->

The scorer is in [benchmark.py](benchmark.py), the requested output schema in [dataclass.py](dataclass.py) and the prompt in [prompts/](prompts/).

To run this benchmark, use `python scripts/run_single_test.py --adhoc` from the repository root and select `address_book_layout`. Provider setup is described in the [root README](../../README.md#quick-start); configured prompts, models and scoring rules are recorded in [benchmarks_tests.csv](../benchmarks_tests.csv). Provider-backed runs incur API charges.

## Benchmark Details

**Name:** Address Book Layout

**Overview:** Models locate every entry in the complete business directory of the Basel address book of 1890 (Staatsarchiv Basel-Stadt), all 64 pages, and return one pixel bounding box per entry; entries are short, set in two columns and may run over several lines.

**Data Type:** image

**Domains:**

- history
- urban history
- trade directories

**Languages:**

- German

**Similar Benchmarks:**

- magazine_pages
- company_lists

**Resources:**

- https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/address_book_layout
- https://github.com/RISE-UNIBAS/humanities_data_benchmark/tree/main/benchmarks/address_book_layout

**Authors:**

- Eric Decker
- Lea Kasper

## Purpose and Intended Users

**Goal:** Measure how well vision-language models segment a dense printed directory page into its entries, returning one pixel bounding box per entry. Locating each entry is the step that ties a record extracted from an address book back to its place on the page, so that a reader can check the record against the print and an extraction pipeline can cut one image snippet per entry. The results are meant to guide historians and digital humanities projects working with directories, address books and similar lists in choosing a model, or an OCR-based method, for this step.

**Audience:**

- humanities researchers
- archivists and librarians
- AI researchers
- model developers

**Tasks:**

- entry detection on printed directory pages
- bounding-box localisation in pixel coordinates

**Limitations:** The 64 pages come from one volume, the business directory of the Basel address book of 1890, all printed in the same two-column layout and scanned under the same conditions; results do not transfer to other directories, layouts or scans. Entries are narrow (a one-line entry is about 1.5 % of the page height, 30 px in the downscaled image), so a box that drifts by one line already falls below the IoU threshold of 0.5 and scores the same as no box. The prompt describes what counts as an entry but not where exactly its box ends (indentation, leaders, marginal marks), so the score also measures agreement with the annotator's reading of that. The ground truth started from automatic boxes (Tesseract line boxes matched to the extracted entries) that the annotator confirmed or redrew (see Annotation); this may bias the reference towards OCR-style line boxes. Every page holds entries, so the benchmark never tests whether a model correctly returns nothing. The images are downscaled to a height of 2000 px, which makes the small type harder to read than in the original scans. Several models, among them Gemini models and Qwen3-VL, report positions on a 0–1000 scale, the convention many vision models are trained on, instead of the pixels the prompt asks for. They score close to 0 although their boxes, read as 0–1000 values, lie on the entries. The scorer takes the coordinates as given, so the benchmark measures finding the entries and reporting them in the requested pixel coordinates together.

**Out-of-Scope Uses:**

- evaluating transcription or the content of the entries (no text is scored)
- evaluating general layout analysis beyond directory entries (headings, notes, legends, footnotes, running heads and page numbers are not annotated)

## Data

**Source:** Pages from the "Verzeichnis der Einwohner nach ihren Geschäften und Gewerben", the business directory of the Basel address book of 1890 ("Adressbuch der Stadt Basel"), held by the Staatsarchiv Basel-Stadt under the signature STA H 43 36 and digitised by it. The directory lists persons, companies and institutions under trade headings, usually with an address and sometimes with marks such as a telephone sign. The benchmark uses the whole directory, images 362 to 425 of the volume: its first page, which carries the printed page number 23, and printed pages 354 to 416. The pages were annotated in the project "Basel address books" at the University of Basel (RISE), which extracts the entries of a series of Basel address books with a language model and links each record to its place on the page.

**Size:** 64 evaluated objects

**Format:** One greyscale JPG per page, downscaled from the archive's scan to 1376×2000 px (about 0.7 MB each). The file name is the image identifier of the archive's IIIF image service (`sta_h_43_36_0363` is image 363 of the volume). The ground truth is one JSON file per page, following the `AddressBookPage` dataclass in `dataclass.py`, with one `[x0, y0, x1, y1]` box per entry in pixel coordinates of the downscaled image, (x0, y0) the top-left and (x1, y1) the bottom-right corner, in reading order (column by column, top to bottom):

The first two entries of `sta_h_43_36_0363`:

```json
{
  "entries": [
    {"box": [226, 254, 745, 344]},
    {"box": [224, 341, 745, 401]}
  ]
}
```

The 64 pages hold 5,494 entries, between 38 and 105 per page (median 88). An entry that runs over several printed lines has one box covering all of them. A cross-reference standing in place of entries, such as "(Siehe Konditoren.)" under a trade heading, is boxed as an entry (about 46 of them); trade headings and sub-headings, notes under a heading, legends of marks, footnotes, running heads and page numbers are not boxed.

**Annotation:** Eric Decker checked every box page by page in a box editor built for the project. The editor showed the box found automatically for each extracted entry (Tesseract line boxes matched to the entry's text); he confirmed 4,157 boxes and drew or redrew 1,337, among them 52 entries for which no automatic box had been found. Headings, notes, footnotes, running heads and page numbers were not boxed. One extracted record was discarded and has no box. On the final ground truth, 97.6 % of the checked boxes are matched by their automatic box at IoU 0.5 or more (98.5 % of the 5,442 automatic boxes; mean IoU of all automatic boxes 0.945). No second annotator checked the boxes, and no written guideline beyond the rule that a box covers all lines of one entry was used.

**Size Breakdown:**

- image files: 64

**Collection Date:** Source documents: 1890. Added to the benchmark: November 2026.

**Contamination Controls:** None. The images are derived from scans the Staatsarchiv Basel-Stadt shows online; the ground truth was not published before this benchmark.

## Methodology

**Methods:**

- zero-shot bounding-box detection from a single image per request
- the prompt defines an entry (including cross-references such as "(Siehe Konditoren.)") and names what is not one, states the page size in pixels, filled in from the image (`{width}`, `{height}`), and the exact JSON shape of the answer
- structured JSON output requested using the `AddressBookPage` dataclass
- output cap: the repository default per request

**Metrics:**

- F1 at IoU 0.5 (`f1`, used for ranking)
- precision (`precision`) and recall (`recall`) at IoU 0.5
- F1 at IoU 0.75 (`f1_strict`)
- mean IoU of matched boxes (`mean_iou`)
- relative error of the number of boxes (`count_error`)

**Calculation:** For each page, boxes are read from `entries[].box` (from `detections[].box` for the local detectors); corners are put in order, and an item that is not four finite JSON numbers (a quoted number, NaN or infinity included) is kept as a box that matches nothing. The Intersection-over-Union (IoU) is computed for every pair of predicted and ground-truth box. Pairs with IoU of 0.5 or more are sorted by IoU, highest first, and assigned greedily so that each box is matched at most once.

- TP: a predicted box matched to a ground-truth box
- FP: a predicted box that matched nothing, including malformed items
- FN: a ground-truth box that no prediction matched

Per page, precision = TP / (TP + FP), recall = TP / (TP + FN) and F1 is their harmonic mean (0 when undefined). The same matching at IoU 0.75 gives `f1_strict`. Mean IoU averages the IoU of the pairs matched at 0.5 (0 when there are none); `count_error` is |predicted − expected| / expected. Each is rounded to three decimals. A response that cannot be parsed is scored as an answer with no boxes, i.e. F1 0 on the page, rather than skipped.

The benchmark scores are the unweighted means of the per-page values, rounded to three decimals. TP, FP and FN are also summed over all pages, and micro precision, recall and F1 (`precision_micro`, `recall_micro`, `f1_micro`) are computed from these sums.

**Interpretation:** Scores range from 0 to 1 (`count_error` from 0 upwards); higher is better, except for `count_error`. The benchmark F1 averages per-page F1, so every page counts equally; the micro values weight pages by their number of entries. Precision and recall separate invented boxes from missed ones. A gap between `f1` and `f1_strict` shows that boxes are found but fit loosely; `count_error` shows whether a model splits or merges entries even where its boxes do not overlap enough to match.

**Baseline Results:** Results are on the [benchmark page](https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/address_book_layout) and in `results/<date>/<test_id>/` at the repository root. No fixed baseline is recorded. As a reference outside the benchmark runs, the automatic OCR-based localisation that produced the pre-boxes matches 97.6 % of the ground-truth boxes at IoU 0.5 (see Annotation); it had the extracted entry texts as input and is therefore not a comparable baseline. Compare runs only with the same prompt, rules and ground-truth revision.

**Validation:** The ground truth was checked box by box by the annotator named under Annotation; every one of the 64 pages has no unchecked box. Boxes of one page (printed page 370) were drawn onto the downscaled image and inspected after the export. Scoring is deterministic; the scorer is covered by `tests/test_address_book_layout_scoring.py`, including a test in which every ground truth scores perfectly against itself.

**Human Baseline:** Not specified

**Judge Uses LLM:** false

**Judge Num:** Not specified

**Judge Models:** Not specified

**Judge Score Consolidation:** Not specified

**Validity Justification:** An IoU of 0.5 is the PASCAL VOC threshold for a correct detection, and one-to-one matching rewards finding each entry exactly once. Because entries are only one to three lines high, the stricter F1 at IoU 0.75 is reported alongside to show whether boxes fit closely enough to cut usable snippets. The score is not confidence-ranked average precision, because responses carry no confidence values.

## Ethical and Legal Considerations

**Privacy and Anonymity:** The pages are a printed public directory from 1890. They name persons and businesses with their trades and addresses, as published at the time; all persons named are long dead. Nothing is anonymised. Only the positions of the entries are annotated; no personal data is extracted or scored.

**Data Licensing:** Source material: Public Domain. Ground truth, prompts and other data created for this benchmark: CC BY 4.0.

**Consent Procedures:** Not specified

**Compliance with Regulations:** The address book was printed in 1890 and is in the public domain as a work; the Staatsarchiv Basel-Stadt marks the digitised volume as "gemeinfrei" (public domain) in its online reading room. No ethical review was carried out.

## Beyond the BenchmarkCard

This section is not part of the BenchmarkCard schema and is not exported to `benchmark_card.json`.

<!-- Versions are generated from meta.json `versions`, which holds the whole history, newest
     first, one line each as `- X.Y.Z (date) — summary`: `{"version", "date", "commit", "change", "summary"}`, with 0.y.z before the card
     (y: incompatible changes, z: compatible ones). Add an entry there for each change, dated and
     with the commit that made it.
     MAJOR: scores before and after are not comparable (ground truth corrected, scoring or
            ranking metric changed, objects added or removed, response schema or an existing
            prompt's text changed).
     MINOR: something added that leaves existing scores unchanged (e.g. a new prompt variant).
     PATCH: a fix that changes no score (e.g. a better scan of the same image). -->

**Versions:**

- 1.0.1 (2026-11-24) — a coordinate too large for a float counts as one malformed box instead of failing the page; scores unchanged
- 1.0.0 (2026-11-23) — first state, created with its card

**How to Cite:** This benchmark:

> Decker, E., & Kasper, L. (2026). Address Book Layout (benchmark version 1.0.1). In *RISE Humanities Data Benchmark*. Zenodo. https://doi.org/10.5281/zenodo.16941752

Source:

> Staatsarchiv Basel-Stadt, STA H 43 36, 1890. Licence of the source material: Public Domain. https://dls.staatsarchiv.bs.ch/records/1231752/611148/preview

The benchmark suite:

> Hindermann, M., Marti, S., Kasper, L. K., & Bosse, A. (2026). The RISE Humanities Data Benchmark: A Framework for Evaluating Large Language Models for Humanities Tasks. *Journal of Open Humanities Data*, *12*(1), 24. https://doi.org/10.5334/johd.481
>
> Hindermann, M., Kasper, L. K., Marti, S., & Bosse, A. (2026). From Experiments to Epistemic Practice: The RISE Humanities Data Benchmark. *Journal of Open Humanities Data*, *12*(1), 38. https://doi.org/10.5334/johd.470

**Contributors by Role:**

- Domain Expert: Eric Decker
- Data Curator: Eric Decker, Lea Kasper
- Annotator: Eric Decker
- Analyst: Eric Decker
- Engineer: Eric Decker
