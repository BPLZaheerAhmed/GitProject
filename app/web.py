from __future__ import annotations

import os
from threading import Lock
from typing import Any

from flask import Flask, jsonify, render_template_string, request, session

from app.agent import build_agent
from app.cli import MAX_MEMORY_MESSAGES
from app.guardrails import apply_guardrails


HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>LangChain Tool Agent</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f5f7fb;
      --surface: #ffffff;
      --ink: #1b2430;
      --muted: #5f6b7a;
      --line: #d8dee8;
      --accent: #1267b1;
      --accent-dark: #0c4f89;
      --user: #dff0ff;
      --agent: #ffffff;
      --error: #b3261e;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      min-height: 100vh;
      font-family: Arial, Helvetica, sans-serif;
      background: var(--bg);
      color: var(--ink);
    }

    .shell {
      display: grid;
      grid-template-rows: auto 1fr auto;
      min-height: 100vh;
    }

    header {
      border-bottom: 1px solid var(--line);
      background: var(--surface);
      padding: 16px clamp(16px, 4vw, 40px);
    }

    h1 {
      margin: 0;
      font-size: 24px;
      line-height: 1.2;
      letter-spacing: 0;
    }

    .subhead {
      margin-top: 6px;
      color: var(--muted);
      font-size: 14px;
    }

    main {
      width: min(980px, 100%);
      margin: 0 auto;
      padding: 18px clamp(14px, 3vw, 28px);
      overflow: hidden;
    }

    .examples {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-bottom: 14px;
    }

    .example {
      border: 1px solid var(--line);
      background: var(--surface);
      color: var(--ink);
      border-radius: 8px;
      padding: 8px 10px;
      min-height: 36px;
      cursor: pointer;
      font-size: 13px;
    }

    .example:hover {
      border-color: var(--accent);
    }

    .messages {
      height: calc(100vh - 230px);
      min-height: 340px;
      overflow-y: auto;
      border: 1px solid var(--line);
      background: #edf2f8;
      border-radius: 8px;
      padding: 16px;
    }

    .message {
      width: fit-content;
      max-width: min(760px, 88%);
      margin-bottom: 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px 12px;
      white-space: pre-wrap;
      line-height: 1.45;
      font-size: 15px;
    }

    .message.user {
      margin-left: auto;
      background: var(--user);
      border-color: #b8dbf7;
    }

    .message.agent {
      background: var(--agent);
    }

    .message.error {
      color: var(--error);
      border-color: #f1b8b2;
    }

    form {
      width: min(980px, 100%);
      margin: 0 auto;
      padding: 14px clamp(14px, 3vw, 28px) 18px;
      border-top: 1px solid var(--line);
      background: var(--surface);
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 10px;
    }

    textarea {
      width: 100%;
      min-height: 48px;
      max-height: 150px;
      resize: vertical;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      font: inherit;
      color: var(--ink);
    }

    button[type="submit"] {
      width: 92px;
      min-height: 48px;
      border: 0;
      border-radius: 8px;
      background: var(--accent);
      color: white;
      font-weight: 700;
      cursor: pointer;
    }

    button[type="submit"]:hover {
      background: var(--accent-dark);
    }

    button:disabled,
    textarea:disabled {
      opacity: 0.65;
      cursor: wait;
    }

    @media (max-width: 640px) {
      h1 {
        font-size: 20px;
      }

      .messages {
        height: calc(100vh - 280px);
      }

      form {
        grid-template-columns: 1fr;
      }

      button[type="submit"] {
        width: 100%;
      }
    }
  </style>
</head>
<body>
  <div class="shell">
    <header>
      <h1>LangChain Tool Agent</h1>
      <div class="subhead">Short-term memory keeps the last 20 messages in this browser session.</div>
    </header>

    <main>
      <div class="examples" aria-label="Example prompts">
        <button class="example" type="button">What is the weather in Lahore?</button>
        <button class="example" type="button">Search sports team Arsenal</button>
        <button class="example" type="button">Create a SQL query for total orders by customer using customers(id, name) and orders(customer_id, amount)</button>
        <button class="example" type="button">My favorite city is Lahore.</button>
      </div>
      <div id="messages" class="messages" aria-live="polite"></div>
    </main>

    <form id="chat-form">
      <textarea id="message-input" name="message" placeholder="Ask the agent..." autocomplete="off" required></textarea>
      <button id="send-button" type="submit">Send</button>
    </form>
  </div>

  <script>
    const form = document.querySelector("#chat-form");
    const input = document.querySelector("#message-input");
    const sendButton = document.querySelector("#send-button");
    const messages = document.querySelector("#messages");

    function addMessage(role, content, isError = false) {
      const node = document.createElement("div");
      node.className = `message ${role}${isError ? " error" : ""}`;
      node.textContent = content;
      messages.appendChild(node);
      messages.scrollTop = messages.scrollHeight;
    }

    async function sendMessage(text) {
      const message = text.trim();
      if (!message) return;

      addMessage("user", message);
      input.value = "";
      input.disabled = true;
      sendButton.disabled = true;

      try {
        const response = await fetch("/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message })
        });
        const data = await response.json();
        addMessage("agent", data.reply || "No reply returned.", !response.ok);
      } catch (error) {
        addMessage("agent", `Request failed: ${error}`, true);
      } finally {
        input.disabled = false;
        sendButton.disabled = false;
        input.focus();
      }
    }

    form.addEventListener("submit", (event) => {
      event.preventDefault();
      sendMessage(input.value);
    });

    input.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        form.requestSubmit();
      }
    });

    document.querySelectorAll(".example").forEach((button) => {
      button.addEventListener("click", () => {
        input.value = button.textContent;
        input.focus();
      });
    });

    addMessage("agent", "Ready. Ask about weather, sports, calculations, text stats, or SQL.");
  </script>
</body>
</html>
"""


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-only-change-me")
    agent = build_agent()
    agent_lock = Lock()

    @app.get("/")
    def index() -> str:
        return render_template_string(HTML)

    @app.post("/chat")
    def chat():
        body = request.get_json(silent=True) or {}
        user_input = str(body.get("message", ""))

        allowed, payload = apply_guardrails(user_input)
        if not allowed:
            return jsonify({"reply": payload}), 400

        memory = _get_memory()
        user_message = {"role": "user", "content": payload}

        with agent_lock:
            response = agent.invoke({"messages": [*memory, user_message]})

        final_message = response["messages"][-1]
        reply = str(final_message.content)

        memory.extend(
            [
                user_message,
                {"role": "assistant", "content": reply},
            ]
        )
        session["memory"] = memory[-MAX_MEMORY_MESSAGES:]
        session.modified = True

        return jsonify({"reply": reply})

    return app


def _get_memory() -> list[dict[str, Any]]:
    memory = session.get("memory", [])
    if not isinstance(memory, list):
        return []

    valid_messages: list[dict[str, Any]] = []
    for message in memory:
        if not isinstance(message, dict):
            continue

        role = message.get("role")
        content = message.get("content")
        if role in {"user", "assistant"} and isinstance(content, str):
            valid_messages.append({"role": role, "content": content})

    return valid_messages[-MAX_MEMORY_MESSAGES:]


app = create_app()
