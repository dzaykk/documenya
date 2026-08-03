from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any
from uuid import UUID


@dataclass(slots=True, frozen=True)
class VectorPoint:
    id: UUID
    vector: tuple[float, ...]
    payload: Mapping[str, Any]


@dataclass(slots=True, frozen=True)
class VectorSearchResult:
    id: UUID
    score: float
    payload: Mapping[str, Any]