from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ChatRole(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass(slots=True, frozen=True)
class ChatMessage:
    role: ChatRole
    content: str


@dataclass(slots=True, frozen=True)
class GenerationConfig:
    temperature: float
    max_tokens: int
    top_p: float

    frequency_penalty: float
    presence_penalty: float

    stream: bool = False
    stop_sequences: tuple[str, ...] = ()


@dataclass(slots=True, frozen=True)
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass(slots=True, frozen=True)
class GenerationResult:
    answer: str
    usage: TokenUsage
    finish_reason: str


@dataclass(slots=True, frozen=True)
class GenerationChunk:
    text: str
    finish_reason: str | None = None
    usage: TokenUsage | None = None