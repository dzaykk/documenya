from __future__ import annotations

import logging

import httpx

from app.ai.llm.dto import (
    ChatMessage,
    GenerationConfig,
    GenerationResult,
    TokenUsage,
)
from app.ai.llm.exceptions import (
    LLMProviderError,
)
from app.ai.llm.protocols import (
    LLMProvider,
)
from app.core.config import settings


logger = logging.getLogger(__name__)


class OllamaProvider(
    LLMProvider,
):

    def __init__(
        self,
    ) -> None:

        self.url = settings.OLLAMA_URL
        self.model = settings.OLLAMA_MODEL

        logger.info(
            "Initialized Ollama provider model=%s url=%s",
            self.model,
            self.url,
        )


    async def generate(
        self,
        messages: list[ChatMessage],
        config: GenerationConfig,
    ) -> GenerationResult:

        logger.info(
            "Starting Ollama generation model=%s messages=%s temperature=%s max_tokens=%s",
            self.model,
            len(messages),
            config.temperature,
            config.max_tokens,
        )


        payload = {
            "model": self.model,

            "messages": [
                {
                    "role": msg.role.value,
                    "content": msg.content,
                }
                for msg in messages
            ],

            "stream": False,

            "options": {
                "temperature": config.temperature,
                "top_p": config.top_p,
                "num_predict": config.max_tokens,
            },
        }


        try:

            async with httpx.AsyncClient(
                timeout=settings.LLM_TIMEOUT,
            ) as client:

                response = await client.post(
                    f"{self.url}/api/chat",
                    json=payload,
                )

                response.raise_for_status()

                data = response.json()


            answer = (
                data["message"]["content"]
            )


            logger.info(
                "Ollama generation completed model=%s answer_length=%s",
                self.model,
                len(answer),
            )


            return GenerationResult(

                answer=answer,

                usage=TokenUsage(
                    prompt_tokens=0,
                    completion_tokens=0,
                    total_tokens=0,
                ),

                finish_reason="stop",
            )


        except httpx.HTTPStatusError as exc:

            logger.exception(
                "Ollama HTTP error status=%s",
                exc.response.status_code,
            )

            raise LLMProviderError(
                "Ollama API error",
            ) from exc


        except Exception as exc:

            logger.exception(
                "Ollama generation failed",
            )

            raise LLMProviderError(
                "Ollama generation failed",
            ) from exc



    async def stream(
        self,
        messages: list[ChatMessage],
        config: GenerationConfig,
    ):

        logger.warning(
            "Ollama streaming requested but not implemented",
        )

        raise NotImplementedError(
            "Streaming not implemented for Ollama",
        )


    async def healthcheck(
        self,
    ) -> bool:

        try:

            async with httpx.AsyncClient(
                timeout=5,
            ) as client:

                response = await client.get(
                    f"{self.url}/api/tags",
                )


                healthy = (
                    response.status_code == 200
                )


                if healthy:

                    logger.info(
                        "Ollama healthcheck passed",
                    )

                else:

                    logger.warning(
                        "Ollama healthcheck failed status=%s",
                        response.status_code,
                    )


                return healthy


        except Exception:

            logger.exception(
                "Ollama healthcheck failed",
            )

            return False