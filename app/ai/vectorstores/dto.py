from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True, frozen=True)
class VectorPoint:
    id: str
    vector: tuple[float, ...]
    payload: Mapping[str, Any]


@dataclass(slots=True, frozen=True)
class VectorSearchResult:
    point_id: str
    score: float
    payload: Mapping[str, Any]