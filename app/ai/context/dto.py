from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ContextDocument:
    text: str
    title: str | None
    score: float