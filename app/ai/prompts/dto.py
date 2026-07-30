from __future__ import annotations

from dataclasses import dataclass

from app.llm.dto import ChatMessage


@dataclass(slots=True, frozen=True)
class Prompt:
    messages: list[ChatMessage]
    context: str = ""