from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Literal
from pydantic import BaseModel


@dataclass
class WorkType:
    type: Literal["Dissertation or thesis", "Reference"]


@dataclass
class Author:
    last_name: str
    first_name: str


@dataclass
class Publication:
    title: str
    year: int
    place: Optional[str] = None
    pages: Optional[str] = None
    publisher: Optional[str] = None
    format: Optional[str] = None
    reprint_note: Optional[str] = None


@dataclass
class Examination:
    place: Optional[str] = None
    year: Optional[int] = None


@dataclass
class LibraryReference:
    shelfmark: Optional[str] = None
    publication_number: Optional[str] = None
    subjects: Optional[str] = None


@dataclass
class Document(BaseModel):
    type: WorkType
    author: Author
    publication: Publication
    examination: Examination
    library_reference: LibraryReference