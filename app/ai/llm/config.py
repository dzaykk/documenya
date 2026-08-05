from app.ai.llm.dto import GenerationConfig
from app.core.config import settings


def default_generation_config() -> GenerationConfig:

    return GenerationConfig(
        temperature=settings.DEFAULT_TEMPERATURE,
        max_tokens=settings.DEFAULT_MAX_TOKENS,
        top_p=settings.DEFAULT_TOP_P,
        frequency_penalty=settings.DEFAULT_FREQUENCY_PENALTY,
        presence_penalty=settings.DEFAULT_PRESENCE_PENALTY,
    )