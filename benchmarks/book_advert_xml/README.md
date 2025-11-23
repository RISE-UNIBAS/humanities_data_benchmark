# Book Advert XML files (malformed) from Avisblatt

## Overview

blblb

## Benchmark Structure

**Tags:** century-18th

**Scoring Metric:** f1_macro (descending)

## Data

- **Texts:** Store text files in the `texts/` directory
- **Ground Truths:** Store JSON ground truth files in `ground_truths/` directory
  - Each ground truth filename must match the corresponding image/text filename (minus extension)

## Ground Truth Format

```json
{
  "field1": "value1",
  "field2": ["item1", "item2"]
}
```

## Scoring

TODO: Describe how scoring works for this benchmark.

## Examples

TODO: Add example inputs and expected outputs.

## Contributors

- **Domain Expert:** ina_serif
- **Data Curator:** sorin_marti
