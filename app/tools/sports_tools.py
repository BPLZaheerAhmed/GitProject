from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


THESPORTSDB_BASE_URL = "https://www.thesportsdb.com/api/v1/json"
DEFAULT_THESPORTSDB_API_KEY = "123"


def search_sports_team(team_name: str) -> str:
    """Search TheSportsDB v1 for a sports team by name."""
    team_name = (team_name or "").strip()
    if not team_name:
        return "Please provide a team name to search."

    payload = _get_thesportsdb_json("searchteams.php", {"t": team_name})
    if isinstance(payload, str):
        return payload

    teams = payload.get("teams") or []
    if not teams:
        return f"No team found for '{team_name}'."

    summaries = []
    for team in teams[:5]:
        summaries.append(
            " | ".join(
                part
                for part in (
                    f"id={team.get('idTeam', '?')}",
                    team.get("strTeam") or "Unknown team",
                    team.get("strSport") or "",
                    team.get("strLeague") or "",
                    team.get("strCountry") or "",
                    f"stadium={team.get('strStadium')}" if team.get("strStadium") else "",
                )
                if part
            )
        )

    return "\n".join(summaries)


def sports_team_next_events(team_id: str) -> str:
    """Get upcoming events for a team from TheSportsDB v1 using its team ID."""
    team_id = (team_id or "").strip()
    if not team_id:
        return "Please provide a TheSportsDB team ID."

    payload = _get_thesportsdb_json("eventsnext.php", {"id": team_id})
    if isinstance(payload, str):
        return payload

    return _format_events(payload.get("events"), f"No upcoming events found for team ID {team_id}.")


def sports_team_last_events(team_id: str) -> str:
    """Get recent past events for a team from TheSportsDB v1 using its team ID."""
    team_id = (team_id or "").strip()
    if not team_id:
        return "Please provide a TheSportsDB team ID."

    payload = _get_thesportsdb_json("eventslast.php", {"id": team_id})
    if isinstance(payload, str):
        return payload

    return _format_events(payload.get("results"), f"No recent events found for team ID {team_id}.")


def _get_thesportsdb_json(endpoint: str, params: dict[str, str]) -> dict[str, object] | str:
    api_key = os.getenv("THESPORTSDB_API_KEY", DEFAULT_THESPORTSDB_API_KEY)
    query = urlencode(params)
    url = f"{THESPORTSDB_BASE_URL}/{api_key}/{endpoint}?{query}"
    request = Request(url, headers={"User-Agent": "langchain-tool-agent/1.0"})

    try:
        with urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        return f"TheSportsDB API returned HTTP {exc.code}."
    except URLError as exc:
        return f"Could not reach TheSportsDB API: {exc.reason}."
    except TimeoutError:
        return "TheSportsDB API request timed out."
    except json.JSONDecodeError as exc:
        return f"Could not read TheSportsDB API response: {exc}."


def _format_events(events: object, empty_message: str) -> str:
    if not isinstance(events, list) or not events:
        return empty_message

    summaries = []
    for event in events[:5]:
        if not isinstance(event, dict):
            continue

        score = ""
        home_score = event.get("intHomeScore")
        away_score = event.get("intAwayScore")
        if home_score is not None and away_score is not None:
            score = f"score={home_score}-{away_score}"

        summaries.append(
            " | ".join(
                part
                for part in (
                    event.get("dateEvent") or "",
                    event.get("strTime") or "",
                    event.get("strEvent") or "Unknown event",
                    event.get("strLeague") or "",
                    score,
                )
                if part
            )
        )

    return "\n".join(summaries) if summaries else empty_message
