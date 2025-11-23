# Fraktur OCR: Metadata and Textual Extraction of Classified Ads in the Basler Avisblatt (1729-1844)

## Table of Contents
- [Overview](#overview)
- [Creator](#creator)
- [Basler Avisblatt](#basler-avisblatt)
- [Ground Truth](#ground-truth)
  - [Guidelines for creating the ground truth](#guidelines-for-creating-the-ground-truth)
  - [Metadata schema](#metadata-schema)
- [Scoring](#scoring)
  - [Scoring an ad](#scoring-an-ad)
  - [Scoring the collection](#scoring-the-collection)
- [Future Enhancements](#future-enhancements)

## Overview

This benchmark evaluates the ability of language models to extract structured information from historical documents printed in Fraktur (Gothic) typeface. Specifically, it focuses on the extraction of metadata and text from classified advertisements in the early modern newspaper "Basler Avisblatt" (1729-1844). The benchmark tests the model's ability to:

1. Correctly identify advertisement sections and their hierarchical structure
2. Extract individual advertisements with their numerical prefixes
3. Maintain historical spelling, punctuation, and formatting
4. Accurately count tokens in the extracted text
5. Identify publication dates in correct ISO format

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

## Basler Avisblatt

The "Basler Avisblatt" was an early advertisement newspaper published in Basel, Switzerland. This benchmark uses the digital collection available at the University Library Basel (shelf mark: `UBH Ztg 1`, digital collection: [https://avisblatt.dg-basel.hasdai.org](https://avisblatt.dg-basel.hasdai.org/search?q=&l=list&p=1&s=10&sort=newest)).

The collection comprises 116 yearbooks spanning the newspaper's publication history, with approximately 52 issues per year (increasing to more issues during the 1840s). Each issue varies in length from 1 to 16 pages and contains primarily classified advertisements, alongside occasional news articles, price lists, and announcements. The text is printed in traditional Gothic/Fraktur typeface, presenting challenges for modern OCR technologies and language models.

## Ground Truth

The ground truth for this benchmark consists of manually transcribed and structured data from selected pages of the Basler Avisblatt. Each advertisement is categorized with metadata and its complete text content, preserving the original formatting, spelling, and punctuation.

### Guidelines for creating the ground truth

The following guidelines were used when creating the ground truth:

1. **Section Structure**: Advertisements are grouped under section headings (e.g., "Es werden zum Verkauff offerirt")
2. **Numbering**: The original numerical prefixes (e.g., "1.", "2.") are preserved
3. **Historical Accuracy**: All historical spellings, typographical errors, and formatting are maintained
4. **Completeness**: Every advertisement on the page is included
5. **Column Order**: Advertisements are processed sequentially by column, from left to right

### Metadata schema

Each advertisement in the ground truth is represented as a JSON object with the following properties:

| Field | Type | Description |
|-------|------|-------------|
| `date` | string | Publication date in ISO 8601 format (YYYY-MM-DD) |
| `tags_section` | string | Title of the section containing the advertisement |
| `ntokens` | integer | Number of words/tokens in the advertisement text |
| `text` | string | Complete text of the advertisement as it appears in the original |

The entire ground truth file follows this structure:

```json
{
  "[key_id]": [
    {
      "date": "1731-01-02",
      "tags_section": "Es werden zum Verkauff offerirt",
      "ntokens": 21,
      "text": "1. Ein Stücklein von in circa 20. Saum extra schön und guter rother Marggräffer-Wein von Anno 1728. in raisonnablem Preiß."
    }
  ],
  ...
}
```

## Scoring

The benchmark uses two complementary metrics to evaluate the accuracy of extracted advertisements: Fuzzy String Matching and Character Error Rate (CER).

### Scoring an ad

Each advertisement is scored by comparing it to the corresponding ground truth entry using the following process:

1. **Section Matching**: Advertisements are matched across response and ground truth based on section names, using exact matching first and fuzzy matching with a 95% similarity threshold as a fallback
2. **Number Matching**: Within each section, advertisements are matched by their numerical prefixes
3. **Text Comparison**: Two metrics are calculated for each matched advertisement:
   - **Fuzzy Score**: Text content is compared using fuzzy string matching, resulting in a similarity score between 0.0 and 1.0 (higher is better)
   - **Character Error Rate (CER)**: Calculated using Levenshtein distance as a ratio of the reference text length, resulting in an error rate between 0.0 and 1.0 (lower is better)
4. **Missing Matches**: Advertisements in the ground truth that aren't found in the response receive a fuzzy score of 0.0 and a CER of 1.0

#### Fuzzy Matching Example

For a ground truth advertisement:
```
"5. Eine zimblich wohl-conditionirte Violino di Gamba, so im Adresse-Contor kan gesehen werden."
```

And a model response:
```
"5. Eine zimlich wohl-conditionirte Violino di Gamba, so im Adresse-Contor kan gesehen werden."
```

The fuzzy matching would yield a high similarity score (approximately 0.99) despite the minor spelling difference ("zimblich" vs. "zimlich").

#### Character Error Rate (CER) Example

For the same example, the CER would be calculated as follows:
1. Calculate the Levenshtein distance (edit distance): 1 character substitution
2. Calculate the CER: 1 / (length of reference text) ≈ 0.01

This results in a very low CER score (approximately 0.01), indicating excellent performance.

### Scoring the collection

The overall benchmark scores are calculated as follows:

1. **Fuzzy Score**: The average of the fuzzy matching scores across all advertisements, producing a value between 0.0 and 1.0, where higher scores indicate better performance.
2. **CER Score**: The average of the character error rates across all advertisements, producing a value between 0.0 and 1.0, where lower scores indicate better performance.

These metrics account for:
- Correctly identified section headings
- Correctly matched advertisement numbers
- Textual similarity to the ground truth

A perfect result would have a fuzzy score of 1.0 and a CER of 0.0, indicating that all advertisements were identified and transcribed with perfect fidelity to the original text.

### Benchmark Sorting

In the benchmark overview page, Fraktur results are sorted by fuzzy score in descending order (highest scores at the top), allowing for quick identification of the best-performing models.

## Future Enhancements

Planned extensions to this benchmark include:

1. **Entity Extraction**: Adding evaluation of named entity recognition for persons and places mentioned in advertisements
2. **Expanded Dataset**: Including more pages and time periods from the Basler Avisblatt collection
3. **Fine-grained Categorization**: Adding classification of advertisement types (sales, rentals, lost items, etc.)
4. **Multi-language Support**: Extending to other historical newspapers with mixed language content

[Maximilian Hindermann]: https://orcid.org/0000-0002-9337-4655
[Ina Serif]: https://orcid.org/0000-0003-2419-4252
