from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Source(BaseModel):
    id: str
    title: str
    author: str
    kind: str
    excerpt: str
    relevance: float = Field(ge=0, le=1)


class Step(BaseModel):
    label: str
    detail: str
    status: Literal["complete", "active", "queued", "warning"]
    duration_ms: int = 0


class Verification(BaseModel):
    status: Literal["verified", "partial", "unverified"]
    summary: str
    checks: list[str]


class RouteInfo(BaseModel):
    intent: str
    needs_retrieval: bool
    needs_symbolic_check: bool
    needs_formal_proof: bool
    rationale: str


class SolveRequest(BaseModel):
    query: str = Field(min_length=3, max_length=12000)
    mode: Literal["auto", "proof", "compute", "explain"] = "auto"
    source_ids: list[str] = []


class SolveResponse(BaseModel):
    id: str
    query: str
    answer: str
    latex: str
    steps: list[Step]
    sources: list[Source]
    verification: Verification
    route: RouteInfo
    created_at: datetime
    model: str
    duration_ms: int


class DocumentIngest(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    author: str = "Unknown"
    kind: str = "note"
    text: str = Field(min_length=20, max_length=100000)


class HealthResponse(BaseModel):
    status: str
    retrieval: str
    llm: str
    documents: int


class CorpusStats(BaseModel):
    documents: int
    kinds: dict[str, int]
    authors: int
    average_length: int
