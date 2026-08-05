from __future__ import annotations

import logging

from app.ai.llm.config import (
    default_generation_config,
)
from app.ai.llm.dto import (
    ChatMessage,
    GenerationConfig,
    GenerationResult,
)
from app.ai.llm.protocols import LLMProvider


logger = logging.getLogger(__name__)


class LLMService:
    def __init__(
        self,
        provider: LLMProvider,
    ) -> None:
        self._provider = provider

        logger.info(
            "LLM service initialized provider=%s",
            provider.__class__.__name__,
        )

    async def generate(
        self,
        messages: list[ChatMessage],
        config: GenerationConfig | None = None,
    ) -> GenerationResult:
        
        if config is None:
            config = default_generation_config()

        logger.info(
            "LLM generation started "
            "provider=%s messages=%s temperature=%s max_tokens=%s",
            self._provider.__class__.__name__,
            len(messages),
            config.temperature,
            config.max_tokens,
        )


        try:
            result = await self._provider.generate(
                messages,
                config,
            )

            logger.info(
                "LLM generation completed "
                "provider=%s answer_length=%s total_tokens=%s finish_reason=%s",
                self._provider.__class__.__name__,
                len(result.answer),
                result.usage.total_tokens,
                result.finish_reason,
            )

            return result


        except Exception:
            logger.exception(
                "LLM generation failed provider=%s",
                self._provider.__class__.__name__,
            )

            raise

    async def healthcheck(
        self,
    ) -> bool:
        logger.info(
            "LLM healthcheck started provider=%s",
            self._provider.__class__.__name__,
        )

        try:
            result = await self._provider.healthcheck()

            if result:
                logger.info(
                    "LLM healthcheck passed provider=%s",
                    self._provider.__class__.__name__,
                )

            else:
                logger.warning(
                    "LLM healthcheck failed provider=%s",
                    self._provider.__class__.__name__,
                )

            return result

        except Exception:
            logger.exception(
                "LLM healthcheck error provider=%s",
                self._provider.__class__.__name__,
            )

            return False