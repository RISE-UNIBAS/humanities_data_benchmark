from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class EntryType(str, Enum):
    BOOK = "book"
    ARTICLE = "journal-article"
    OTHER = "other"


class Author(BaseModel):
    family: str
    given: str


class Entry(BaseModel):
    id: str
    type: EntryType
    title: str
    container_title: Optional[str] = None
    author: Optional[List[Author]] = None
    note: Optional[str] = None
    publisher: Optional[str] = None
    editor: Optional[List[str]] = None
    publisher_place: Optional[str] = None
    issued: Optional[str] = None
    event_date: Optional[str] = None
    related: Optional[List[str]] = None
    relation: Optional[str] = None
    volume: Optional[str] = None
    page: Optional[str] = None
    fascicle: Optional[str] = None
    reprint: Optional[str] = None
    edition: Optional[str] = None
    incomplete: Optional[bool] = None


class Metadata(BaseModel):
    title: str
    year: str
    page_number: Optional[int] = None


class Document(BaseModel):
    metadata: Metadata
    entries: List[Entry]
