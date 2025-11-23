from typing import Optional, List
from pydantic import BaseModel


class Advertisement(BaseModel):
    date: Optional[str] = None  # date in ISO 8601 format
    tags_section: Optional[str] = None  # title of the section in which an advertisement is placed
    ntokens: Optional[int] = None  # number of tokens of an advertisement
    text: Optional[str] = None  # text of the advertisement


class Document(BaseModel):
    advertisements: List[Advertisement] = []