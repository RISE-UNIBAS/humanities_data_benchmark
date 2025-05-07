from typing import Dict, Optional, List
from dataclasses import dataclass, field
from pydantic import BaseModel


@dataclass
class Advertisement:
    date: Optional[str] = None  # date in ISO 8601 format
    tags_section: Optional[str] = None  # title of the section in which an advertisement is placed
    ntokens: Optional[int] = None  # number of tokens of an advertisement
    text: Optional[str] = None  # text of the advertisement


@dataclass
class Document(BaseModel):
    advertisements: List[Advertisement] = field(default_factory=dict)