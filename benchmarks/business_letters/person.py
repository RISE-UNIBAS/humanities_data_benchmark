""" person.py
============
Person class. """

from dataclasses import dataclass


@dataclass
class Person:
    """Representation of a person.

    :param name: name of the person
    :param alternate_names: alternate names of the person
    :param inferred_from_function: whether the person was inferred from a job function
    :param inferred_from_correspondence: whether the person was inferred from the correspondence history
    """

    name: str
    alternate_names: list = None
    inferred_from_function: bool = False
    inferred_from_correspondence: bool = False

    @staticmethod
    def from_string(person: str) -> "Person":
        """Create a Person object from a string.

        Used to parse persons in persons.csv exported from Google Sheets. Inferred attributes are set to True given
        the angle brackets conventions.

        :param person: string representation of a person (i.e., their name)
        """

        try:
            person = person.strip()
            if person.startswith("<<") and person.endswith(">>"):
                return Person(name=person[2:-2].strip(), inferred_from_correspondence=True)
            elif person.startswith("<") and person.endswith(">"):
                return Person(name=person[1:-1].strip(), inferred_from_function=True)
            return Person(name=person)
        except AttributeError:
            return Person(name=None)
