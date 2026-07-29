# Task Tracker

A FastAPI backend + vanilla JS Kanban frontend, built for the AI-Assisted Coding course (Modules 1-3 baseline, extended in the mid-course project with Tags and Search+Filters).

## Backend fields
- `id, title, description, status, priority, assignee, created_at, updated_at`
- `status`: `ToDo`, `InProgress`, `Done`
- `priority`: `Low`, `Medium`, `High`
- Allowed status transitions: `ToDo -> InProgress`, `InProgress -> Done`, `Done -> InProgress`

## Setup

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

## Run the backend

```bash
uvicorn app.main:app --reload
```
- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Open the frontend

With the backend running, open `frontend/index.html` directly in your browser
(double-click it, or use a simple local server e.g. `python -m http.server 5500` from the `frontend/` folder, then visit http://localhost:5500).

## Run tests

```bash
pytest
```

## Project structure

```
app/
  main.py            FastAPI app and routes
  models.py          Pydantic models (TaskCreate, TaskUpdate, TaskResponse)
  storage.py         In-memory storage layer
  business_rules.py  Status transition validation
frontend/
  index.html         Kanban board UI
tests/
  conftest.py        Pytest fixtures (client, created_task, storage reset)
  test_tasks.py       API test suite
```
## Final Project

Branch reviewed: final-project

### What this submission demonstrates
- Existing Task Tracker app (baseline + Tags + Search/combined filters from the mid-course project) still runs inside the intended course scope. No new product features were added in this phase.
- CI runs the pytest suite on push and pull request via `.github/workflows/ci.yml`.
- Docker image builds and runs with `/health` returning 200, as a non-root user, with no secrets or unrelated files baked in.
- AI review, security, and ownership evidence is in `docs/final-ai-review.md`, `docs/release-evidence.md`, and `docs/ai-playbook.md`.

### How to run locally
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

### How to run tests
```bash
pytest
```

### How to run with Docker
```bash
docker build -t task-tracker .
docker run -d -p 8000:8000 --name task-tracker task-tracker
curl http://localhost:8000/health
```

### Evidence files
- `docs/release-evidence.md`
- `docs/final-ai-review.md`
- `docs/ai-playbook.md`
- `docs/midcourse/` (mid-course project evidence, carried forward)

### AI assistance summary
AI helped draft or review: CI workflow, Dockerfile, documentation, security mini-review, debugging (three real bugs found and fixed during the mid-course and final phases).
I verified the work by: running the full pytest suite (35 passing), manually exercising the API with `Invoke-RestMethod`, opening the frontend in a browser, checking GitHub Actions run results, and building/running the Docker container and confirming `/health`, the non-root user, and the absence of baked-in secrets.
One AI suggestion I rejected or corrected: the original `requirements.txt` used exact version pins that failed to install cleanly on this machine's Python version (no pre-built wheel, required compiling from source); corrected to minimum-version constraints instead. Full detail in `docs/final-ai-review.md`.
