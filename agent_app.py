"""Backward-compatible entrypoint for the LangChain tool agent."""

from app.cli import run_chat


if __name__ == "__main__":
    run_chat()
