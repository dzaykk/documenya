from __future__ import annotations

from dataclasses import dataclass

from app.ai.llm.dto import ChatMessage


@dataclass(slots=True, frozen=True)
class Prompt:
    messages: list[ChatMessage]
    context: str = ""