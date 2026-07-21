# General Meeting Minutes

## Overview

Extract names, locations, share counts, and signatures from table-like general meeting minutes of Mines de Costano S.A., 1930s–1960s. The documents are typed and handwritten shareholder/voting registers in Italian, French, and German, and the task turns each scanned page into a normalized JSON record.

## Benchmark Structure

**Tags:** minutes, lists, information-extraction

**Scoring Metric:** fuzzy (descending)

## Data

- **Images:** Stored in the `images/` directory (one page per image).
- **Ground Truths:** JSON files in `ground_truths/`. Each ground truth filename matches the corresponding image filename (minus extension).

## Output Format

Model output is validated against the `MinutesPage` Pydantic model (`dataclass.py`):

```python
class Entry(BaseModel):
    number: str
    name: str
    address: str
    actions_o: str
    actions_p: str
    no_de_voix: str
    signature_present: bool = False
    signature: str

class TotalActions(BaseModel):
    total_o: str
    total_p: str
    total_voix: str

class MinutesPage(BaseModel):
    document: str        # document name, passed in via the prompt
    page_number: int     # page number, passed in via the prompt
    entries: List[Entry]
    total_actions: TotalActions
```

`document` and `page_number` are injected into the prompt from the filename (see `get_prompt_kwargs`). `name` and `address` share a single table cell in the source and must be split into separate fields.

## Scoring

Scoring is field-level fuzzy matching (`score_request_answer`):

1. All leaf keys of the ground truth are enumerated (including nested `entries[i].*` and `total_actions.*`).
2. For each key, the model's value at that path is compared to the ground-truth value with `calculate_fuzzy_score` (normalized fuzzy string similarity).
3. The page score is the mean of the per-key scores.

The benchmark score (`score_benchmark`) is the mean of the per-page scores. Higher is better.

## Examples

Input: `images/Se_18_Bilanz1967_page_4.jpg` → expected output (abridged):

```json
{
  "document": "Se_18_Bilanz1967_page_4",
  "page_number": 4,
  "entries": [
    {
      "number": "1",
      "name": "Mr Alain BREHAM ",
      "address": "(Cabinet D. FEAU -\n 132 Boulevard Haussmann - 75 / PARIS 8",
      "actions_o": "179",
      "actions_p": "520",
      "no_de_voix": "699",
      "signature_present": false,
      "signature": ""
    }
  ],
  "total_actions": { "total_o": "601", "total_p": "2217", "total_voix": "2818" }
}
```

## Contributors

- **Domain Expert:** alexandra_binnenkade, sven_lienhard
- **Data Curator:** sven_lienhard
- **Analyst:** sven_lienhard, sorin_marti
- **Engineer:** sorin_marti