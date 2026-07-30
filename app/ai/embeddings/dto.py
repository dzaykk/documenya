from __future__ import annotations

from dataclasses import dataclass

from app.chunking.dto import DocumentChunk


@dataclass(slots=True, frozen=True)
class EmbeddingRequest:
    chunks: list[DocumentChunk]
    batch_size: int | None = None


@dataclass(slots=True, frozen=True)
class EmbeddedChunk:
    chunk: DocumentChunk
    vector: tuple[float, ...]