# Nursing Staff Duty Rosters

## Overview

Monthly nursing staff duty rosters from a Swiss care facility. Each image shows one row from a roster, representing a single staff member's schedule for the month. Models must identify shift icons, half-day splits, alternate unit assignments, and person metadata.

Images are paired with two shared context images sent once per benchmark run:
- **roster_header.jpg** — the roster header with unit name, month/year, and date columns
- **icons.jpg** — the icon legend mapping visual shift indicators to their codes

## Data

- 4 images (100, 103, S414, S420), ~1200x100 pixels each
- Language: German
- Source: Swiss nursing care facility, April 2025

## Ground Truth Format

```json
{
  "unit": "1. Stock OST",
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
        }
      ]
    }
  ]
}
```

Key fields:
- **icon**: Descriptive name from the icon legend (e.g. "F-Dienst 1", "Ferien", "Freier Tag")
- **length**: `full`, `half_left`, or `half_right` (cells can be split into two half-day shifts)
- **planned_on_current_unit**: `true` if the icon has no red shading, `false` if the icon has red shading
- **alternate_unit**: Unit abbreviation shown below the cell (e.g. "LE", "TS") if present, null otherwise

## Scoring

**F1 Micro** with field-level fuzzy matching (threshold: 0.92, rapidfuzz).

All leaf fields are scored (unit, year, month, person metadata, and per-day shift fields). TP/FP/FN are calculated per field across the full nested structure. F1 Macro (per-image F1 averaged) is also reported.

## Ideas for Improvement

1. **Composite header + row into a single image.** The header and roster row are currently sent as separate images, forcing models to align columns across images. Stitching the header directly above each row would make date-to-cell mapping visual and trivial — this is the single largest error source (~50% of dates are wrong).

2. **Use day-of-month integers instead of ISO dates.** Converting cell position to a day number and then to an ISO date string is two steps of error. Since year and month are already captured at the Schedule level, `date: 17` would be simpler than `"2025-04-17"`.

3. **Separate icon recognition from structure extraction in scoring.** Report a structure score (dates, length, planned_on_current_unit, alternate_unit, person metadata) and an icon score separately. This gives more diagnostic value than a single F1 number.

4. **Crop individual cells for icon classification.** As a benchmark variant: pre-crop each day cell and pair it with the legend, asking "which icon is this?" This isolates icon recognition from layout understanding and reveals where the real bottleneck is.

5. **Add a visual example of an empty cell to the legend.** Models confuse null (no icon) with "Freier Tag" or hallucinate icons like "HomeOffice" for empty cells. Showing what "no icon" looks like in the legend could help.

6. **Score fields with different weights.** Currently all leaf fields count equally, so ~128 shift-level entries dominate 4 person-level fields. Consider per-day accuracy or separate person-metadata vs shift-level reporting.

7. **Reduce the active icon vocabulary.** The legend has 33 icons but the ground truth only uses ~8. Noting the active subset in the prompt or evaluating icon accuracy within the active set would be informative.