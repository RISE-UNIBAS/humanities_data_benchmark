from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class Entry(BaseModel):
    transcription: str

class Company(BaseModel):
    transcription: str

class BID(BaseModel):
    transcription: str

class Location(BaseModel):
    transcription: str

class Card(BaseModel):
    company: Company
    location: Location
    b_id: BID
    date: Optional[str] = None
    information: Optional[List[Entry]] = None