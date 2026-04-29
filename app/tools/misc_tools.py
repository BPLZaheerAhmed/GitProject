from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo


def current_time(timezone: str = "Asia/Karachi") -> str:
    """Get the current date and time for an IANA timezone."""
    try:
        now = datetime.now(ZoneInfo(timezone))
    except Exception:
        return "Unknown timezone. Use an IANA timezone like Asia/Karachi or America/New_York."

    return now.strftime("%Y-%m-%d %H:%M:%S %Z")


def text_stats(text: str) -> str:
    """Count characters, words, and lines in a piece of text."""
    words = text.split()
    lines = text.splitlines() or [text]
    return f"characters={len(text)}, words={len(words)}, lines={len(lines)}"

