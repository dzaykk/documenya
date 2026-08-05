from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True, frozen=True)
class ChunkMetadata:
    document_id: int
    owner_id: int
    chunk_index: int
    page: int | None = None
    title: str | None = None
    section: str | None = None
    start_char: int | None = None
    end_char: int | None = None


@dataclass(slots=True, frozen=True)
class ChunkDTO:
    id: UUID
    document_id: int
    text: str
    metadata: ChunkMetadata