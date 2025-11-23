# Ground truth for persons and organizations

## Overview

The ground truth for persons and organizations is created in the [RSF Letters Ground Truth Google Sheet](https://docs.google.com/spreadsheets/d/1qGMVvGZV7GpU11uy0grIffDbGS2rSOj85ziFWZGyuBI/edit?usp=sharing). It is then imported and used to benchmark LLMs with respect to information extraction tasks.

## Persons

The ground truth for persons is created by filling out the `persons` tab of the Google Sheet.

### Fields

The metadata schema for persons is based on the [Schema.org](https://schema.org/Person) `Person` type. It uses three categories of information: person information, job history, and sources.

#### Person Information

This category includes general information about the person.

| **Field**           | **Schema.org Property** | **Description**                                                                    |
|---------------------|-------------------------|------------------------------------------------------------------------------------|
| **Identifier**      | `identifier`            | Links to the person’s unique identifier (e.g., GND ID, Wikidata, ORCID).           |
| **Name**            | `name`                  | The primary name of the person.                                                    |
| **Alternate Names** | `alternateName`         | Other names, pseudonyms, or aliases used by the person.                            |
| **Birth Date**      | `birthDate`             | The person’s date of birth in ISO 8601 format (YYYY-MM-DD).                        |
| **Death Date**      | `deathDate`             | The person’s date of death in ISO 8601 format (YYYY-MM-DD).                        |
| **Notes**           | `description`           | Free-text field for additional biographical information or notes about the person. |

#### Job History

This category includes information about the person’s roles and occupations.

| **Field**          | **Schema.org Property**             | **Description**                                                 |
|--------------------|-------------------------------------|-----------------------------------------------------------------|
| **Occupation**     | `hasOccupation`                     | Represents a job or role the person held.                       |
| **Role/Job Title** | `name` (inside `hasOccupation`)     | The name of the role or job title.                              |
| **Start Date**     | `startDate`                         | The date the role began, in ISO 8601 format.                    |
| **End Date**       | `endDate`                           | The date the role ended, in ISO 8601 format.                    |
| **Employer**       | `employer`                          | The organization associated with the job.                       |
| **Employer ID**    | `identifier` (inside `employer`)    | Unique identifier for the employer (e.g., GND ID, Wikidata ID). |
| **Location**       | `location`                          | The geographic location where the job was performed.            |
| **Job Sources**    | `citation` (inside `hasOccupation`) | References or sources verifying the job information.            |

#### Sources

This category includes references or sources for the person’s information.

| **Field**                | **Schema.org Property**             | **Description**                                                                             |
|--------------------------|-------------------------------------|---------------------------------------------------------------------------------------------|
| **Overall Sources**      | `citation`                          | References or sources for the overall person description (e.g., books, articles, websites). |
| **Job-Specific Sources** | `citation` (inside `hasOccupation`) | Sources verifying specific roles or job information.                                        |

### Example JSON

```
{
  "@context": "http://schema.org",
  "@type": "Person",
  "identifier": [
    {
      "@type": "PropertyValue",
      "propertyID": "GND",
      "value": "118529579"
    }
  ],
  "name": "Marie Curie",
  "alternateName": ["Maria Skłodowska"],
  "birthDate": "1867-11-07",
  "deathDate": "1934-07-04",
  "description": "Marie Curie was a physicist and chemist.",
  "citation": [
    {
      "@type": "CreativeWork",
      "name": "Marie Curie: A Life",
      "author": "Susan Quinn",
      "datePublished": "1995",
      "publisher": "Simon & Schuster"
    },
    {
      "@type": "CreativeWork",
      "name": "Wikipedia Entry for Marie Curie",
      "url": "https://en.wikipedia.org/wiki/Marie_Curie"
    }
  ],
  "hasOccupation": [
    {
      "@type": "Occupation",
      "name": "Physicist",
      "startDate": "1903",
      "endDate": "1934",
      "employer": {
        "@type": "Organization",
        "name": "University of Paris",
        "identifier": [
          {
            "@type": "PropertyValue",
            "propertyID": "GND",
            "value": "20212345-7"
          },
          {
            "@type": "PropertyValue",
            "propertyID": "Wikidata",
            "value": "Q123456"
          }
        ]
      },
      "location": {
        "@type": "Place",
        "name": "Paris, France"
      },
      "citation": {
        "@type": "CreativeWork",
        "name": "University of Paris Historical Records",
        "url": "https://university-paris-history.org"
      }
    },
    {
      "@type": "Occupation",
      "name": "Director",
      "startDate": "1914",
      "endDate": "1934",
      "employer": {
        "@type": "Organization",
        "name": "Radium Institute",
        "identifier": [
          {
            "@type": "PropertyValue",
            "propertyID": "GND",
            "value": "20267890-3"
          }
        ]
      },
      "location": {
        "@type": "Place",
        "name": "Paris, France"
      },
      "citation": {
        "@type": "CreativeWork",
        "name": "Radium Institute Archive",
        "url": "https://radium-institute-archive.org"
      }
    }
  ]
}
```

### Workflow

1. Fill in information in `person` tab in [RSF Letters Ground Truth Google Sheet](https://docs.google.com/spreadsheets/d/1qGMVvGZV7GpU11uy0grIffDbGS2rSOj85ziFWZGyuBI/edit?usp=sharing).
2. Export the `person` tab as a CSV file to `data/persons.csv`.
3. Run `BenchmarkClient.update_persons` on `data/persons.csv` to create `person/persons.json`.

## Organizations

The ground truth for organizations is created by filling out the `organizations` tab of the Google Sheet.

### Fields

The metadata schema for organizations is based on the [Schema.org](https://schema.org/Organization) `Organization` type. It includes information about the organization and its address history.

#### Employer Information

This category includes general information about the organization.

| **Field**           | **Schema.org Property** | **Description**                                                                                     |
|---------------------|-------------------------|-----------------------------------------------------------------------------------------------------|
| **Organization ID** | `identifier`            | Unique identifier for the organization (e.g., GND ID, Wikidata ID, custom ID).                      |
| **Name**            | `name`                  | The primary name of the organization.                                                               |
| **Alternate Names** | `alternateName`         | Other names, abbreviations, or aliases used for the organization.                                   |
| **Notes**           | `description`           | Free-text field for additional information or notes about the organization.                         |
| **Sources**         | `citation`              | References or sources for the organization's information (e.g., URLs, books, structured citations). |


#### Address History

This category includes information about the organization's address history.

| **Field**          | **Schema.org Property** | **Description**                                                        |
|--------------------|-------------------------|------------------------------------------------------------------------|
| **Street Address** | `streetAddress`         | The street address where the organization was located.                 |
| **Locality**       | `addressLocality`       | The city or locality of the address.                                   |
| **Country**        | `addressCountry`        | The country where the address is located.                              |
| **Postal Code**    | `postalCode`            | The postal code of the address.                                        |
| **Start Date**     | `startDate`             | The date the organization started using the address (ISO 8601 format). |
| **End Date**       | `endDate`               | The date the organization stopped using the address (ISO 8601 format). |


### Example JSON

```
{
  "@context": "http://schema.org",
  "@type": "Organization",
  "identifier": [
    {
      "@type": "PropertyValue",
      "propertyID": "GND",
      "value": "20212345-7"
    },
    {
      "@type": "PropertyValue",
      "propertyID": "Wikidata",
      "value": "Q123456"
    }
  ],
  "name": "University of Paris",
  "alternateName": ["Université de Paris", "Sorbonne"],
  "description": "The University of Paris, often referred to as the Sorbonne, is one of the oldest universities in the world, established in 1150.",
  "citation": [
    {
      "@type": "CreativeWork",
      "name": "Historical Records of the University of Paris",
      "url": "https://university-paris-history.org"
    },
    {
      "@type": "CreativeWork",
      "name": "Wikipedia Entry for University of Paris",
      "url": "https://en.wikipedia.org/wiki/University_of_Paris"
    }
  ],
  "address": [
    {
      "@type": "PostalAddress",
      "streetAddress": "47 rue des Écoles",
      "addressLocality": "Paris",
      "addressCountry": "France",
      "postalCode": "75005",
      "startDate": "1150-01-01",
      "endDate": "1896-12-31"
    },
    {
      "@type": "PostalAddress",
      "streetAddress": "1 rue Victor Cousin",
      "addressLocality": "Paris",
      "addressCountry": "France",
      "postalCode": "75005",
      "startDate": "1897-01-01",
      "endDate": "2020-12-31"
    }
  ]
}

```

### Workflow

Not yet implemented.

## To Dos

- [ ] Implement workflow for organizations.