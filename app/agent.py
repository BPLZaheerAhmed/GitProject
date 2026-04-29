from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain.agents import create_agent

from app.tools.math_tools import calculator
from app.tools.misc_tools import current_time, current_weather, text_stats
from app.tools.sql_tools import plain_text_to_sql
from app.tools.sports_tools import search_sports_team, sports_team_last_events, sports_team_next_events


load_dotenv()


def build_agent():
    model = os.getenv("LANGCHAIN_MODEL", "gpt-4.1-mini")

    return create_agent(
        model=model,
        tools=[
            calculator,
            current_time,
            current_weather,
            text_stats,
            plain_text_to_sql,
            search_sports_team,
            sports_team_next_events,
            sports_team_last_events,
        ],
        system_prompt=(
            "You are a helpful Python LangChain agent. Use tools when they make "
            "the answer more accurate. Keep responses concise and explain which "
            "tool you used when relevant."
        ),
    )
