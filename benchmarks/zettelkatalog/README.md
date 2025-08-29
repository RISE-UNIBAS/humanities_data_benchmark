# [Benchmark Name]

## Table of Contents
- [Overview](#overview)
- [Creator](#creator)
- [Dataset Description](#dataset-description)
- [Task Description](#task-description)
- [Ground Truth](#ground-truth)
- [Evaluation Criteria](#evaluation-criteria)
- [Results](#results)
- [Observations](#observations)
- [Limitations and Future Work](#limitations-and-future-work)

## Overview
This benchmark evaluates the performance of large language models on extracting bibliograhic information from index cards. The benchmark consists of 1000 images containing descriptions of historical dissertations (before 1980, some well before 1900). The set contains both typeset and handwritten cards, and the format and exact content of the descriptions varies. 

## Creator
This benchmark was created by Gabriel Müller (https://github.com/gbmllr1) at Basel University Library in 2025. [Include any additional information about the creators or contributors].

## Dataset Description

### Source
- **Collection**: [Name of collection or source]
- **Time Period**: -1980
- **Language**: German, Latin
- **Format**: Mixed
- **Link**: https://ub.unibas.ch/cmsdata/spezialkataloge/ipac/searchform.php?KatalogID=ak2
- **License**: [License information for the dataset]

### Contents
The dataset contains 1000 images of index cards describing historical dissertations. Each image corresponds to one card and one dissertation. It is a random sample out of the ~600'000 dissertations collected by Basel University Library in the time period before 1980. The original works come predominantly from Switzerland and neighboring countries, but some may come from anywhere in the world.
Strictly speaking, a typical card may describe multiple things and events related to a given dissertation/PhD thesis (an abstract work): 1) The author (a person), 2) the published version of record required for the diploma (a publication), 3) the thesis defense (an event), 4) other published versions of the thesis (a publication, e.g. an extract in the form of a journal article). Not all of these elements are present in every case, and they are often not explicitly separated on the card.
Furthermore, some of the cards do not contain a full description of a thesis, but are merely references to another card in the catalogue. In these cases, the card begins with the name of the referenced author, followed by an "s." on a separate line (German "siehe"). There may or may not be other information below that.

## Ground Truth

### Ground Truth Creation
The ground truth was was created by manual correction of responses by chat-gpt-4o, using the ground-truther.py tool contained in the folder of this benchmark. In addition to correct readings of the text, the following rules were enforced (cf. also the instructions given in prompt.txt):
- A card containing the note "s." on a separate line should be classified as a reference.
- Page numbers should be given without "p." or "S.", but if there is information on additional unnumbered pages, that info should be kept (i.e. "IV S. + 67-74 S." --> "IV. 67-74")
- A work in octavo format may be listed as "8°" or as "8'". The result should render the exact value as it is on the card.
- The place and year of examination should only be filled out if they are explicitly mentioned on the card (not deduced from the date of publication). A shelfmark with a time and place counts as such a mention (e.g. "Diss. Basel, 1967"). 

### Ground Truth Format
The ground truth is stored in [format, e.g., "JSON files", "CSV files", etc.] with the following structure:

```json
{
  "field1": "ground truth value",
  "field2": ["ground truth value 1", "ground truth value 2"],
  "field3": {
    "subfield1": "ground truth value",
    "subfield2": "ground truth value"
  }
}
```
## Scoring

### Evaluation Criteria
The models are tasked with extracting the bibliographic information on each index card. Models should output a json structure with the fields defined in dataclass.py. The top-level fields describe separate aspects of the cards. "type" designates whether the card in question contains a full description of a dissertation/thesis or merely a reference to another record. "author" contains the first and last name(s) of the author of the thesis.   

```json
{
  "field1": "value",
  "field2": ["value1", "value2"],
  "field3": {
    "subfield1": "value",
    "subfield2": "value"
  }
}
```

### Scoring Methodology
[Explain how the scoring is done, e.g., "The extracted data is compared to the ground truth using fuzzy string matching", "The model's output is evaluated based on precision, recall, and F1 score", etc.]

### Example Scoring
[Include an example scoring]

## Observations

[Include any notable observations about model performance, patterns, or insights gained from the benchmark results]

## Limitations and Future Work

- [Describe any limitations of the current benchmark]
- [Suggest potential improvements or extensions for future versions]
- [Mention any work in progress related to this benchmark]

## To Dos
- [ ] specify metadata schema
- [x] create random sample of 1000 images from 1-680671, put into /images folder
- [ ] get completions for these images (run main script on T66)
- [ ] create ground truth for 1000 images based on completions
- [ ] put ground truth into /ground_truth folder
- [ ] conceptualize scoring, implement scoring method