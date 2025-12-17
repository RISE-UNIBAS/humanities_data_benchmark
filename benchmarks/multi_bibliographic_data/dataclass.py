"""Pydantic models for Multilanguage Multiscript Bibliographic Data benchmark output validation.

This module defines the expected structure of model outputs.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class Title(BaseModel):
    """Title in multiple languages and scripts."""

    arabic: str = Field(description="Title in Arabic script")
    transliterated: str = Field(description="Transliterated title (romanized)")
    german: str = Field(description="German translation of the title")


class PublicationDetails(BaseModel):
    """Publication metadata."""

    organization: Optional[str] = Field(default=None, description="Publishing organization")
    year_hijri: Optional[int] = Field(default=None, description="Publication year (Hijri calendar)")
    year_gregorian: Optional[int] = Field(default=None, description="Publication year (Gregorian calendar)")
    place: Optional[str] = Field(default=None, description="Place of publication")
    language: Optional[str] = Field(default=None, description="Language(s) of publication")
    pages: Optional[str] = Field(default=None, description="Number of pages")


class BibliographicEntry(BaseModel):
    """Single bibliographic entry."""

    id: str = Field(description="Entry identifier")
    author: Optional[str] = Field(default=None, description="Author name (romanized)")
    title: Title = Field(description="Title in multiple languages")
    author_arabic: Optional[str] = Field(default=None, description="Author name in Arabic script")
    publication_details: PublicationDetails = Field(description="Publication information")
    description: str = Field(description="Description of the work (in German)")


class Sequence(BaseModel):
    """Main output structure for Multilanguage Multiscript Bibliographic Data."""

    entries: List[BibliographicEntry] = Field(
        default_factory=list,
        description="List of bibliographic entries extracted from the catalog"
    )
