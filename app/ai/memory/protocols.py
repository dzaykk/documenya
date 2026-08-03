from __future__ import annotations

from typing import Protocol

from app.ai.llm.dto import ChatMessage


class ConversationMemory(Protocol):
    async def append(
        self,
        conversation_id: str,
        message: ChatMessage,
    ) -> None:
        ...

    async def history(
        self,
        conversation_id: str,
        limit: int | None = None,
    ) -> list[ChatMessage]:
        ...

    async def summarize(
        self,
        conversation_id: str,
    ) -> str:
        ...

    async def clear(
        self,
        conversation_id: str,
    ) -> None:
        ...