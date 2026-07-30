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
    temperature: float = 0.1
    max_tokens: int = 1024
    top_p: float = 0.95
    stream: bool = False
    stop_sequences: tuple[str, ...] = ()
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0


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