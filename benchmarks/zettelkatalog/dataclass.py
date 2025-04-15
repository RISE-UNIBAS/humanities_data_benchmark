from typing import List, Optional, Dict
from dataclasses import dataclass, field
from pydantic import BaseModel


@dataclass
class Metadata:
    author: Optional[List[str]] = field(default_factory=list)


@dataclass
class Document(BaseModel):
    metadata: Metadata