from typing import List, Optional
from pydantic import BaseModel


class Metadata(BaseModel):
    send_date: Optional[List[str]]
    letter_title: Optional[List[str]]
    sender_persons: Optional[List[str]]
    receiver_persons: Optional[List[str]]


class Document(BaseModel):
    metadata: Metadata
