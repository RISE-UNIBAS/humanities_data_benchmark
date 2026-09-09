[[start_block=Overview]]

[[start_cell]]

Evaluates models' ability to extract structured schedule data from visual nursing staff duty rosters from a Swiss care facility (April 2025), including shift types, half-day splits, alternate unit assignments, and staff metadata, in German.

[[page-btn-secondary-lg|benchmarks/duty_rosters|Dataset Description]] [[page-btn-primary-lg|benchmark-results?id=duty_rosters|Result Overview]] [[page-btn-primary-lg|testruns?testruns_benchmark=duty_rosters__true&search_button_testruns=Search|Test Runs]]

[[end_cell]]

[[start_cell=40%]]

[[toc]]

[[end_cell]]

[[end_block]]

[[start_block=Dataset Description]]

[[start_cell]]

Data Type

Images (JPG, ~2646x140, ~90 KB each), plus two shared context images (roster header and icon legend) sent once per run

Amount

21 roster rows (one image per staff member)

Origin

Swiss nursing care facility

Signature

04-25_PEP_02-12-01

Language

German

Content Description

Monthly nursing staff duty rosters. Each image is a single staff member's row for the month, containing per-day shift icons, half-day splits, alternate unit assignments, and person metadata (ID, profession, employment percentage, jumper status).

Time Period

2025-04

License

CC BY-NC-SA 4.0

Tags

[[element|duty_rosters_tags]]

[[element|duty_rosters_cont]]

[[end_cell]]

[[start_cell=40%]]

[[element|duty_rosters_img]]

[[end_cell]]

[[end_block]]

[[start_block=Ground Truth]]

[[start_cell=50%]]

Ground truth files follow the Schedule dataclass structure, with schedule-level metadata, a list of persons, and per-day shift entries:

[[start_code=json]]

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

[[end_code]]

[[end_cell]]

[[start_cell]]

Key fields:

icon: Descriptive name from the icon legend (e.g. "F-Dienst 1", "Ferien", "Freier Tag")

length: full, half_left, or half_right (cells can be split into two half-day shifts)

planned_on_current_unit: true if the icon has no red shading, false if the icon has red shading

alternate_unit: Unit abbreviation shown below the cell (e.g. "LE", "TS") if present, null otherwise. Multiple abbreviations for the same date are joined with a comma (e.g. "LE, TS").


The extraction rules are defined in the prompt file.

[[end_cell]]

[[end_block]]

[[start_block=Scoring]]

The benchmark uses F1 micro scoring with field-level fuzzy matching:

Scoring Method

Each terminal (leaf) field across the full nested structure — e.g. year, month, person metadata, and per-day shift fields like persons[0].days[0].shifts[0].icon — is compared between response and ground truth

Fuzzy matching threshold: 0.92 (using rapidfuzz)

Field-level TP/FP/FN calculation:TP (True Positive): Both have values AND fuzzy score ≥ 0.92

FP (False Positive): Response has value but ground truth doesn't, OR fuzzy score < 0.92

FN (False Negative): Ground truth has value but response doesn't, OR fuzzy score < 0.92

Metrics

F1 Micro: Aggregate TP/FP/FN across all rosters, then calculate F1 (used for ranking)

F1 Macro: Calculate F1 per roster, then average

Field Scoring

All leaf fields are scored and weighted equally. There are no configurable field-scoring rules for this benchmark; when parent keys have child keys, only the child (leaf) keys are scored so that structural container fields are not double-counted.

[[end_block]]