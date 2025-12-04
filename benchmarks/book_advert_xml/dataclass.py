"""Pydantic models for Book Advert XML files (malformed) from Avisblatt benchmark output validation.

This module defines the expected structure of model outputs.
"""

from pydantic import BaseModel, Field


class CorrectedAdvert(BaseModel):
    """Main output structure for Book Advert XML files from Avisblatt."""

    fixed_xml: str = Field(..., description="The corrected XML content as a string.")
    number_of_corrections: int = Field(..., description="The number of corrections made to the original XML.")
    explanation: str = Field(None, description="Optional explanation of the corrections made.")