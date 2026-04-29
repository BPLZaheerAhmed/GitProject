from __future__ import annotations

import json
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen
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


def current_weather(location: str = "Karachi") -> str:
    """Get current weather for a city or location using the public wttr.in API."""
    location = (location or "").strip() or "Karachi"
    url = f"https://wttr.in/{quote(location)}?format=j1"
    request = Request(url, headers={"User-Agent": "langchain-tool-agent/1.0"})

    try:
        with urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        return f"Weather API returned HTTP {exc.code} for {location}."
    except URLError as exc:
        return f"Could not reach the weather API: {exc.reason}."
    except TimeoutError:
        return "Weather API request timed out."
    except (json.JSONDecodeError, KeyError, IndexError) as exc:
        return f"Could not read the weather API response: {exc}."

    current = payload["current_condition"][0]
    area = payload.get("nearest_area", [{}])[0]
    area_name = _area_value(area, "areaName") or location
    country = _area_value(area, "country")
    description = current.get("weatherDesc", [{}])[0].get("value", "Unknown")

    place = f"{area_name}, {country}" if country else area_name
    return (
        f"Weather in {place}: {description}, "
        f"{current.get('temp_C', '?')}C/{current.get('temp_F', '?')}F "
        f"(feels like {current.get('FeelsLikeC', '?')}C/{current.get('FeelsLikeF', '?')}F), "
        f"humidity {current.get('humidity', '?')}%, "
        f"wind {current.get('windspeedKmph', '?')} km/h, "
        f"observed at {current.get('observation_time', 'unknown time')} UTC."
    )


def _area_value(area: dict[str, object], key: str) -> str:
    values = area.get(key)
    if isinstance(values, list) and values and isinstance(values[0], dict):
        value = values[0].get("value")
        if isinstance(value, str):
            return value

    return ""
