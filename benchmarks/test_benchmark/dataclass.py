from typing import List
from pydantic import BaseModel

class PersonList(BaseModel):
    persons_mentioned: List[str]