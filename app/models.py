from dataclasses import dataclass
from typing import Dict

from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str
    department: str | None = None
    access_level: str = "employee"


class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: list
    
@dataclass
class DocumentChunk:
    content: str
    metadata: Dict