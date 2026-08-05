from __future__ import annotations

from dataclasses import dataclass

from app.ai.chunking.dto import ChunkDTO


@dataclass(slots=True, frozen=True)
class EmbeddingRequest:
    chunks: list[ChunkDTO]
    batch_size: int | None = None


@dataclass(slots=True, frozen=True)
class EmbeddedChunk:
    chunk: ChunkDTO
    vector: tuple[float, ...]