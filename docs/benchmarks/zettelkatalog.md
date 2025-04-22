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
This benchmark evaluates the performance of large language models on [describe the specific task - e.g., "extracting bibliographic information from historical documents"]. The benchmark consists of [number] images containing [describe the content of the images, e.g., "19th century newspaper articles", "handwritten letters", etc.].

## Creator
This benchmark was created by [individual/organization name] ([contact information]) in [year]. [Include any additional information about the creators or contributors].

## Dataset Description

### Source
- **Collection**: [Name of collection or source]
- **Time Period**: [e.g., "1880-1920"]
- **Language**: [e.g., "German", "English", "Mixed"]
- **Format**: [e.g., "Typewritten", "Handwritten", "Printed", "Mixed"]
- **Link**: [If available, link to the original dataset]
- **License**: [License information for the dataset]

### Contents
The dataset contains [number] images of [describe what the images contain]. Each image [describe relevant characteristics, e.g., "contains a single page from a historical newspaper", "consists of multiple pages of correspondence", etc.].

## Ground Truth

### Ground Truth Creation
[Explain how the ground truth was created and which guidelines were used, e.g., "The ground truth was manually annotated by domain experts", "The ground truth was created using a semi-automated process and then verified by experts", etc.]

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
The models are tasked with [clearly describe what the models are expected to do, e.g., "extracting named entities", "categorizing text segments", "transcribing handwritten text", etc.]. Models should output [describe the expected output format, e.g., "a JSON structure with the following fields...", "a list of extracted entities categorized by type", etc.].

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
- [ ] create random sample of 1000 images from 1-680671, put into /images folder
- [ ] get completions for these images (run main script on T66)
- [ ] create ground truth for 1000 images based on completions
- [ ] put ground truth into /ground_truth folder
- [ ] conceptualize scoring, implement scoring method

## Test Results

