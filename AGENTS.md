# AGENTS.md

Guardrails for any AI coding assistant (Cursor, Copilot, Claude, etc.) working in this repository.

## Stack

- **Backend:** Python 3.12+, FastAPI, Pydantic v2, in-memory storage (no database)
- **Frontend:** vanilla HTML/CSS/JavaScript — no framework, no build step
- **Tests:** pytest, FastAPI `TestClient`
- **CI:** GitHub Actions (`.github/workflows/ci.yml`) — runs `pytest -v` on every push and pull request
- **Container:** Docker, `Dockerfile` + `.dockerignore` at the repo root — backend only, non-root user

## Run and test commands

```bash
# Install
pip install -r requirements.txt

# Run backend
uvicorn app.main:app --reload

# Run tests
pytest

# Build and run with Docker
docker build -t task-tracker .
docker run -d -p 8000:8000 --name task-tracker task-tracker
```

## Read-first / docs-first guardrail

**Before generating or changing any code, read the relevant existing file(s) first** — do not assume the shape of `app/models.py`, `app/storage.py`, `app/main.py`, or `frontend/index.html` from a generic FastAPI/vanilla-JS template. This project has specific, established conventions (see below) that a generic answer will not match.

Before making changes, also check `docs/midcourse/mini-adr.md` and `docs/final-ai-review.md` for prior decisions — several behaviors here (tag partial-matching, AND-logic on combined filters, rejection of explicit `null` on PATCH) were deliberately chosen after finding bugs, not accidents. Don't "fix" them back to the naive version.

## Project rules

- **Status values are exactly:** `ToDo`, `InProgress`, `Done`. **Priority values are exactly:** `Low`, `Medium`, `High`. Never invent different casing or additional values.
- **Status transitions are restricted:** only `ToDo->InProgress`, `InProgress->Done`, `Done->InProgress` are valid (see `app/business_rules.py`). Same-status and any other transition must return HTTP 422.
- **`TaskUpdate` fields are optional to allow partial updates, but explicit `null` for `title` or `status` must be rejected (422)** — only *omitting* a field means "don't change it." See `docs/midcourse/mini-adr.md` decision #6 for why.
- **Tag filtering and Search both use case-insensitive partial matching** — keep them consistent; do not silently revert one to exact-match.
- **Combined query filters (`status`, `priority`, `tag`, `search`) always combine with AND logic**, never OR.
- **No ORM, no database.** Storage is a module-level in-memory dict (`app/storage.py`). Do not introduce SQLAlchemy, SQLModel, or any persistence layer without an explicit, documented decision.
- **No new product features** in this final-project phase (no comments, auth, notifications, production DB). Only bug fixes, security fixes, or documentation-supported corrections to `app/` or `frontend/` are allowed, and any such change must be explained in `docs/final-ai-review.md`.
- **Never include real secrets, `.env` values, tokens, or personal/customer data** in code, commits, or AI prompts. `.dockerignore` and `.gitignore` both exclude `.env` — keep it that way.

## Before proposing a change

1. Read the file(s) you're changing in full first.
2. State which existing test(s) cover the behavior you're touching, or note that none do.
3. Prefer the smallest diff that fixes the issue — do not rewrite whole files for a one-line fix.
4. If your change affects validation, status codes, or filter behavior, say so explicitly so it can be checked against `docs/midcourse/mini-adr.md`.
