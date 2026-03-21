# Anglo Swiss Trade Review

## Overview

Examines a model's ability to extract bounding boxes of advertisments from magazine pages.

## Benchmark Structure

**Tags:** century, document-type, language, layout, script, task, writing

**Scoring Metric:** fuzzy (descending)

## Data

- **Images:** Store images in the `images/` directory
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

- **Domain Expert:** lea_kasper
- **Data Curator:** lea_kasper, sorin_marti
- **Annotator:** lea_kasper, sorin_marti
- **Analyst:** arno_bosse
- **Engineer:** sorin_marti
