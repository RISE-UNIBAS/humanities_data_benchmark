from typing import List, Optional
from pydantic import BaseModel, field_validator


class Metadata(BaseModel):
    send_date: Optional[List[str]]
    letter_title: Optional[List[str]]
    sender_persons: Optional[List[str]]
    receiver_persons: Optional[List[str]]

    @field_validator("send_date", "letter_title", "sender_persons", "receiver_persons",
                     mode="before")
    @classmethod
    def _drop_empty_entries(cls, value):
        """Drop null and blank entries from the list.

        `Optional[List[str]]` allows the list itself to be null but not an entry within it, and
        models return `[null]` or `["Betreff", null]`. Ground truth is built by `_split_by_pipe`,
        which discards empties, so dropping them here keeps the two sides comparable. The fields
        stay required: a missing key is still a failed extraction.
        """
        if isinstance(value, list):
            return [v for v in value if v is not None and str(v).strip()]
        return value


class Document(BaseModel):
    metadata: Metadata
