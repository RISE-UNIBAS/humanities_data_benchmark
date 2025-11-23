from __future__ import annotations
from typing import List, Optional, Literal, Any
from pydantic import BaseModel


class WorkType(BaseModel):
    type: Literal["Dissertation or thesis", "Reference"]


class Author(BaseModel):
    last_name: str
    first_name: str


class Publication(BaseModel):
    title: str
    year: str
    place: Optional[str] = None
    pages: Optional[str] = None
    publisher: Optional[str] = None
    format: Optional[str] = None
    editor: Optional[str] = None


class LibraryReference(BaseModel):
    shelfmark: Optional[str] = None
    subjects: Optional[str] = None


class Document(BaseModel):
    type: WorkType
    author: Author
    publication: Publication
    library_reference: LibraryReference