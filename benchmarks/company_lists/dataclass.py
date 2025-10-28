from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class Entry(BaseModel):
    entry_id: str
    company_name: str
    location: str

class ListPage(BaseModel):
    page_id: str
    entries: List[Entry]