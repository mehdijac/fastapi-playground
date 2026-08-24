# fastapi-playground

A uv-managed FastAPI + Pydantic playground.

## Development

```bash
uv sync
uv run uvicorn main:app --reload
uv run pytest
```

Or via Docker:

```bash
docker build -t fastapi-playground .
docker run -p 8000:8000 fastapi-playground
```

Pre-commit hooks (ruff lint/format + pytest) run automatically on `git commit`. First-time setup:

```bash
uv run pre-commit install
```

## AI engineering news agent

`news_agent/` is a LangGraph agent that collects AI engineering news via a custom
MCP tool (curated RSS feeds) and synthesizes a digest with a local Ollama model,
served through its own FastAPI app.

```bash
ollama serve                                          # local LLM, needs llama3.2 pulled
uv run uvicorn news_agent.api:app --port 8010 --reload
```

Open `http://127.0.0.1:8010`, click "Refresh digest" to generate one (calls the
local model, takes ~30s), and get a synthesized summary plus every source article.

### Monitoring (Arize Phoenix)

Tracing is on by default and covers both LLM/tool calls (prompts, latency, token
counts) and HTTP requests to the app. Run Phoenix separately to view it:

```bash
uv run phoenix serve   # UI + trace collector at http://127.0.0.1:6006
```

If Phoenix isn't running, the app still works fine — span export just fails
silently in the background instead of blocking requests. To disable tracing
entirely (already the default in tests/CI):

```bash
export NEWS_AGENT_ENABLE_OBSERVABILITY=false
```

## Workflow

`master` is protected: no direct pushes, CI must pass, merges must come through a pull request.

For a new feature:

```bash
git checkout master && git pull
git checkout -b feature/short-description
# ... work, commit ...
git push -u origin feature/short-description
gh pr create --fill
```

Once the `test` check passes on the PR, merge it (squash or rebase — merge commits are disabled to keep history linear). The feature branch is deleted automatically on merge.
