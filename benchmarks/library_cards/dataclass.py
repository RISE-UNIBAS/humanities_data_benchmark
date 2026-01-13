from __future__ import annotations
from typing import List, Optional, Literal, Any
from pydantic import BaseModel


class WorkType(BaseModel):
    """Represents the type of work referenced in a library card.

    Attributes:
        type: Type of work, either "Dissertation or thesis" or "Reference"
    """
    type: Literal["Dissertation or thesis", "Reference"]


class Author(BaseModel):
    """Represents an author on a library card.

    Attributes:
        last_name: Author's last name
        first_name: Author's first name
    """
    last_name: str
    first_name: str


class Publication(BaseModel):
    """Represents publication information from a library card.

    Attributes:
        title: Title of the publication
        year: Year of publication
        place: Place of publication
        pages: Number of pages or page range
        publisher: Publisher name
        format: Format of the publication
        editor: Editor name if applicable
    """
    title: str
    year: str
    place: Optional[str] = None
    pages: Optional[str] = None
    publisher: Optional[str] = None
    format: Optional[str] = None
    editor: Optional[str] = None


class LibraryReference(BaseModel):
    """Represents library-specific reference information.

    Attributes:
        shelfmark: Library shelfmark or call number
        subjects: Subject classifications or tags
    """
    shelfmark: Optional[str] = None
    subjects: Optional[str] = None


class Document(BaseModel):
    """Represents a complete library card document.

    Attributes:
        type: Type of work
        author: Author information
        publication: Publication details
        library_reference: Library reference information
    """
    type: WorkType
    author: Author
    publication: Publication
    library_reference: LibraryReference
