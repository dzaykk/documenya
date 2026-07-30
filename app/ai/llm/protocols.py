from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol

from app.llm.dto import (
    ChatMessage,
    GenerationConfig,
    GenerationResult,
)


class LLMProvider(Protocol):
    async def generate(
        self,
        messages: list[ChatMessage],
        config: GenerationConfig,
    ) -> GenerationResult:
        ...

    async def stream(
        self,
        messages: list[ChatMessage],
        config: GenerationConfig,
    ) -> AsyncIterator[str]:
        ...

    async def healthcheck(
        self,
    ) -> bool:
        ...