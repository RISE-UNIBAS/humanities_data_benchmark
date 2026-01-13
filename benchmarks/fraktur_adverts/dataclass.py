from typing import Optional, List
from pydantic import BaseModel


class Advertisement(BaseModel):
    """Represents a single advertisement from a Fraktur document.

    Attributes:
        date: Date in ISO 8601 format
        tags_section: Title of the section in which an advertisement is placed
        text: Text of the advertisement
    """
    date: Optional[str] = None
    tags_section: Optional[str] = None
    text: Optional[str] = None


class Document(BaseModel):
    """Represents a document containing multiple advertisements.

    Attributes:
        advertisements: List of advertisements in the document
    """
    advertisements: List[Advertisement] = []
