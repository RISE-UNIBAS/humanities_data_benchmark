# Metadata Extraction from Historic Rheinschifffahrt Letters

## Table of Contents
- [Overview](#overview)
- [Creator](#creator)
- [Historic Rheinschifffahrt Letters](#historic-rheinschifffahrt-letters)
- [Ground Truth](#ground-truth)
  - [Guidelines for creating the ground truth](#guidelines-for-creating-the-ground-truth)
  - [Metadata schema](#metadata-schema)
  - [Importing the ground truth from Google Sheets](#importing-the-ground-truth-from-google-sheets)
- [Scoring](#scoring)
  - [Scoring a letter](#scoring-a-letter)
  - [Scoring the collection](#scoring-the-collection)
- [To Dos](#to-dos)

## Overview

This benchmark focuses on the extraction of metadata from historic letters. It provides a ground truth for the metadata categories `send_date`, `sender_persons` and `receiver_persons` for a collection of letters from the Basler Rheinschifffahrt-Aktiengesellschaft between 1926 and 1932, and F1-micro and F1-macro scores across these categories.

## Creator

This benchmark was created by the University of Basel's Research and Infrastructure Support RISE (rise@unibas.ch) between 2022 and 2025.

| Role | Contributors |
|------|-------------|
| Domain expert | [Eric Decker], [Maximilian Hindermann], [Lea Kasper] |
| Data curator | [Anthea Alberto], [Eric Decker], [Maximilian Hindermann] |
| Annotator | [Anthea Alberto], [Eric Decker], [Pema Frick], [Maximilian Hindermann], [Lea Kasper], [José Luis Losada Palenzuela], [Sorin Marti], [Elena Spadini] |
| Analyst | [Maximilian Hindermann] |
| Engineer | [Maximilian Hindermann] |

For detailed contributor information and role descriptions, see [CONTRIBUTORS.md](https://github.com/RISE-UNIBAS/humanities_data_benchmark/blob/main/CONTRIBUTORS.md).

## Historic Rheinschifffahrt Letters

This benchmark uses as input the digital collection "Basler Rheinschifffahrt-Aktiengesellschaft, insbesondere über die Veräusserung des Dieselmotorbootes 'Rheinfelden' und die Gewährung eines Darlehens zur Finanzierung der Erstellung des Dieselmotorbootes 'Rhyblitz' an diese Firma" (shelf mark: `CH SWA HS 191 V 10`, persistent link: http://dx.doi.org/10.7891/e-manuscripta-54917, referred to as "the collection" in what follows) of the Schweizer Wirtschaftsarchiv. 

The collection consists of 68 letters of various length (mostly 1-3 pages). The letters are dated between 1926 and 1932 and are written in German. The letters are mostly typewritten, with some handwritten annotations. The letters reflect the correspondence of the Basler Rheinschifffahrt-Aktiengesellschaft and are mostly signed by individuals or companies. The letters cover a variety of topics, including business transactions, shipping schedules, and personnel matters. In this benchmark, a subset of 57 letters have been ground truthed (see below). 

## Ground Truth

The ground truth for the collection is created in the [RSF Letters Ground Truth Google Sheet](https://docs.google.com/spreadsheets/d/1qGMVvGZV7GpU11uy0grIffDbGS2rSOj85ziFWZGyuBI/edit?usp=sharing). It is then imported and used to benchmark LLMs with respect to information extraction tasks.

### Guidelines for creating the ground truth

The ground truth for letters is created by filling out the `ground_truth` tab of the Google Sheet.

#### Metadata schema

The `ground_truth` tab of the Google Sheet uses the following metadata schema:

| **Field Name**                 | **Description**                                                                                                                  | **Data Type**           |
|--------------------------------|----------------------------------------------------------------------------------------------------------------------------------|-------------------------|
| **transkribus_doc_url**        | URL link to the letter on Transkribus.                                                                                           | `string (URL)`          |
| **document_number**            | The letter's number is between 1 and 68, inclusive (1 ≤ i ≤ 68).                                                                 | `zero padded integer`   |
| **done**                       | Indicates whether the creation of the ground truth is completed.                                                                 | `boolean`               |
| **checked_by**                 | Identifier of the person who is responsible for creating the ground truth.                                                       | `string`                |
| **send_date**                  | Date when the letter was sent.                                                                                                   | `ISO 8601 date or None` |
| **letter_title**               | Title of the letter as diplomatically inscribed.                                                                                 | `string or None`        |
| **sender_persons_inscribed**   | Sender person(s) as diplomatically inscribed.                                                                                    | `string or None`        |
| **sender_persons**             | Individuals explicitly mentioned as senders in the document.	                                                                    | `string or None`        |
| **receiver_persons_inscribed** | Receiver person(s) as diplomatically inscribed.                                                                                  | `string or None`        |
| **receiver_persons**           | Individuals associated with receiving the document, inferred or explicitly stated.                                               | `string`                |
| **has_signatures**             | Indicates whether the document contains signatures.                                                                              | `boolean`               |
| **signatures_recognised**      | Indicates whether all signatures have been mapped to persons as per [`ground_truth/persons.json`](../ground_truth/persons.json). | `boolean`               |
| **comment**                    | Additional comments or annotations about the document.                                                                           | `string or None`        |
| **action_required**            | Indicates what action is required to get to document done.                                                                       | `string`                |

#### Persons

Persons are recorded in the `persons` tab of the Google Sheet. The metadata schema and workflow for persons is described in [`ground_truth_persons_organizations.md`](ground_truth_persons_organizations).

For `sender_persons_inscribed`, `sender_persons` `receiver_persons_inscribed`, `receiver_persons`:

- Pipe `|` is used to separate multiple values: `Mustermann, Hans | Musterfrau, Maria`.
- Indicate persons inferred from function & date with angle brackets: `<Mustermann, Hans>`
- Indicate persons inferred from the correspondence history with double angle brackets: `<<Musterfrau, Maria>>`

The `sender_persons` and `receiver_persons` fields use the names of persons as recorded in the normalized `persons` tab. Be sure to add inscribed variants to their respective `alternateName` fields.

#### Importing the ground truth from Google Sheets
							
Letters that are done are exported from the `ground_truth_export` tab of the Google Sheet as a CSV file and saved to [`ground_truth/letters.csv`](../ground_truth/letters.csv).

## Scoring

We score the metadata extraction of letters from the ground truth using the predictions of LLMs. Intuitively, we want to tell if the extracted metadata is correct and complete.

### Scoring a letter

We score each letter for the metadata categories `send_date`, `sender_persons` and `receiver_persons` by checking true positives (TP), false positives (FP), and false negatives (FN) against the ground truth. 

#### Example

Consider the first letter as an example. The letter is composed of three pages:

<table>
  <tr>
    <td>
      <a href="https://raw.githubusercontent.com/RISE-UNIBAS/humanities_data_benchmark/main/benchmarks/metadata_extraction/images/letter01_p1.jpg">
        <img src="https://raw.githubusercontent.com/RISE-UNIBAS/humanities_data_benchmark/main/benchmarks/metadata_extraction/images/letter01_p1.jpg" alt="Letter page 1" width="200">
      </a>
    </td>
    <td>
      <a href="https://raw.githubusercontent.com/RISE-UNIBAS/humanities_data_benchmark/main/benchmarks/metadata_extraction/images/letter01_p2.jpg">
        <img src="https://raw.githubusercontent.com/RISE-UNIBAS/humanities_data_benchmark/main/benchmarks/metadata_extraction/images/letter01_p2.jpg" alt="Letter page 2" width="200">
      </a>
    </td>
    <td>
      <a href="https://raw.githubusercontent.com/RISE-UNIBAS/humanities_data_benchmark/main/benchmarks/metadata_extraction/images/letter01_p3.jpg">
        <img src="https://raw.githubusercontent.com/RISE-UNIBAS/humanities_data_benchmark/main/benchmarks/metadata_extraction/images/letter01_p3.jpg" alt="Letter page 3" width="200">
      </a>
    </td>
  </tr>
</table>

The scoring of the letter is as follows:

| Metric             | Ground Truth                                    | Prediction                                    | TP | FP | FN |
|--------------------|-------------------------------------------------|-----------------------------------------------|----|----|----|
| `send_date`        | 1926-02-16                                      | 1926-02-16                                    | 1  | 0  | 0  |
| `sender_persons`   | Groschupf-Jaeger, Louis<br>Ritter-Dreier, Fritz | Basler Rheinschiffahrt-Aktiengesellschaft     | 0  | 1  | 2  |
| `receiver_persons` | Christ-Wackernagel, Paul                        | Herr Christ<br>i/Fa. Paravicini, Christ & Co. | 1  | 1  | 0  |

- `send_date`: The prediction matches the ground truth (1 TP).
- `sender_persons`: The prediction is incorrect (1 FP) as "Basler Rheinschiffahrt-Aktiengesellschaft" is not a sender person, and the two actual sender persons "(Groschupf-Jaeger, Louis" and "Ritter-Dreier, Fritz") are missing (2 FN).
- `receiver_persons`: The prediction is partly correct as "Herr Christ" is mentioned as a receiver person (1 TP), and the prediction is partly incorrect as "i/Fa. Paravicini, Christ & Co." is not a receiver person (1 FP).

### Scoring the collection

With scores for each letter in place, we can calculate the overall performance of an LLM on the collection. We calculate F1-micro and F1-macro:

- F1 is the harmonic mean of precision and recall, where precision is TP / (TP + FP) and recall is TP / (TP + FN).
- F1-micro is the harmonic mean of precision and recall across all categories.
- F1-macro is the average of F1 scores across all categories.

### Rule parameters
- `inferred_from_function`: If true, the person is inferred from their function and the date (e.g., a letter from the Basler Personenschifffahrtsgesellschaft in 1925 signed by "der Präsident" was penned by Max Vischer-von Planta ).
- `inferred_from_correspondence`: If true, the person is inferred from the correspondence history (e.g., "referring to your letter from last week").
- `skip_signatures`: If true, then letters with signatures are not scored.
- `skip_non_signatures`: If true, then letters without signatures are not scored.

## To Dos

- [ ] Add more fields to the metadata schema, namely `sender_organization` (inscribed and normalized), `receiver_organization` (inscribed and normalized),  fields for entities mentioned (persons, places, organizations, ships; inscribed and normalized).		

[Anthea Alberto]: https://orcid.org/0009-0007-0430-0050
[Sven Burkhardt]: https://orcid.org/0009-0001-4954-4426
[Eric Decker]: https://orcid.org/0000-0003-3035-2413
[Pema Frick]: https://orcid.org/0000-0002-8733-7161
[Maximilian Hindermann]: https://orcid.org/0000-0002-9337-4655
[Lea Kasper]: https://orcid.org/0000-0002-4671-1700
[José Luis Losada Palenzuela]: https://orcid.org/0000-0002-6530-1328
[Gabriel Müller]: https://orcid.org/0000-0001-8320-5148
[Sorin Marti]: https://orcid.org/0000-0002-9541-1202
[Ina Serif]: https://orcid.org/0000-0003-2419-4252
[Elena Spadini]: https://orcid.org/0000-0002-4522-2833