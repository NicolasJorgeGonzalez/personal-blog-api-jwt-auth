from pydantic import BaseModel
from datetime import date
from typing import List

class Publication(BaseModel):
    id:str
    title:str
    content:str
    category:str
    tags:List[str]
    createdAt: str
    updatedAt: str
