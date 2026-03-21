"""Pydantic models for magazine page advertisement detection."""

from typing import List

from pydantic import BaseModel, Field


class Advertisement(BaseModel):
    box: List[float] = Field(
        description="Bounding box of the advertisement as [x0, y0, x1, y1] pixel coordinates, "
                    "where (x0, y0) is the top-left corner and (x1, y1) is the bottom-right corner."
    )


class MagazinePage(BaseModel):
    advertisements: List[Advertisement] = Field(
        description="All advertisements found on the page. Empty list if none are present."
    )