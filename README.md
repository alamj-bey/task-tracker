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
