from __future__ import annotations

from app.agent import build_agent
from app.guardrails import apply_guardrails


def run_chat() -> None:
    agent = build_agent()
    print("LangChain tool agent is ready. Type 'exit' to quit.")

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            break

        allowed, payload = apply_guardrails(user_input)
        if not allowed:
            print(f"\nAgent: {payload}")
            continue

        response = agent.invoke({"messages": [{"role": "user", "content": payload}]})
        final_message = response["messages"][-1]
        print(f"\nAgent: {final_message.content}")


if __name__ == "__main__":
    run_chat()

