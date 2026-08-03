from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol

from app.ai.llm.dto import (
    ChatMessage,
    GenerationChunk,
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
    ) -> AsyncIterator[GenerationChunk]:
        ...

    async def healthcheck(
        self,
    ) -> bool:
        ...