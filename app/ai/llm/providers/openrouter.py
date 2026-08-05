from __future__ import annotations

import asyncio
import logging
import time

import httpx

from app.ai.llm.dto import (
    ChatMessage,
    GenerationConfig,
    GenerationResult,
    TokenUsage,
)
from app.ai.llm.exceptions import (
    LLMConfigurationError,
    LLMProviderError,
)
from app.ai.llm.protocols import LLMProvider
from app.core.config import settings


logger = logging.getLogger(__name__)


class OpenRouterProvider(LLMProvider):

    RETRYABLE_STATUS_CODES = {
        429,
        500,
        502,
        503,
        504,
    }

    FATAL_STATUS_CODES = {
        400,
        401,
        403,
        404,
        422,
    }

    def __init__(self) -> None:

        if not settings.OPENROUTER_API_KEY:
            raise LLMConfigurationError(
                "OPENROUTER_API_KEY is missing",
            )

        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = settings.OPENROUTER_BASE_URL
        self.model = settings.OPENROUTER_MODEL

        self.client = httpx.AsyncClient(
            timeout=settings.LLM_TIMEOUT,
        )

        logger.info(
            "OpenRouter initialized model=%s",
            self.model,
        )

    async def generate(
        self,
        messages: list[ChatMessage],
        config: GenerationConfig,
    ) -> GenerationResult:

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": message.role.value,
                    "content": message.content,
                }
                for message in messages
            ],
            "temperature": config.temperature,
            "top_p": config.top_p,
            "max_tokens": config.max_tokens,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "Documenya",
        }

        started_at = time.monotonic()

        last_error: Exception | None = None

        data: dict | None = None

        for attempt in range(
            settings.OPENROUTER_MAX_RETRIES
        ):
            try:
                response = await self.client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )

                status = response.status_code

                if status in self.FATAL_STATUS_CODES:
                    raise LLMProviderError(
                        f"OpenRouter rejected request status={status}: "
                        f"{response.text[:300]}"
                    )

                if status in self.RETRYABLE_STATUS_CODES:

                    if attempt + 1 >= settings.OPENROUTER_MAX_RETRIES:
                        raise LLMProviderError(
                            "OpenRouter unavailable after retries"
                        )

                    retry_after = response.headers.get(
                        "Retry-After"
                    )

                    delay = (
                        float(retry_after)
                        if retry_after
                        else settings.OPENROUTER_RETRY_DELAY
                        * (attempt + 1)
                    )

                    logger.warning(
                        "OpenRouter temporary error "
                        "status=%s attempt=%s/%s retry_in=%ss body=%s",
                        status,
                        attempt + 1,
                        settings.OPENROUTER_MAX_RETRIES,
                        delay,
                        response.text[:300],
                    )

                    await asyncio.sleep(delay)

                    continue

                response.raise_for_status()

                data = response.json()

                break

            except httpx.HTTPError as exc:

                last_error = exc

                logger.warning(
                    "OpenRouter request failed "
                    "attempt=%s/%s error=%s",
                    attempt + 1,
                    settings.OPENROUTER_MAX_RETRIES,
                    exc,
                )

                if (
                    attempt + 1
                    >= settings.OPENROUTER_MAX_RETRIES
                ):
                    raise LLMProviderError(
                        "OpenRouter request failed"
                    ) from exc

                await asyncio.sleep(
                    settings.OPENROUTER_RETRY_DELAY
                )

        if data is None:
            raise LLMProviderError(
                "OpenRouter returned no response"
            ) from last_error

        elapsed = (
            time.monotonic() - started_at
        )

        choice = data["choices"][0]

        usage_data = data.get(
            "usage",
            {},
        )

        usage = TokenUsage(
            prompt_tokens=usage_data.get(
                "prompt_tokens",
                0,
            ),
            completion_tokens=usage_data.get(
                "completion_tokens",
                0,
            ),
            total_tokens=usage_data.get(
                "total_tokens",
                0,
            ),
        )

        logger.info(
            "OpenRouter completed "
            "time=%.2fs tokens=%s",
            elapsed,
            usage.total_tokens,
        )

        return GenerationResult(
            answer=choice["message"]["content"] or "",
            usage=usage,
            finish_reason=choice.get(
                "finish_reason",
                "stop",
            ),
        )

    async def stream(
        self,
        messages: list[ChatMessage],
        config: GenerationConfig,
    ):
        raise NotImplementedError(
            "Streaming not implemented",
        )

    async def healthcheck(
        self,
    ) -> bool:

        try:
            response = await self.client.get(
                f"{self.base_url}/models",
                headers={
                    "Authorization": (
                        f"Bearer {self.api_key}"
                    ),
                },
            )

            return response.status_code == 200

        except Exception:

            logger.exception(
                "OpenRouter healthcheck failed",
            )

            return False

    async def close(
        self,
    ) -> None:

        await self.client.aclose()