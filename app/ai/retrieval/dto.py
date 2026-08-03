from __future__ import annotations

from dataclasses import dataclass

from app.ai.chunking.dto import DocumentChunk


@dataclass(slots=True, frozen=True)
class RetrievalRequest:
    query: str
    owner_id: int
    top_k: int
    similarity_threshold: float


@dataclass(slots=True, frozen=True)
class RetrievedChunk:
    chunk: DocumentChunk
    score: float


@dataclass(slots=True, frozen=True)
class RetrievalResult:
    chunks: list[RetrievedChunk]