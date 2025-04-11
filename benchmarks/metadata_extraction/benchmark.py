from __future__ import annotations
import pandas as pd
import csv
import json
import os
import logging
from typing import Literal, Optional

from scripts.benchmark_base import Benchmark
from benchmarks.metadata_extraction.category import Category
from benchmarks.metadata_extraction.letter import Letter
from benchmarks.metadata_extraction.person import Person


class MetadataExtraction(Benchmark):

    def score_benchmark(self,
                        all_scores: list[dict]) -> dict:
        """ Score the benchmark.

        :param all_scores: a list of scores
        """

        send_date = Category(used=True)
        sender_persons = Category(used=True)
        receiver_persons = Category(used=True)

        for score in all_scores:
            try:
                send_date.tp += score["send_date_tp"]
                send_date.fp += score["send_date_fp"]
                send_date.fn += score["send_date_fn"]

                sender_persons.tp += score["sender_persons_tp"]
                sender_persons.fp += score["sender_persons_fp"]
                sender_persons.fn += score["sender_persons_fn"]

                receiver_persons.tp += score["receiver_persons_tp"]
                receiver_persons.fp += score["receiver_persons_fp"]
                receiver_persons.fn += score["receiver_persons_fn"]
            except (KeyError, TypeError):
                continue

        categories = [send_date, sender_persons, receiver_persons]
        f1_macro = self._get_f1_macro(categories)
        f1_micro = self._get_f1_micro(categories)
        logging.info(f"f1_macro: {f1_macro}, f1_micro: {f1_micro}")
        return {"f1_macro": f1_macro,
                "f1_micro": f1_micro}

    def score_request_answer(self,
                             image_name: str,
                             response: dict,
                             ground_truth: dict,
                             inferred_from_function=False,
                             inferred_from_correspondence=False) -> Optional[dict]:
        """ Score the answer.

        :param image_name: the name of the image
        :param response: the response
        :param ground_truth: the ground truth
        :param inferred_from_function: whether to filter by persons inferred from function, defaults to False
        :param inferred_from_correspondence: whether to filter by persons inferred from correspondence, defaults to False
        """

        data = self.prepare_scoring_data(response)

        try:
            response_letter = self._initialize_letter(raw_letter=data["metadata"],
                                                      image_name=image_name)
        except KeyError:
            if "error" in data:
                return None
            response_letter = self._initialize_letter(raw_letter=data,
                                                      image_name=image_name)
        ground_truth_letter = self._initialize_letter(raw_letter=ground_truth,
                                                      image_name=image_name)

        score = self._score_send_date(ground_truth_letter=ground_truth_letter,
                                      predicted_letter=response_letter)

        try:
            persons = json.load(open(os.path.join(self.benchmark_dir, "ground_truths", "persons.json")))
        except FileNotFoundError as e:
            logging.error(f"{e}: Persons ground truth not found!")

        score = score | self._score_persons(sender_or_receiver="sender",
                                            ground_truth_letter=ground_truth_letter,
                                            predicted_letter=response_letter,
                                            persons=persons,
                                            inferred_from_function=inferred_from_function,
                                            inferred_from_correspondence=inferred_from_correspondence)

        score = score | self._score_persons(sender_or_receiver="receiver",
                                            ground_truth_letter=ground_truth_letter,
                                            predicted_letter=response_letter,
                                            persons=persons,
                                            inferred_from_function=inferred_from_function,
                                            inferred_from_correspondence=inferred_from_correspondence)
        return score

    def create_request_render(self,
                              image_name: str,
                              result: dict,
                              score: dict,
                              ground_truth: dict,
                              inferred_from_function=False,
                              inferred_from_correspondence=False) -> str:
        """ Create a render for the request.

        :param image_name: the name of the image
        :param result: the result
        :param score: the score
        :param ground_truth: the ground truth
        :param inferred_from_function: whether to filter by persons inferred from function, defaults to False
        :param inferred_from_correspondence: whether to filter by persons inferred from correspondence, defaults to False
        """

        data = self.prepare_scoring_data(result)

        try:
            response_letter = self._initialize_letter(raw_letter=data["metadata"],
                                                      image_name=image_name)
        except KeyError:
            response_letter = self._initialize_letter(raw_letter=data,
                                                      image_name=image_name)
        ground_truth_letter = self._initialize_letter(raw_letter=ground_truth,
                                                      image_name=image_name)

        ground_truth_sender_persons = self._select_persons(sender_or_receiver="sender",
                                                           ground_truth_letter=ground_truth_letter,
                                                           inferred_from_function=inferred_from_function,
                                                           inferred_from_correspondence=inferred_from_correspondence)
        ground_truth_receiver_persons = self._select_persons(sender_or_receiver="receiver",
                                                             ground_truth_letter=ground_truth_letter,
                                                             inferred_from_function=inferred_from_function,
                                                             inferred_from_correspondence=inferred_from_correspondence)

        ground_truth_persons = ground_truth_sender_persons + ground_truth_receiver_persons
        ground_truth_persons = [person for person in ground_truth_persons if person.name != "None"]

        try:
            persons = json.load(open(os.path.join(self.benchmark_dir, "ground_truths", "persons.json")))
            for person in ground_truth_persons:
                for key in persons:
                    if person.name == key["name"]:
                        person.alternate_names = key["alternateName"]
                        break
        except FileNotFoundError:
            logging.error("Persons ground truth not found.")

        if "error" in data:
            render = (
                f"### Result for {ground_truth_letter.document_number}\n"
                f"Model did not produce a valid response!\n"
            )
            return render

        scoring_table = "| Category          | Ground Truth | Prediction | TP | FP | FN |\n"
        scoring_table += "|------------------|--------------|------------|----|----|----|\n"
        scoring_table += f"| `send_date`        | {ground_truth_letter.send_date} | {response_letter.send_date} | {score['send_date_tp']} | {score['send_date_fp']} | {score['send_date_fn']} |\n"
        scoring_table += f"| `sender_persons`  | {self._make_render_person(persons=ground_truth_sender_persons)} | {self._make_render_person(persons=response_letter.sender_persons)} | {score['sender_persons_tp']} | {score['sender_persons_fp']} | {score['sender_persons_fn']} |\n"
        scoring_table += f"| `receiver_persons` | {self._make_render_person(persons=ground_truth_receiver_persons)} | {self._make_render_person(persons=response_letter.receiver_persons)} | {score['receiver_persons_tp']} | {score['receiver_persons_fp']} | {score['receiver_persons_fn']} |\n"

        persons_table = "| Name | Alternate Names |\n"
        persons_table += "| --- | --- |\n"

        for person in ground_truth_persons:
            try:
                person.alternate_names.sort()
                alt_names = "<br>".join(person.alternate_names)
            except (TypeError, AttributeError):
                alt_names = "None"
            persons_table += f"| {person.name} | {alt_names} |\n"

        render = (
            f"### Result for {response_letter.document_number}\n"
            f"{scoring_table}\n"
            f"{persons_table}\n"
            f"#### Rules\n"
            f"`inferred_from_function`: {inferred_from_function}\n\n"
            f"`inferred_from_correspondence`: {inferred_from_correspondence}\n\n"
        )

        if self.rules is not None:
            for key, value in self.rules.items():
                render += f"`{key}`: {value}\n\n"

        # todo: display all images in the render

        return render

    def skip_image(self,
                   image_name: str) -> bool:
        """ Skip the image if the rules say so."""

        try:
            if self.rules["skip_signatures"] is True:
                ground_truth = self.load_ground_truth(image_name)
                ground_truth_letter = self._initialize_letter(raw_letter=ground_truth,
                                                              image_name=image_name)
                if ground_truth_letter.has_signatures is True:
                    return True
            elif self.rules["skip_non_signatures"] is True:
                ground_truth = self.load_ground_truth(image_name)
                ground_truth_letter = self._initialize_letter(raw_letter=ground_truth,
                                                              image_name=image_name)
                if ground_truth_letter.has_signatures is False:
                    return True

        except TypeError:
            return False

    def update_ground_truth(self) -> None:
        """ Update the ground truth. """

        ground_truth_path = os.path.join(self.benchmark_dir, "ground_truths")
        try:
            self._update_persons(persons_csv=f"{ground_truth_path}/persons.csv",
                                 persons_json=f"{ground_truth_path}/persons.json")
        except FileNotFoundError:
            logging.error(
                f"Ground truth not found: {ground_truth_path}/persons.csv")
        try:
            self._update_letters(letters_csv=f"{ground_truth_path}/letters.csv",
                                 letters_json_dir=ground_truth_path)
        except FileNotFoundError:
            logging.error(
                f"Ground truth not found: {ground_truth_path}/letters.csv")

    def update_required(self) -> bool:
        """ If an update of the ground truth is required before running the benchmark. """

        return True

    @staticmethod
    def _get_f1_macro(categories: list[Category]) -> float:
        """ Get the macro average F1 score.

        :param categories: a list of categories
        """

        return sum([category.get_f1() for category in categories]) / len(categories)

    @staticmethod
    def _get_f1_micro(categories: list[Category]) -> float:
        """ Get the micro average F1 score.

        :param categories: a list of categories
        """

        sum_tp = sum([category.tp for category in categories])
        sum_fp = sum([category.fp for category in categories])
        sum_fn = sum([category.fn for category in categories])

        try:
            micro_precision = sum_tp / (sum_tp + sum_fp)
            micro_recall = sum_tp / (sum_tp + sum_fn)
            return 2 * (micro_precision * micro_recall) / (micro_precision + micro_recall)
        except ZeroDivisionError:
            return float(0)

    @staticmethod
    def _initialize_letter(raw_letter: dict,
                           image_name: str) -> Letter:
        """ Initialize a Letter object from a dictionary.

        :param raw_letter: the raw letter data
        :param image_name: the name of the image
        """

        try:
            raw_letter["document_number"] = image_name
            return Letter(**raw_letter)
        except (ValueError, TypeError) as e:
            logging.error(f"{e} parsing {raw_letter} for {image_name}!")

    @staticmethod
    def _make_render_person(persons: list[Person]) -> str | None:
        """ Render a list of persons as a string.

        :param persons: the list of persons
        """

        rendered_persons = []
        try:
            for person in persons:
                if person.name == "None" or person.name == "null":
                    return None
                rendered_persons.append(person.name)
            if len(rendered_persons) == 0:
                return None
            return "<br>".join(rendered_persons)
        except TypeError:
            return None

    @staticmethod
    def _match_person(persons: dict,
                      ground_truth_person: Person,
                      predicted_person: str) -> str | None:
        """ Match predicted person to ground truth person name variant. """

        for person in persons:
            if ground_truth_person.name == person["name"]:
                if predicted_person in person["alternateName"]:
                    return ground_truth_person.name

        return None

    @staticmethod
    def _score_send_date(ground_truth_letter: Letter,
                         predicted_letter: Letter) -> dict[str, int]:
        """ Score 'send_date'.

        :param ground_truth_letter: the ground truth letter
        :param predicted_letter: the predicted letter
        """

        predicted_date = predicted_letter.send_date
        ground_truth_date = ground_truth_letter.send_date

        # remove name artifacts and duplicates:
        ground_truth_date = {ground_truth_date}
        predicted_date = {predicted_date}
        try:
            predicted_date.remove("null")
        except KeyError:
            pass
        try:
            predicted_date.remove(None)
        except KeyError:
            pass

        logging.debug(f"ground_truth_date: {ground_truth_date}")
        logging.debug(f"predicted_date: {predicted_date}")

        return {"send_date_tp": len(ground_truth_date & predicted_date),
                "send_date_fp": len(predicted_date - ground_truth_date),
                "send_date_fn": len(ground_truth_date - predicted_date)}

    def _score_persons(self,
                       sender_or_receiver: Literal["sender", "receiver"],
                       ground_truth_letter: Letter,
                       predicted_letter: Letter,
                       persons: dict,
                       inferred_from_function: bool = False,
                       inferred_from_correspondence: bool = False) -> dict[str, int]:
        """ Score 'sender_persons' or 'receiver_persons'.

        :param sender_or_receiver: whether to score by sender or receiver persons
        :param ground_truth_letter: the ground truth letter
        :param predicted_letter: the predicted letter
        :param persons: the persons ground_truth
        :param inferred_from_function: whether sender person was inferred from function, defaults to False
        :param inferred_from_correspondence: whether sender person was inferred from correspondence, defaults to False
        """

        # select ground truth persons:
        ground_truth_persons = self._select_persons(sender_or_receiver=sender_or_receiver,
                                                    ground_truth_letter=ground_truth_letter,
                                                    inferred_from_function=inferred_from_function,
                                                    inferred_from_correspondence=inferred_from_correspondence)

        # select predicted persons:
        predicted_persons = []
        if predicted_letter.__getattribute__(f"{sender_or_receiver}_persons") is not None:
            predicted_persons = predicted_letter.__getattribute__(f"{sender_or_receiver}_persons")
        predicted_persons = [predicted_person.name for predicted_person in predicted_persons]

        # match predicted persons to their preferred name variant:
        matched_predicted_persons = []
        for predicted_person in predicted_persons:
            matched = False
            for ground_truth_person in ground_truth_persons:
                if ground_truth_person.name == predicted_person:
                    matched_predicted_persons.append(predicted_person)
                    matched = True
                    break
                else:
                    match = self._match_person(persons=persons,
                                               ground_truth_person=ground_truth_person,
                                               predicted_person=predicted_person)
                    if match is not None:
                        matched_predicted_persons.append(match)
                        matched = True
                        break
            if not matched:
                matched_predicted_persons.append(predicted_person)

        # normalize persons:
        ground_truth_persons = set([person.name for person in ground_truth_persons if person.name != "None"])
        predicted_persons = set()
        for predicted_person in matched_predicted_persons:
            if predicted_person == "null":
                continue
            elif predicted_person is None:
                continue
            else:
                predicted_persons.add(predicted_person)

        return {f"{sender_or_receiver}_persons_tp": len(ground_truth_persons & predicted_persons),
                f"{sender_or_receiver}_persons_fp": len(predicted_persons - ground_truth_persons),
                f"{sender_or_receiver}_persons_fn": len(ground_truth_persons - predicted_persons)}

    @staticmethod
    def _select_persons(sender_or_receiver: Literal["sender", "receiver"],
                        ground_truth_letter: Letter,
                        inferred_from_function: bool = False,
                        inferred_from_correspondence: bool = False
                        ):
        """ Select 'sender_persons' or 'receiver_persons' from the ground truth and filter by inference method.

        :param sender_or_receiver: whether to select sender or receiver persons
        :param ground_truth_letter: the ground truth letter
        :param inferred_from_function: whether to filter by persons inferred from function, defaults to False
        :param inferred_from_correspondence: whether to filter by persons inferred from correspondence, defaults to False
        """

        ground_truth_persons = []
        for person in ground_truth_letter.__getattribute__(f"{sender_or_receiver}_persons"):
            if inferred_from_function is False and person.inferred_from_function is True:
                continue
            elif inferred_from_correspondence is False and person.inferred_from_correspondence is True:
                continue
            else:
                ground_truth_persons.append(person)

        return ground_truth_persons

    @staticmethod
    def _split_by_pipe(cell: str) -> list[str]:
        """ Splits a CSV cell by the pipe '|' character and strips whitespace. """

        return [s.strip() for s in cell.split('|') if s.strip()]

    @staticmethod
    def _update_persons(persons_csv: str,
                        persons_json: str) -> None:
        """ Convert persons ground truth from a GoogleSheets export CSV to JSON file.

        :param persons_csv: file path of CSV file containing persons ground truth exported from Google Sheets
        :param persons_json: file path of JSON file to save the converted ground truth to
        """

        persons_df = pd.read_csv(persons_csv)
        grouped_persons = persons_df.groupby("identifier_value")
        persons = []

        for identifier, rows in grouped_persons:
            first_row = rows.iloc[0]
            logging.debug(f"Added person {first_row["identifier_value"]}...")
            person = {
                "@context": "http://schema.org",
                "@type": "Person",
                "identifier": [
                    {
                        "@type": "PropertyValue",
                        "propertyID": first_row["identifier_propertyID"],
                        "value": str(first_row["identifier_value"]) if pd.notna(first_row["identifier_value"]) else None
                    }
                ],
                "name": first_row["name"],
                "alternateName": [name.strip() for name in first_row["alternateName"].split(",")] if pd.notna(
                    first_row["alternateName"]) else [],
                "birthDate": str(first_row["birthDate"]) if pd.notna(first_row["birthDate"]) else None,
                "deathDate": str(first_row["deathDate"]) if pd.notna(first_row["deathDate"]) else None,
                "description": first_row["description"] if pd.notna(first_row["description"]) else "",
                "hasOccupation": [],
                "citation": []
            }

            for _, row in rows.iterrows():
                job = {
                    "@type": "Occupation",
                    "name": row["job_name"],
                    "startDate": str(row["job_startDate"]) if pd.notna(row["job_startDate"]) else None,
                    "endDate": str(row["job_endDate"]) if pd.notna(row["job_endDate"]) else None,
                    "employer": {
                        "@type": "Organization",
                        "name": row["employer_name"],
                        "identifier": [
                            {
                                "@type": "PropertyValue",
                                "propertyID": row["employer_identifier_propertyID"],
                                "value": str(row["employer_identifier_value"]) if pd.notna(
                                    row["employer_identifier_value"]) else None  # int(row["employer_identifier_value"])
                            }
                        ]
                    }
                }
                person["hasOccupation"].append(job)

                citation = {
                    "@type": "CreativeWork",
                    "name": row["citation_name"],
                    "url": row["citation_url"]
                }
                if citation not in person["citation"]:
                    person["citation"].append(citation)

            persons.append(person)

        with open(persons_json, "w", encoding="utf-8") as jsonfile:
            json.dump(persons, jsonfile, indent=4)

    def _update_letters(self,
                        letters_csv: str,
                        letters_json_dir: str) -> None:
        """ Convert letters ground truth from a CSV to JSON files.

        :param letters_csv: file path of CSV file containing letters ground truth
        :param letters_json_dir: directory to save the converted ground truth to
        """

        with open(letters_csv, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data = {
                    "letter_title": self._split_by_pipe(row["letter_title"]),
                    "send_date": self._split_by_pipe(row["send_date"]),
                    "sender_persons": self._split_by_pipe(row["sender_persons"]),
                    "receiver_persons": self._split_by_pipe(row["receiver_persons"]),
                    "has_signatures": row["has_signatures"],
                }

                doc_num = row["document_number"]
                filename = os.path.join(letters_json_dir, f"letter{doc_num}.json")

                with open(filename, "w", encoding="utf-8") as jsonfile:
                    json.dump(data, jsonfile, indent=4)
