# Multilanguage Multiscript Bibliographic Data

## Overview

Evaluates models' ability to extract structured bibliographic information from multilingual, multiscript documents. This benchmark uses a catalog of publications from the Afghan resistance movement (1979-1992), containing entries written in multiple scripts (Arabic/Persian script and Latin romanization) and multiple languages (Farsi, Pashtu, German). Tests the model's capability to handle complex bibliographic records with parallel titles, author names in different scripts, and metadata spanning different calendar systems (Hijri and Gregorian).

## Description

This benchmark challenges vision-language models to:
- **Extract structured data** from dense bibliographic catalog pages
- **Handle multiple scripts simultaneously** (Arabic/Persian and Latin alphabets)
- **Process multilingual content** (Farsi, Pashtu, German translations)
- **Capture parallel metadata** (titles in Arabic, transliterated, and German forms)
- **Parse complex publication details** (dual calendar systems, organizational affiliations)
- **Maintain accuracy** across 1,546 bibliographic entries from historical resistance literature

The source material consists of a scholarly catalog documenting monographic writings and periodicals published by the Afghan resistance movement during the Soviet-Afghan War, originally compiled in German with Arabic script titles and transliterations.

## Benchmark Structure

**Tags:** multilingual, multiscript, bibliographic, historical, structured-extraction

**Scoring Metrics:**
- **Primary:** `combined_score` - Harmonic mean of F1 and field quality (descending)
- **F1 Score:** Entry detection accuracy (precision/recall)
- **Field Score:** Weighted fuzzy matching of extracted fields

**Ranking Order:** Descending (higher is better)

## Data

- **Images:** 6 catalog page images in `images/` directory (300 DPI JPG format)
- **Ground Truth:** Single comprehensive JSON file containing all 1,546 bibliographic entries
  - File: `ground_truths/katalog_master_Qudsia_20251211.json`
- **PDF Source:** Original catalog PDF available for reference

## Ground Truth Format

The ground truth is structured as a list of bibliographic entries, each containing:

```json
{
  "entries": [
    {
      "id": "0001",
      "author": "GHEIRAT, ABDOLBARI",
      "title": {
        "arabic": "آثار چاپی در معضله افغانستان",
        "transliterated": "Asar-e chapi dar mo'azeleh-ye afghanestan",
        "german": "Publikationen der afghanischen Widerstandsbewegung"
      },
      "author_arabic": "عبد الباری غیرت",
      "publication_details": {
        "organization": "Jami'at-e eslami",
        "year_hijri": 1362,
        "year_gregorian": 1983,
        "place": "Peshawar",
        "language": "farsi/pashtu",
        "pages": "250"
      },
      "description": "Kommentiertes Verzeichnis von der afghanischen Widerstandsbewegung publizierter Periodika sowie monographischer Schriften."
    }
  ]
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Sequential entry identifier |
| `author` | string/null | Author name in romanized form |
| `author_arabic` | string/null | Author name in Arabic/Persian script |
| `title.arabic` | string | Title in original Arabic/Persian script |
| `title.transliterated` | string | Romanized transliteration of title |
| `title.german` | string | German translation of title |
| `publication_details.organization` | string/null | Publishing organization or movement |
| `publication_details.year_hijri` | int/null | Publication year (Islamic calendar) |
| `publication_details.year_gregorian` | int/null | Publication year (Gregorian calendar) |
| `publication_details.place` | string/null | Place of publication |
| `publication_details.language` | string/null | Language(s) of publication |
| `publication_details.pages` | string/null | Page count (may include annotations like "ca. 250" or "6 +") |
| `description` | string | Brief description of work (in German) |

## Scoring

This benchmark uses a **hybrid two-level scoring approach**:

### 1. Entry-Level Matching (F1 Score)
- Matches predicted entries to ground truth by `id`
- Calculates True Positives, False Positives, False Negatives
- Computes Precision, Recall, and F1 for entry detection

### 2. Field-Level Weighted Fuzzy Matching
For each correctly matched entry, individual fields are scored using fuzzy string matching with importance weights:

**High Importance (weight: 2.0)**
- `title.arabic`, `title.transliterated`, `title.german`
- `author`, `author_arabic`

**Medium Importance (weight: 1.0)**
- `publication_details.year_gregorian`, `publication_details.year_hijri`
- `publication_details.organization`, `publication_details.place`
- `description`, `id`

**Low Importance (weight: 0.5)**
- `publication_details.pages`, `publication_details.language`

### 3. Final Metrics
- **F1 Score:** How well the model finds the correct entries
- **Field Score:** How accurately the model extracts field content (weighted average)
- **Combined Score:** Harmonic mean of F1 and field score (primary ranking metric)

The weighted approach ensures that core bibliographic data (titles, authors) is valued more heavily than supplementary details (page counts, languages).

## Challenges

1. **Dense Layout:** Multiple entries per page with minimal spacing
2. **Script Mixing:** Arabic/Persian script embedded within Latin text
3. **Bidirectional Text:** Right-to-left Arabic mixed with left-to-right Latin
4. **Transliteration Variants:** Multiple valid romanization systems
5. **Historical Content:** Non-standard formatting and abbreviations (e.g., "o.O." for ohne Ort/no place)
6. **Calendar Conversion:** Parallel dating systems (Hijri/Gregorian)
7. **Complex Organizations:** Long Persian/Pashtu organizational names
8. **Incomplete Data:** Many entries have null values for certain fields

## Examples

### Input
A catalog page containing multiple bibliographic entries with:
- Arabic/Persian script titles
- Romanized transliterations
- German translations
- Publication metadata in mixed languages

### Expected Output
Structured JSON with complete extraction of all entries, maintaining:
- Accurate transcription of Arabic script
- Correct transliterations
- Proper association of metadata with each entry
- Preservation of both calendar dates
- Correct sequential id assignment

### Performance Expectations
- **Excellent (>0.85):** Captures most entries with high field accuracy
- **Good (0.70-0.85):** Finds most entries but has some transcription errors
- **Fair (0.50-0.70):** Misses entries or has significant field errors
- **Poor (<0.50):** Struggles with script recognition or entry boundaries

## Contributors

