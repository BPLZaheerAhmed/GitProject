# LangChain Tool Agent

A small Python LangChain agent that can call local tools for arithmetic, current time, live weather, sports data, text statistics, and SQL query generation. The CLI keeps short-term memory for the last 20 user/agent messages in the current session.

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

To run the web interface:

```powershell
python web_app.py
```

Then open `http://127.0.0.1:5000`.

Try:

```text
What time is it in Asia/Karachi?
What is the weather in Lahore?
Search sports team Arsenal
What are the next events for team id 133604?
Calculate 25 * (18 + 4)
Count the words in: LangChain agents can use tools.
Create a SQL query for: show each customer's total order amount using customers(id, name) and orders(customer_id, amount)
My favorite city is Lahore.
What is the weather there?
```

## How the Agent Works

```mermaid
flowchart TD
    A[You type a question] --> B[agent_app.py chat loop]
    B --> C[LangChain agent (app/agent.py)]
    C --> D{Need a tool?}
    D -->|Yes| E[Call Python tool (app/tools/*)]
    E --> F[calculator / current_time / current_weather / sports tools / text_stats / plain_text_to_sql]
    F --> C
    D -->|No| G[OpenAI ChatGPT model]
    C --> G
    G --> H[Final answer in terminal]
```
