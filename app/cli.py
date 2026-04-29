from __future__ import annotations

from app.agent import build_agent
from app.guardrails import apply_guardrails
from app.memory import classify_query_type, relevant_memory, remember_exchange, sanitize_memory


def run_chat() -> None:
    agent = build_agent()
    memory = sanitize_memory({})
    print("LangChain tool agent is ready. Type 'exit' to quit.")

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            break

        allowed, payload = apply_guardrails(user_input)
        if not allowed:
            print(f"\nAgent: {payload}")
            continue

        query_type = classify_query_type(payload)
        history = relevant_memory(memory, query_type)
        user_message = {"role": "user", "content": payload}
        response = agent.invoke({"messages": [*history, user_message]})
        final_message = response["messages"][-1]
        print(f"\nAgent: {final_message.content}")
        memory = remember_exchange(memory, query_type, payload, str(final_message.content))


if __name__ == "__main__":
    run_chat()
