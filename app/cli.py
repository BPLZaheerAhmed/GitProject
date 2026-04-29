from __future__ import annotations

from typing import Any

from app.agent import build_agent
from app.guardrails import apply_guardrails


MAX_MEMORY_MESSAGES = 20


def run_chat() -> None:
    agent = build_agent()
    memory: list[dict[str, Any]] = []
    print("LangChain tool agent is ready. Type 'exit' to quit.")

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            break

        allowed, payload = apply_guardrails(user_input)
        if not allowed:
            print(f"\nAgent: {payload}")
            continue

        user_message = {"role": "user", "content": payload}
        response = agent.invoke({"messages": [*memory, user_message]})
        final_message = response["messages"][-1]
        print(f"\nAgent: {final_message.content}")

        memory.extend(
            [
                user_message,
                {"role": "assistant", "content": final_message.content},
            ]
        )
        memory = memory[-MAX_MEMORY_MESSAGES:]


if __name__ == "__main__":
    run_chat()
