from __future__ import annotations

import os
import re

from langchain.chat_models import init_chat_model


BANNED_SQL_RE = re.compile(
    r"\b(ALTER|CREATE|DELETE|DROP|EXEC|EXECUTE|GRANT|INSERT|MERGE|REVOKE|TRUNCATE|UPDATE)\b",
    re.IGNORECASE,
)
READ_ONLY_START_RE = re.compile(r"^\s*(SELECT|WITH)\b", re.IGNORECASE)


def plain_text_to_sql(
    request: str,
    database_schema: str = "",
    sql_dialect: str = "PostgreSQL",
) -> str:
    """
    Convert a plain-English analytics request into a read-only SQL query.

    Include table names and columns in database_schema when the request depends on
    a specific database shape, for example: "users(id, email), orders(id, user_id)".
    """
    if not request.strip():
        return "Please provide a plain-text request to convert into SQL."

    model_name = os.getenv("LANGCHAIN_MODEL", "gpt-4.1-mini")
    model = init_chat_model(model_name)
    schema_context = database_schema.strip() or "No schema was provided. Use clear placeholder table and column names."

    response = model.invoke(
        [
            (
                "system",
                "You convert plain-English requests into read-only SQL. "
                "Return exactly one SQL query and no explanation. "
                "Only produce SELECT queries or WITH queries that end in SELECT. "
                "Never produce statements that modify schema or data.",
            ),
            (
                "human",
                f"SQL dialect: {sql_dialect}\n"
                f"Database schema:\n{schema_context}\n\n"
                f"Plain-text request:\n{request}",
            ),
        ]
    )

    query = _extract_text(response.content).strip()
    query = _strip_markdown_fence(query).strip()

    if not query:
        return "Could not generate a SQL query."

    if not READ_ONLY_START_RE.search(query) or BANNED_SQL_RE.search(query):
        return (
            "The generated SQL was blocked because it was not a read-only SELECT query. "
            "Try rephrasing the request as a reporting or analytics question."
        )

    return query.rstrip(";") + ";"


def _extract_text(content: object) -> str:
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text") or item.get("content")
                if isinstance(text, str):
                    parts.append(text)
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join(parts)

    return str(content)


def _strip_markdown_fence(text: str) -> str:
    fenced = re.fullmatch(r"\s*```(?:sql)?\s*(.*?)\s*```\s*", text, re.IGNORECASE | re.DOTALL)
    if fenced:
        return fenced.group(1)

    return text
