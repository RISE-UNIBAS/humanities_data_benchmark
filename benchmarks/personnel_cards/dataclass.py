"""Pydantic models for Personnel Cards benchmark output validation.

This module defines the expected structure of model outputs.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class FieldValue(BaseModel):
    """Represents a single field value with transcript and interpretation."""

    diplomatic_transcript: str = Field(
        description="Exact text as written on the card, including abbreviations"
    )
    interpretation: Optional[str] = Field(
        default=None,
        description="Interpretation or expansion of abbreviations and meanings"
    )
    is_crossed_out: bool = Field(
        default=False,
        description="Whether the text has been crossed out on the card"
    )


class TableRow(BaseModel):
    """Represents a single row in the personnel card table."""

    row_number: int = Field(
        description="Sequential row number from top to bottom"
    )
    dienstliche_stellung: FieldValue = Field(
        description="Official position/job title"
    )
    dienstort: FieldValue = Field(
        description="Place of service/work location"
    )
    gehaltsklasse: FieldValue = Field(
        description="Salary class/grade"
    )
    jahresgehalt_monatsgehalt_taglohn: FieldValue = Field(
        description="Annual salary, monthly salary, or daily wage"
    )
    datum_gehaltsänderung: FieldValue = Field(
        description="Date of salary change (day, month, year)"
    )
    bemerkungen: FieldValue = Field(
        description="Remarks, notes, or additional information"
    )


class Table(BaseModel):
    """Main output structure for Personnel Cards."""

    rows: List[TableRow] = Field(
        default_factory=list,
        description="List of all rows in the personnel card table"
    )
