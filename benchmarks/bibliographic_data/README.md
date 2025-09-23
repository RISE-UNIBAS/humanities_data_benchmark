# Bibliographic Data Extraction Benchmark

## Table of Contents
- [Overview](#overview)
- [Creator](#creator)
- [Dataset Description](#dataset-description)
- [Ground Truth](#ground-truth)
- [Scoring](#scoring)
- [Results](#results)
- [Observations](#observations)
- [Limitations and Future Work](#limitations-and-future-work)

## Overview

This benchmark evaluates the performance of large language models on extracting structured bibliographic information from historical academic documents. The benchmark consists of 5 pages from the "Bibliography of Works in the Philosophy of History, 1945–1957", each containing multiple bibliographic entries that models must extract and structure according to a predefined JSON schema.

## Creator

This benchmark was created by the University of Basel's Research and Infrastructure Support RISE (rise@unibas.ch) in 2025, based on the scholarly resource compiled by John C. Rule and published in 1961.

| Role          | Contributors                   |
|---------------|--------------------------------|
| Domain expert | [Pema Frick]                   |
| Data curator  | [Pema Frick]                   |
| Annotator     | [Sven Burkhardt], [Pema Frick] |
| Analyst       | [Pema Frick], [Sorin Marti]    |
| Engineer      | [Pema Frick], [Sorin Marti]    |


For detailed contributor information and role descriptions, see [CONTRIBUTORS.md](https://github.com/RISE-UNIBAS/humanities_data_benchmark/blob/main/CONTRIBUTORS.md).

## Dataset Description

### Source
- **Collection**: Bibliography of Works in the Philosophy of History, 1945–1957
- **Time Period**: 1945-1957 (works covered), 1961 (publication date)
- **Language**: English
- **Format**: Printed academic bibliography
- **Link**: http://www.jstor.org/stable/2504495
- **License**: Academic use

### Contents
The dataset contains 5 pages from a comprehensive scholarly bibliography published as "Chronological List." History and Theory, vol. 1, 1961, pp. 1–74. Each page contains multiple bibliographic entries listing books, articles, and other scholarly works that contribute to the philosophy of history. Entries include standard bibliographic information (author, title, publisher, year) and may contain cross-references to other entries, reviews, and additional notes.

#### Example Page
Below is an example of a typical bibliography page showing the structure and format of entries that models must extract:

![Bibliography Page 2](https://github.com/RISE-UNIBAS/humanities_data_benchmark/blob/main/benchmarks/bibliographic_data/images/page_2.jpeg?raw=true)

## Ground Truth

### Ground Truth Creation
The ground truth was manually created by domain experts who extracted and structured the bibliographic information according to the defined schema. Each entry was  annotated to capture all relevant bibliographic details, cross-references, and structural relationships between entries.

### Ground Truth Format
The ground truth is stored in JSON files with the following structure based on the dataclass schema:

```json
{
  "metadata": {
    "title": "Books",
    "year": "1945", 
    "page_number": 2
  },
  "entries": [
    {
      "id": "1",
      "type": "book",
      "title": "Time as Dimension and History",
      "author": [
        {"family": "Alexander", "given": "Hubert G."}
      ],
      "publisher": "University of New Mexico Press",
      "publisher_place": "Albuquerque",
      "issued": 1945
    },
    {
      "id": "6",
      "type": "journal-article",
      "title": "Review of The Use of Personal Documents",
      "author": [
        {"family": "Lapiere", "given": "R. T."}
      ],
      "container_title": "The American Journal of Sociology",
      "volume": "LII",
      "issued": 1946,
      "relation": {
        "reviewed": "5"
      }
    }
  ]
}
```

## Scoring

### Evaluation Criteria
The models are tasked with extracting bibliographic entries from academic bibliography pages and outputting a structured JSON document. Models must identify and extract:

- **Entry identification**: Unique identifiers for each bibliographic entry
- **Entry classification**: Type of work (book, journal-article, review, other)
- **Author information**: Family and given names of all authors
- **Publication details**: Title, publisher, place, year, volume, pages as available
- **Cross-references**: Relationships between entries (reviews, reprints, etc.)
- **Incomplete entries**: Detection of entries that continue on subsequent pages

### Expected Output Format
Models should output a JSON structure matching the dataclass schema with complete metadata and entry information.

### Scoring Methodology
The extracted data is compared to the ground truth using fuzzy string matching with field-level evaluation:

1. **Field Extraction**: All terminal fields from both model response and ground truth are extracted
2. **Field Comparison**: Each field is compared using fuzzy string matching (RapidFuzz) with a threshold for exact matches
3. **Score Calculation**: A score between 0 and 1 is assigned to each field based on similarity
4. **Total Score**: The final score is computed as the average accuracy across all fields

### Example Scoring
For a bibliographic entry with 8 extractable fields where the model correctly extracts 6 fields with perfect matches and 2 fields with partial matches (0.8 similarity each), the score would be: (6 × 1.0 + 2 × 0.8) / 8 = 0.95

## Observations

Common challenges include:
- Complex multi-author entries
- Abbreviated journal titles and volume notations
- Distinguishing between reviews and reviewed works
- Handling incomplete entries that span pages

## Limitations and Future Work

### Current Limitations
- **Dataset Size**: Only 5 pages may not capture full range of bibliographic complexity
- **Time Period**: Limited to mid-20th century academic style
- **Language**: English-only content
- **Domain**: Focused specifically on philosophy of history

### Future Work
- **Expand Dataset**: Include more pages and different bibliographic styles
- **Multi-language Support**: Add bibliographies in German, French, and other languages
- **Cross-domain Testing**: Test on bibliographies from different academic disciplines
- **Temporal Coverage**: Include bibliographies from different historical periods
- **Advanced Features**: Add support for more complex citation relationships and metadata

[Sven Burkhardt]: https://orcid.org/0009-0001-4954-4426
[Pema Frick]: https://orcid.org/0000-0002-8733-7161
[Sorin Marti]: https://orcid.org/0000-0002-9541-1202