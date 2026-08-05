from __future__ import annotations

from app.ai.llm.dto import (
    ChatMessage,
    ChatRole,
)


def build_rag_messages(
    question: str,
    context: str,
) -> list[ChatMessage]:

    return [

        ChatMessage(
            role=ChatRole.SYSTEM,
            content="""
You are an AI assistant that answers questions using the provided document context.

Rules:

- Use ONLY the supplied context.
- Do not invent information.
- If the answer cannot be found in the context, answer:
  "I don't know based on the provided documents."
- Keep answers concise.
- When appropriate, quote important facts directly from the context.
""".strip(),
        ),

        ChatMessage(
            role=ChatRole.USER,
            content=f"""
Context:

{context}

Question:

{question}
""".strip(),
        ),
    ]