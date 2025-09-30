""" letter.py
=============
Letter class. """

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, TypedDict
from datetime import date
from benchmarks.metadata_extraction.person import Person


@dataclass
class Letter:
    """Representation of a letter."""
    document_number: str
    send_date: Optional[date] = None
    letter_title: Optional[str] = None
    sender_persons: Optional[List[Person]] = field(default_factory=list)
    receiver_persons: Optional[List[Person]] = field(default_factory=list)
    has_signatures: Optional[bool] = None

    def __post_init__(self):
        # Normalize letter_title if it's a list:
        if type(self.letter_title) is list:
            self.letter_title = self.letter_title[0] if self.letter_title else None

        # Convert sender and receiver strings to lists if necessary:
        self.sender_persons = self._split_and_process(self.sender_persons)
        self.receiver_persons = self._split_and_process(self.receiver_persons)

        # Normalize date:
        if type(self.send_date) is list:
            self.send_date = self.send_date[0] if self.send_date else None

        # Normalize has_signatures:
        if self.has_signatures == "TRUE":
            self.has_signatures = True
        else:
            self.has_signatures = False

    @staticmethod
    def _split_and_process(persons):
        if persons is None:
            return None
        if isinstance(persons, str):
            persons = [p.strip() for p in persons.split('|')]
        # Handle lists that might contain non-string items
        if isinstance(persons, list):
            result = []
            for p in persons:
                if isinstance(p, str):
                    result.append(Person.from_string(p))
                elif isinstance(p, Person):
                    result.append(p)
                elif isinstance(p, dict):
                    # Handle dict format (from Pydantic models)
                    result.append(Person(**p))
                else:
                    # Skip invalid items
                    continue
            return result
        return [Person.from_string(str(p)) for p in persons]
