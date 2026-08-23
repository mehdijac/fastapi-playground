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
