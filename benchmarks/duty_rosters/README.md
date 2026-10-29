# Nursing Staff Duty Rosters

This README is a BenchmarkCard (Sokol et al., NeurIPS 2025, arXiv 2410.12974), schema as in evaleval/auto-benchmarkcard v0.2.0.

<!-- Every field stays, in this order; write 'Not specified' when unknown. Fields marked
     (generated) are filled from meta.json and the benchmark's files by
     `python scripts/benchmark_cards.py <name>`; edit meta.json, not the README, to change them. -->

The scoring implementation is in [benchmark.py](benchmark.py), the requested output schema in [dataclass.py](dataclass.py), and the instructions in [prompts/](prompts/).

To run this benchmark, use `python scripts/run_single_test.py --adhoc` from the repository root and select `duty_rosters`. Provider setup is described in the [root README](../../README.md#quick-start); configured prompts, models and scoring rules are recorded in [benchmarks_tests.csv](../benchmarks_tests.csv). Provider-backed runs incur API charges.

## Benchmark Details

**Name:** Nursing Staff Duty Rosters

**Overview:** Evaluates models' ability to extract structured schedule data from an icon-based nursing staff duty roster of a Swiss care facility, April 2025: shift types, half-day splits, alternate unit assignments and staff metadata.

**Data Type:** image

**Domains:**

- nursing science
- health services research
- workforce scheduling

**Languages:**

- German

**Similar Benchmarks:** Not specified

**Resources:**

- https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/duty_rosters
- https://github.com/RISE-UNIBAS/humanities_data_benchmark/tree/main/benchmarks/duty_rosters

**Authors:**

- Ana-Maria Leonte
- Franziska Zúñiga
- Maximilian Hindermann

## Purpose and Intended Users

**Goal:** Measure how well vision-language models read a dense, icon-based staff planning grid: mapping each cell to its date via a separate header, identifying shift icons via a separate legend, and recording half-day splits, shading and alternate unit assignments as structured records. The results are meant to guide nursing and health services researchers who need staffing data from planning sheets that exist only as printouts or scans.

**Audience:**

- health services researchers
- AI researchers
- model developers

**Tasks:**

- table extraction from images
- icon classification against a legend
- date alignment of cells across separate images

**Limitations:** 21 rows from one monthly roster of one ward in one facility; results do not transfer automatically to other roster software, layouts or icon sets. Days and shifts are compared by position, so a model that omits a day or splits a cell differently shifts every later field into a mismatch. All fields count equally, so each row's 30 dates and roughly 31 shifts of four fields each outweigh the four person fields and the year and month. The legend holds 33 icons, of which the ground truth uses 21; `Freier Tag` alone makes up a third of all shifts.

**Out-of-Scope Uses:**

- drawing conclusions about the staff, the ward or the facility
- re-identifying staff members or analysing their absences
- evaluating general table or handwriting recognition

## Data

**Source:** One monthly staff planning sheet (PEP, file `04-25_PEP_02-12-01`) for April 2025 from one ward of a Swiss nursing care facility, provided by Ana-Maria Leonte and Franziska Zúñiga through the INTERSCALE study of the Institute of Nursing Science, University of Basel (https://clinicaltrials.gov/study/NCT06473051). The facility is not named. The sheet was segmented by hand into one image per staff member's row; the roster header (dates and weekdays) and the icon legend are separate images.

**Size:** 21 evaluated objects

**Format:** One JPG per roster row, 2,646 px wide, 85–141 px high and 70–110 KB. Two context images go with every request: `context/roster_header.jpg` (2,646×194 px) and `context/icons.jpg` (1,279×912 px). The file `context/shared_context_prompt.txt` also lists icon names but is not sent; the allowed names reach the model through the `icon` enumeration in `dataclass.py`. The ground truth is one JSON file per row, following the `Schedule` dataclass in `dataclass.py`:

```json
{
  "year": 2025,
  "month": "April",
  "persons": [
    {
      "id": "103",
      "profession": "WBL",
      "employment_percent": 80,
      "is_jumper": false,
      "days": [
        {
          "date": "2025-04-01",
          "shifts": [
            {
              "icon": "F-Dienst 1",
              "length": "full",
              "planned_on_current_unit": true,
              "alternate_unit": "LE"
            }
          ]
        },
        {
          "date": "2025-04-11",
          "shifts": [
            {
              "icon": "HomeOffice",
              "length": "half_left",
              "planned_on_current_unit": true,
              "alternate_unit": null
            },
            {
              "icon": "Freier Tag",
              "length": "half_right",
              "planned_on_current_unit": true,
              "alternate_unit": null
            }
          ]
        }
      ]
    }
  ]
}
```

- `id`: the staff number written in the row's margin
- `profession`: the section label printed above the row (e.g. `WBL`, `SRK`, `Tertiär`); not scored, because the row images do not show it
- `employment_percent`, `is_jumper`: the employment percentage and the `S` (jumper) column
- `icon`: the legend name of the cell's icon, or `null` for an empty cell
- `length`: `full`, `half_left` or `half_right`; a split cell gives two entries for the same date
- `planned_on_current_unit`: `false` if the icon has red shading or a red border
- `alternate_unit`: the unit abbreviation below the cell (e.g. `LE`, `TS`), several joined with a comma, or `null`

Every row covers all 30 days of April; the 21 rows hold 656 shifts.

**Annotation:** Maximilian Hindermann (annotator) created the ground truth by hand, with Ana-Maria Leonte and Franziska Zúñiga as domain experts, following the extraction rules in the [prompt file](prompts/prompt.txt).

**Size Breakdown:**

- image files: 21

**Collection Date:** Source documents: April 2025. Added to the benchmark: April 2026.

**Contamination Controls:** None. The images, prompt and ground truth have been public in this repository since April 2026.

## Methodology

**Methods:**

- zero-shot structured extraction; each request carries the header image, the legend image and one roster row
- structured JSON output requested using the `Schedule` dataclass, with `icon` restricted to the 33 legend names
- benchmark default output cap of 98,304 tokens; a test rule can override it and model-specific ceilings can lower it

**Metrics:**

- F1 micro (`f1_micro`, used for ranking)
- F1 macro (`f1_macro`)

**Calculation:** Every terminal field present in the response or the ground truth (for example `persons[0].days[4].shifts[0].icon`) is compared at the same path; empty strings count as missing. Values are compared with a rapidfuzz similarity score on their string form, and a field is a match at a score of 0.92 or above.

- TP: both have a value and the score is at least 0.92
- FP and FN: both have a value but the score is below 0.92 (the field counts once as each)
- FP: only the response has a value
- FN: only the ground truth has a value

`profession` is not scored. A `null` icon or alternate unit on both sides counts as nothing. F1 micro sums TP, FP and FN over all rows before computing F1; F1 macro averages the per-row F1 values, each rounded to two decimals. There are no configurable field-selection rules. A response that cannot be parsed is scored as a miss: every ground-truth field counts as a false negative.

**Interpretation:** Scores range from 0 to 1; higher is better. Both metrics are dominated by the shift fields, about 120 of the roughly 130 fields per row, so a score mainly reflects how well a model reads the shift icons, half-day splits, shading and alternate units. Across the 89 active test configurations, F1 micro has a median of 0.78 and an interquartile range of 0.71–0.86; the best reach 0.97.

**Baseline Results:** Model results are available on the [benchmark page](https://rise-services.rise.unibas.ch/benchmarks/p/benchmarks/duty_rosters) and in `results/<date>/<test_id>/` at the repository root. Compare runs with the same prompt, scoring rules and ground-truth revision, and report the number of successfully scored objects alongside the score. There is no fixed model baseline with a run ID and date.

Observed across models: the shift icon is the field read worst (38% of icons correct across all stored runs), followed by the alternate unit (49%) and the shading flag `planned_on_current_unit` (73%). Mapping cells to their dates through the separate header works comparatively well (88%). Models also confuse empty cells with `Freier Tag` or assign icons such as `HomeOffice` to them.

**Validation:** The ground truth was created by a single annotator, Maximilian Hindermann; no second check is recorded. Scoring is deterministic; the scorer is covered by `tests/test_duty_rosters_scoring.py`.

**Human Baseline:** Not specified

**Judge Uses LLM:** false

**Judge Num:** Not specified

**Judge Models:** Not specified

**Judge Score Consolidation:** Not specified

**Validity Justification:** Field-level F1 reflects the downstream use: each shift becomes a record in a staffing dataset, so a field is either usable or needs correction.

## Ethical and Legal Considerations

**Privacy and Anonymity:** The roster is from April 2025 and covers living people. It was anonymised by the facility before release: neither the images nor the ground truth contain names, staff are identified only by the IDs the INTERSCALE study assigned (the handwritten numbers in the margin), the facility is not named, and the ward label is cropped from the header image. Each row records a profession group, employment percentage and a month of shifts and absences, including sick days (two rows) and a month of maternity protection (one row).

**Data Licensing:** Source material: CC BY 4.0. Ground truth, prompts and other data created for this benchmark: CC BY 4.0.

**Consent Procedures:** The facility released the anonymised roster for publication through the INTERSCALE study.

**Compliance with Regulations:** As the roster is anonymised and carries only study IDs (see Privacy and Anonymity), it contains no personal data that identifies staff. The facility granted its use under CC BY 4.0 through the INTERSCALE study. No separate ethical review was carried out for the benchmark.

## Beyond the BenchmarkCard

This section is not part of the BenchmarkCard schema and is not exported to `benchmark_card.json`.

<!-- Versions use semantic versioning, newest first, one line each: `- MAJOR.MINOR.PATCH — what
     changed and why`.
     MAJOR: scores before and after are not comparable (ground truth corrected, scoring or
            ranking metric changed, objects added or removed).
     MINOR: something added that leaves existing scores unchanged (e.g. a new prompt variant).
     PATCH: a fix that changes no score (e.g. a better scan of the same image). -->

**Versions:**

- 3.0.0 — `profession` is no longer scored (the section label is not in the row images); a response that cannot be parsed is scored as a miss; all stored runs re-scored
- 2.0.0 — ground truth corrected: staff ids `SaA410` and `S402` as written in the margin (were `23` and `402`); row 109, 29 April: the right half of the split cell (Persönliche Absenz) added and the alternate unit removed; all stored runs re-scored against the corrected ground truth
- 1.0.0 — initial versioned state

**How to Cite:** This benchmark:

> Leonte, A.-M., Zúñiga, F., & Hindermann, M. (2026). Nursing Staff Duty Rosters (benchmark version 3.0.0). In *RISE Humanities Data Benchmark*. Zenodo. https://doi.org/10.5281/zenodo.16941752

Source:

> Swiss nursing care facility (not named), via the INTERSCALE study, 04-25_PEP_02-12-01, April 2025. Licence of the source material: CC BY 4.0. https://clinicaltrials.gov/study/NCT06473051

The benchmark suite:

> Hindermann, M., Marti, S., Kasper, L. K., & Bosse, A. (2026). The RISE Humanities Data Benchmark: A Framework for Evaluating Large Language Models for Humanities Tasks. *Journal of Open Humanities Data*, *12*(1), 24. https://doi.org/10.5334/johd.481
>
> Hindermann, M., Kasper, L. K., Marti, S., & Bosse, A. (2026). From Experiments to Epistemic Practice: The RISE Humanities Data Benchmark. *Journal of Open Humanities Data*, *12*(1), 38. https://doi.org/10.5334/johd.470

**Contributors by Role:**

- Domain Expert: Ana-Maria Leonte, Franziska Zúñiga
- Data Curator: Ana-Maria Leonte, Franziska Zúñiga
- Annotator: Maximilian Hindermann
- Analyst: Maximilian Hindermann
- Engineer: Maximilian Hindermann
