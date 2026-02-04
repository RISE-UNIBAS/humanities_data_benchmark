# Personnel Cards

## Overview



## Benchmark Structure

**Tags:** index-cards, table-like, handwritten-source, typed-source, printed-source, century-20th, transcription, interpretation

**Scoring Metric:** F1 macro (descending), F1 micro (radar chart)

## Data

- **Images:** Store images in the `images/` directory
- **Ground Truths:** Store JSON ground truth files in `ground_truths/` directory
  - Each ground truth filename must match the corresponding image/text filename (minus extension)

## Ground Truth Format

Ground truth files follow the `Table` dataclass structure with multiple rows:

```json
{
  "rows": [
    {
      "row_number": 1,
      "dienstliche_stellung": {
        "diplomatic_transcript": "Assist.",
        "interpretation": "Assistant",
        "is_crossed_out": false
      },
      "dienstort": {
        "diplomatic_transcript": "Basel",
        "interpretation": null,
        "is_crossed_out": false
      },
      "gehaltsklasse": {
        "diplomatic_transcript": "III",
        "interpretation": "3",
        "is_crossed_out": false
      },
      "jahresgehalt_monatsgehalt_taglohn": {
        "diplomatic_transcript": "Fr. 2400.-",
        "interpretation": "2400 CHF",
        "is_crossed_out": false
      },
      "datum_gehaltsänderung": {
        "diplomatic_transcript": "1.4.1920",
        "interpretation": "1920-04-01",
        "is_crossed_out": false
      },
      "bemerkungen": {
        "diplomatic_transcript": "",
        "interpretation": null,
        "is_crossed_out": false
      }
    }
  ]
}
```

Each `FieldValue` has three sub-fields:
- **`diplomatic_transcript`**: Exact text as written on the card, including abbreviations
- **`interpretation`**: Interpretation or expansion of abbreviations and meanings (optional)
- **`is_crossed_out`**: Boolean indicating if text is crossed out on the card

## Scoring

The benchmark uses **F1 micro scoring** with field-level fuzzy matching:

### Scoring Method
- Each terminal field (e.g., `rows[0].dienstliche_stellung.diplomatic_transcript`) is compared between response and ground truth
- Fuzzy matching threshold: 0.92 (using rapidfuzz)
- Field-level TP/FP/FN calculation:
  - **TP (True Positive)**: Both have values AND fuzzy score ≥ 0.92
  - **FP (False Positive)**: Response has value but ground truth doesn't, OR fuzzy score < 0.92
  - **FN (False Negative)**: Ground truth has value but response doesn't, OR fuzzy score < 0.92

### Metrics
- **F1 Micro**: Aggregate TP/FP/FN across all cards, then calculate F1 (used for ranking)
- **F1 Macro**: Calculate F1 per card, then average (used for radar chart)

### Rules Configuration

The benchmark supports configurable field scoring through the `rules` column in `benchmarks_tests.csv`.

**Default Rules:**
```json
{
  "score_diplomatic_transcript": true,
  "score_interpretation": true,
  "score_is_crossed_out": true
}
```

When `rules` is empty or omitted in `benchmarks_tests.csv`, these defaults apply.

**Available Flags:**
- `score_diplomatic_transcript` - Score diplomatic transcript fields
- `score_interpretation` - Score interpretation fields
- `score_is_crossed_out` - Score is_crossed_out boolean fields

**Example Configurations:**

1. Explicit default (same as empty rules):
   ```json
   {"score_diplomatic_transcript": true, "score_interpretation": true, "score_is_crossed_out": true}
   ```

2. Score only diplomatic transcript:
   ```json
   {"score_diplomatic_transcript": true, "score_interpretation": false, "score_is_crossed_out": false}
   ```

3. Score transcript + interpretation only (exclude is_crossed_out):
   ```json
   {"score_diplomatic_transcript": true, "score_interpretation": true, "score_is_crossed_out": false}
   ```

**Note:** The `row_number` field is never scored as it's structural metadata.

## Examples

TODO: Add example inputs and expected outputs.

## Contributors

- **Domain Expert:** tabea_wullschleger
- **Data Curator:** tabea_wullschleger
- **Annotator:** tabea_wullschleger
- **Engineer:** maximilian_hindermann
