"""Pydantic models for entry localisation in the Basel address book of 1890."""

from typing import List

from pydantic import BaseModel, Field


class Entry(BaseModel):
    box: List[float] = Field(
        description="Bounding box of one directory entry as [x0, y0, x1, y1] pixel coordinates, "
                    "where (x0, y0) is the top-left corner and (x1, y1) is the bottom-right corner. "
                    "If the entry runs over several lines, the box covers all of them."
    )


class AddressBookPage(BaseModel):
    entries: List[Entry] = Field(
        description="All directory entries on the page, column by column from top to bottom."
    )
