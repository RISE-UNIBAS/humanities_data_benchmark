from enum import Enum
from typing import List, Optional, Dict
from dataclasses import dataclass, field
from pydantic import BaseModel

class EntryType(str, Enum):
    BOOK = "book"
    ARTICLE = "journal-article"
    OTHER = "other"

@dataclass
class Author:
    family: str
    given: str

@dataclass
class Entry:
    id: str
    type: EntryType
    title: str
    container_title: Optional[str] = None
    author: Optional[List[Author]] = field(default_factory=list)
    note: Optional[str] = None
    publisher: Optional[str] = None
    editor: Optional[List[str]] = field(default_factory=list)
    publisher_place: Optional[str] = None
    issued: Optional[str] = None
    event_date: Optional[str] = None
    related: Optional[List[str]] = field(default_factory=list)
    relation: Optional[Dict] = field(default_factory=dict)
    volume: Optional[str] = None
    page: Optional[str] = None
    fascicle: Optional[str] = None
    reprint: Optional[Dict] = field(default_factory=dict)
    edition: Optional[str] = None
    incomplete: Optional[bool] = None

@dataclass
class Metadata:
    title: str
    year: str
    page_number: Optional[int] = None

@dataclass
class Document(BaseModel):
    metadata: Metadata
    entries: List[Entry]