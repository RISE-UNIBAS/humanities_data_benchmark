from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class TypeValuePair(BaseModel):
    type: str
    value: str

class Entry(BaseModel):
    entry_id: str
    company_name: str
    location: str
    additional_information: Optional[List[TypeValuePair]] = None

class ListPage(BaseModel):
    page_id: str
    entries: List[Entry]