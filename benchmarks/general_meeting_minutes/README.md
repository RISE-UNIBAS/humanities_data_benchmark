# General Meeting Minutes

## Overview

Extract names, locations, signatures from table-like metting minutes of Mines de Costano S.A., 1930s - 1960s

## Benchmark Structure

**Tags:** minutes-pages, lists

**Scoring Metric:** fuzzy (descending)

## Data

- **Images:** Store images in the `images/` directory
- **Shared Context:** Store reference documents in the `context/` directory
  - These files are sent once at the beginning and cached
  - Useful for large reference documents that all test items reference
- **Ground Truths:** Store JSON ground truth files in `ground_truths/` directory
  - Each ground truth filename must match the corresponding image/text filename (minus extension)

## Shared Context

This benchmark uses shared context to send reference documents once before processing test items.

**How it works:**
1. Large reference documents are placed in `context/` directory
2. The initial prompt (`context/shared_context_prompt.txt`) is sent with these files
3. Individual test items can then reference this context without re-sending it
4. This saves tokens and costs, especially with Anthropic's prompt caching

**Configuration:**
- Edit `get_shared_context_files()` in `benchmark.py` to specify which files to load
- Edit `context/shared_context_prompt.txt` to customize the initial prompt

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

- **Domain Expert:** sven_lienhard
- **Engineer:** sorin_marti
