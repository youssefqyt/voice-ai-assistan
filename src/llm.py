"""Ollama client and bounded in-memory conversation history."""

from __future__ import annotations

import requests

from src.settings import Settings

_conversation: list[dict[str, str]] = []


def reset_conversation() -> None:
    """Clear local conversation context."""
    _conversation.clear()


def ask_ai(question: str, *, settings: Settings | None = None) -> str:
    settings = settings or Settings.from_env()
    question = question.strip()
    if not question:
        raise ValueError("Question cannot be empty")
    messages = [
        {"role": "system", "content": "You are a helpful voice assistant. Answer naturally and briefly."},
        *_conversation,
        {"role": "user", "content": question},
    ]
    try:
        response = requests.post(
            f"{settings.ollama_url}/api/chat",
            json={"model": settings.ollama_model, "messages": messages, "stream": False},
            timeout=settings.ollama_timeout,
        )
        response.raise_for_status()
        answer = response.json().get("message", {}).get("content", "").strip()
        if not answer:
            raise ValueError("Ollama returned an empty response")
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Could not reach Ollama at {settings.ollama_url}. Start Ollama and pull '{settings.ollama_model}'."
        ) from exc
    except (ValueError, AttributeError, TypeError) as exc:
        raise RuntimeError(f"Ollama returned an invalid response: {exc}") from exc

    _conversation.extend(({"role": "user", "content": question}, {"role": "assistant", "content": answer}))
    del _conversation[:-2 * settings.conversation_turns]
    return answer
