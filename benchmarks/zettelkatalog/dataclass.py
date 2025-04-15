from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from pydantic import BaseModel


@dataclass
class Author:
    last_name: str
    first_name: str


@dataclass
class Publication:
    place: str
    year: int
    pages: Optional[str] = None
    publisher: Optional[str] = None
    format: Optional[str] = None


@dataclass
class Education:
    secondary: Optional[str] = None
    university: List[str] = field(default_factory=list)


@dataclass
class Examination:
    location: str
    count: int


@dataclass
class PersonalData:
    birth_date: Optional[str] = None
    birth_place: Optional[str] = None
    residence: Optional[str] = None
    nationality: Optional[str] = None
    education: Optional[Education] = None
    examinations: List[Examination] = field(default_factory=list)
    final_exam_location: Optional[str] = None
    final_exam_date: Optional[str] = None


@dataclass
class Document(BaseModel):
    author: Author
    title: str
    publication: Publication
    type: str
    institution: Optional[str] = None
    language: Optional[str] = None
    notes: Optional[str] = None
    defense_date: Optional[str] = None
    advisor: Optional[str] = None
    department: Optional[str] = None
    director: Optional[str] = None
    personal_data: Optional[PersonalData] = None
    library_reference: Optional[str] = None
