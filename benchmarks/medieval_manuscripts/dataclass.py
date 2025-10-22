from typing import Optional, List
from pydantic import BaseModel


class FolioEntry(BaseModel):
    folio: str
    text: str
    addition1: Optional[str] = None
    addition2: Optional[str] = None
    addition3: Optional[str] = None


class Document(BaseModel):
    folios: List[FolioEntry]
