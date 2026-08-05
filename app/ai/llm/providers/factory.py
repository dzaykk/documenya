from __future__ import annotations

import logging

from app.ai.llm.protocols import LLMProvider
from app.ai.llm.providers.ollama import OllamaProvider
from app.ai.llm.providers.openrouter import OpenRouterProvider
from app.core.config import settings


logger = logging.getLogger(__name__)


class LLMProviderFactory:

    @staticmethod
    def create() -> LLMProvider:

        provider = (
            settings.DEFAULT_LLM_PROVIDER
        )

        logger.info(
            "Initializing LLM provider: %s",
            provider,
        )

        match provider:

            case "ollama":

                logger.info(
                    "Using Ollama model=%s url=%s",
                    settings.OLLAMA_MODEL,
                    settings.OLLAMA_URL,
                )

                return OllamaProvider()


            case "openrouter":

                logger.info(
                    "Using OpenRouter model=%s",
                    settings.OPENROUTER_MODEL,
                )

                return OpenRouterProvider()


            case _:

                logger.error(
                    "Unsupported LLM provider: %s",
                    provider,
                )

                raise ValueError(
                    f"Unsupported LLM provider: {provider}"
                )