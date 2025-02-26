from typing import List, Optional, Dict
from dataclasses import dataclass, field
from pydantic import BaseModel


@dataclass
class Metadata:
    send_date: Optional[str]
    letter_title: Optional[str]
    sender_persons: Optional[List[str]]
    receiver_persons: Optional[List[str]]

@dataclass
class Document(BaseModel):
    metadata: Metadata