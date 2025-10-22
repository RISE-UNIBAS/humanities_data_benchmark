# Recognition of medieval handwriting: Page Segmentation and Textual Extraction of Medieval Manuscripts

## Table of Contents
- [Overview](#overview)
- [Creator](#creator)
- [Medieval Manuscripts](#medman)
- [Ground Truth](#ground-truth)
  - [Guidelines for creating the ground truth](#guidelines-for-creating-the-ground-truth)
  - [Metadata schema](#metadata-schema)
- [Scoring](#scoring)
  - [Scoring a page](#scoring-a-page)
  - [Scoring the collection](#scoring-the-collection)
- [Future Enhancements](#future-enhancements)

## Overview

This benchmark evaluates the ability of language models to extract structured information from medieval manuscripts. It focuses on the extraction of text from digitized images. The benchmark tests the model's ability to:

1. Correctly identify sections that contain handwritten text (in case of two columns or writing at the margins)
2. Extract the text for every section, namely "text" and "addition1", "addition2", "addition3", etc
3. Maintain historical spelling, punctuation, and formatting
4. Include folio number if present


## Creator

This benchmark was created by the University of Basel's Research and Infrastructure Support RISE (rise@unibas.ch) in 2025.

| Role | Contributors |
|------|-------------|
| Domain expert | [Ina Serif] |
| Data curator | [Ina Serif] |
| Annotator | [Ina Serif] |
| Analyst | [Maximilian Hindermann] |
| Engineer | [Maximilian Hindermann], [Ina Serif] |

For detailed contributor information and role descriptions, see [CONTRIBUTORS.md](https://github.com/RISE-UNIBAS/humanities_data_benchmark/blob/main/CONTRIBUTORS.md).

## Medieval Manuscripts

The variety of medieval handwriting is enormous, and the quality of a scripts depends on the time and place of creation, the scope of use and the capacities of the scribe. 
While software for handwritten text recognition offers generic models that can be used for a variety of scripts, it seems worth to compare the output of LLMs when confronted with specific writing.

The first set of ground truth images comes from a 15th century manuscript written in Basel, in late medieval German: [Basel, Universitätsbibliothek, H V 15](www.e-codices.ch/de/description/ubb/H-V-0015/HAN).
It was written by two scribes.


## Ground Truth

The ground truth for this benchmark consists of manually transcribed pages of a selection of pages of the manuscript Basel, Universitätsbibliothek, H V 15.

### Guidelines for creating the ground truth

The following guidelines were used when creating the ground truth:

1. **Main text and additions**: The main text is labeled as such; additions on the margins are labeled as such
2. **Folio numbering**: The folio numbers are extracted and stored in the json of the page
1. **Historical Accuracy**: All historical spellings, typographical errors, and formatting are maintained
2. **Completeness**: All text on a page is transcribed

### Metadata schema

Each manuscript page in the ground truth is represented as a JSON object with the following properties:

| Field | Type | Description |
|-------|------|-------------|
| `folio` | string | Folio number (e.g., "3", "4") |
| `text` | string | Complete text of the main text as it appears in the original |
| `addition1` | string | Complete text of the first marginal addition (empty string if not present) |
| `addition2` | string | Complete text of the second marginal addition (empty string if not present) |
| `addition3` | string | Complete text of the third marginal addition (empty string if not present) |


The entire ground truth file follows this structure:

```json
{
  "[3r]": [
    {
      "folio": "3",
      "text": "Vnd ein pferit die mir vnd\n minen knechten vber hulfend\n den do was nienan kein weg\n denne den wir machtend\n vnd vielend die knecht dick\n vnd vil in untz an den ars\n vnd die pferit vntz an die \n settel vnd was ze mol ein grosser\n nebel dz wir kum gesachend\n vnd also mit grosser arbeit kome\n wir ze mittem tag zuo sant\n kristoffel vff den berg Do\n Do sach ich die buecher Do gar\n vil herren wopen in stond\n die ir stür do hin geben hand\n do stuond mines vatters seligen\n wopen och in dem einen",
      "addition1": ""
    }
  ]
}
```

## Scoring

The benchmark uses two complementary metrics to evaluate the accuracy of extracted text: Fuzzy String Matching and Character Error Rate (CER).

### Scoring a page

Each element - "folio", "text" and "addition1", "addition2", "addition3", etc. - is scored by comparing it to the corresponding ground truth entry using the following process:

1. **Entry Matching**: Model responses are matched to ground truth entries by position. Ground truth entries are sorted alphabetically by folio reference (e.g., [3r], [4v]), and the first response entry is matched to the first ground truth entry, the second to the second, etc.
2. **Field Comparison**: For each matched entry, individual fields (folio, text, additions) are compared between the model's response and ground truth
3. **Text Comparison**: Two metrics are calculated for each field:
   - **Fuzzy Score**: Text content is compared using fuzzy string matching, resulting in a similarity score between 0.0 and 1.0 (higher is better)
   - **Character Error Rate (CER)**: Calculated using Levenshtein distance as a ratio of the reference text length, resulting in an error rate between 0.0 and 1.0 (lower is better)
4. **Empty Field Handling**: Fields that are empty in both ground truth and prediction are excluded from scoring (correctly empty fields don't affect the score)
5. **Missing Content**: Fields with content in ground truth but missing in the response receive a fuzzy score of 0.0 and a CER of 1.0

#### Fuzzy Matching Example

For a ground truth text line:
```
"Vnd ein pferit die mir vnd"
```

And a model response:
```
"und ein pferit die mir vnd"
```

The fuzzy matching would yield a high similarity score (approximately 0.99) despite the minor spelling difference ("Vnd" vs. "und").

#### Character Error Rate (CER) Example

For the same example, the CER would be calculated as follows:
1. Calculate the Levenshtein distance (edit distance): 1 character substitution
2. Calculate the CER: 1 / (length of reference text) ≈ 0.01

This results in a very low CER score (approximately 0.01), indicating excellent performance.

### Scoring the collection

The overall benchmark scores are calculated as follows:

1. **Fuzzy Score**: The average of the fuzzy matching scores across all texts, producing a value between 0.0 and 1.0, where higher scores indicate better performance.
2. **CER Score**: The average of the character error rates across all texts, producing a value between 0.0 and 1.0, where lower scores indicate better performance.

These metrics account for:
- Correctly identified sections - text and addtions
- Correctly matched folio numbers
- Textual similarity to the ground truth

A perfect result would have a fuzzy score of 1.0 and a CER of 0.0, indicating that all texts were identified and transcribed with perfect fidelity to the original text.

### Benchmark Sorting

In the benchmark overview page, medieval manuscript results are sorted by fuzzy score in descending order (highest scores at the top), allowing for quick identification of the best-performing models.

## Future Enhancements

Planned extensions to this benchmark include:

1. **Expanded Dataset**: Including more pages and time periods from medieval manuscripts
2. **Multi-language Support**: Extending to manuscripts with mixed language content

[Maximilian Hindermann]: https://orcid.org/0000-0002-9337-4655
[Ina Serif]: https://orcid.org/0000-0003-2419-4252
