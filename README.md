# LangChain Tool Agent

A small Python LangChain agent that can call local tools for arithmetic, current time, and text statistics.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` and set `OPENAI_API_KEY`.

## Run

```powershell
python agent_app.py
```

You can also run the CLI module directly:

```powershell
python -m app.cli
```

Try:

```text
What time is it in Asia/Karachi?
Calculate 25 * (18 + 4)
Count the words in: LangChain agents can use tools.
```

## How the Agent Works

```mermaid
flowchart TD
    A[You type a question] --> B[agent_app.py chat loop]
    B --> C[LangChain agent (app/agent.py)]
    C --> D{Need a tool?}
    D -->|Yes| E[Call Python tool (app/tools/*)]
    E --> F[calculator / current_time / text_stats]
    F --> C
    D -->|No| G[OpenAI ChatGPT model]
    C --> G
    G --> H[Final answer in terminal]
```
