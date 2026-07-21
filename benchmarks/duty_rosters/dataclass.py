"""Pydantic models for Nursing staff duty rosters benchmark output validation.

This module defines the expected structure of model outputs.
"""

from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel

ICON_MAP = {
    "?": "Unbekannt",
    "200": "HomeOffice",
    "202": "Ferien",
    "203": "Kranktag",
    "204": "kIND kRANK",
    "206": "Unfall",
    "207": "Kurse bezahlte Weiterb.",
    "211": "Zügeltag",
    "214": "Mutterschutz",
    "216": "Schultag",
    "219": "BESPRECHUNG",
    "222": "Wunschfrei",
    "224": "Freier Tag",
    "228": "RAI/RUG",
    "232": "Bürotag",
    "238": "Obl. Fort-Bildung",
    "300": "F-Dienst 1",
    "322": "M-Dienst 3",
    "323": "M-Dienst 4",
    "340": "S-Dienst 1",
    "817": "N 1",
    "8897": "Azu-Gespräche dives",
    "905": "TV-FAL",
    "919": "SD",
    "922": "Schülerbetreuung",
    "932": "L",
    "Auszubildende Lerntandem": "Auszubildende Lerntandem",
    "Betriebsausflug": "Betriebsausflug",
    "Interne Einblicke": "Interne Einblicke",
    "PA": "Persönliche Absenz",
    "S": "Schule",
    "Su": "Schwangerschaftsurlaub",
    "uU": "Unbezahlter Urlaub",
}

IconCode = Literal[
    "Auszubildende Lerntandem", "Azu-Gespräche dives", "BESPRECHUNG",
    "Betriebsausflug", "Bürotag", "F-Dienst 1", "Ferien", "Freier Tag",
    "HomeOffice", "Interne Einblicke", "kIND kRANK", "Kranktag",
    "Kurse bezahlte Weiterb.", "L", "M-Dienst 3", "M-Dienst 4",
    "Mutterschutz", "N 1", "Obl. Fort-Bildung", "Persönliche Absenz",
    "RAI/RUG", "S-Dienst 1", "Schule", "Schultag", "Schülerbetreuung",
    "Schwangerschaftsurlaub", "SD", "TV-FAL", "Unbezahlter Urlaub",
    "Unbekannt", "Unfall", "Wunschfrei", "Zügeltag",
]


class ShiftLength(str, Enum):
    FULL = "full"
    HALF_LEFT = "half_left"
    HALF_RIGHT = "half_right"


class ShiftEntry(BaseModel):
    icon: Optional[IconCode] = None
    length: ShiftLength
    planned_on_current_unit: bool
    alternate_unit: Optional[str] = None


class DayEntry(BaseModel):
    date: str
    shifts: list[ShiftEntry]


class Person(BaseModel):
    id: str
    profession: str
    employment_percent: int
    is_jumper: bool
    days: list[DayEntry]


class Schedule(BaseModel):
    year: int
    month: str
    persons: list[Person]