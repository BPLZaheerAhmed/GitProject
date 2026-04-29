from __future__ import annotations

import re
from typing import Any


MAX_MEMORY_MESSAGES = 20
MEMORY_TYPES = ("weather", "sports", "sql", "calculator", "text_stats", "memory")
Message = dict[str, Any]
TypedMemory = dict[str, list[Message]]


def classify_query_type(text: str) -> str:
    """Choose the memory bucket most relevant to a user message."""
    lowered = (text or "").lower()

    if _has_any(
        lowered,
        (
            "weather",
            "temperature",
            "humidity",
            "wind",
            "forecast",
            "rain",
            "snow",
            "city",
            "location",
        ),
    ):
        return "weather"

    if _has_any(
        lowered,
        (
            "sport",
            "sports",
            "team",
            "teams",
            "player",
            "match",
            "game",
            "event",
            "events",
            "league",
            "arsenal",
            "football",
            "soccer",
            "nba",
            "nfl",
            "mlb",
            "nhl",
        ),
    ):
        return "sports"

    if _has_any(
        lowered,
        (
            "sql",
            "query",
            "select",
            "table",
            "tables",
            "column",
            "columns",
            "database",
            "schema",
        ),
    ):
        return "sql"

    if _looks_like_calculation(lowered):
        return "calculator"

    if _has_any(lowered, ("count", "characters", "words", "lines", "text stats")):
        return "text_stats"

    return "memory"


def relevant_memory(memory: TypedMemory, query_type: str) -> list[Message]:
    """Return only the message history for the selected memory type."""
    return _valid_messages(memory.get(query_type, []))[-MAX_MEMORY_MESSAGES:]


def remember_exchange(memory: TypedMemory, query_type: str, user_text: str, assistant_text: str) -> TypedMemory:
    """Store one user/assistant exchange in the selected memory bucket."""
    clean_memory = sanitize_memory(memory)
    bucket = clean_memory.setdefault(query_type, [])
    bucket.extend(
        [
            {"role": "user", "content": user_text},
            {"role": "assistant", "content": assistant_text},
        ]
    )
    clean_memory[query_type] = bucket[-MAX_MEMORY_MESSAGES:]
    return clean_memory


def sanitize_memory(memory: object) -> TypedMemory:
    if not isinstance(memory, dict):
        return {memory_type: [] for memory_type in MEMORY_TYPES}

    clean_memory: TypedMemory = {}
    for memory_type in MEMORY_TYPES:
        clean_memory[memory_type] = _valid_messages(memory.get(memory_type, []))[-MAX_MEMORY_MESSAGES:]

    return clean_memory


def _valid_messages(messages: object) -> list[Message]:
    if not isinstance(messages, list):
        return []

    valid_messages: list[Message] = []
    for message in messages:
        if not isinstance(message, dict):
            continue

        role = message.get("role")
        content = message.get("content")
        if role in {"user", "assistant"} and isinstance(content, str):
            valid_messages.append({"role": role, "content": content})

    return valid_messages


def _has_any(text: str, words: tuple[str, ...]) -> bool:
    return any(word in text for word in words)


def _looks_like_calculation(text: str) -> bool:
    if _has_any(text, ("calculate", "math", "add", "subtract", "multiply", "divide", "percent")):
        return True

    return bool(re.search(r"\d+\s*[-+*/%]\s*\d+", text))
