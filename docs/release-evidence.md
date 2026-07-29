# Release Evidence

## Baseline

- **Branch:** final-project
- **Date:** 2026-07-29
- **Local app run command:** `uvicorn app.main:app --reload`
- **/health result:**
  ```
  GET http://localhost:8000/health
  200 OK
  { "status": "ok", "timestamp": "2026-07-29T13:19:35.783565+00:00" }
  ```
- **Frontend check:** Opened `frontend/index.html` directly in the browser with the backend running. Kanban board (To Do / In Progress / Done columns) and the create/edit task modal are both visible and functional, unchanged from the mid-course project.
- **Test command:** `pytest`
- **Test result:**
  ```
  collected 35 items
  tests\test_tasks.py ...................................    [100%]
  35 passed, 3 warnings in 0.38s
  ```
  No pre-existing failures. No tests were failing before final-project work began.

## CI evidence

- **Workflow file:** `.github/workflows/ci.yml`
- **Latest run link or note:** 3 consecutive green runs on the `final-project` branch, triggered automatically by each push (adding `ci.yml`, then `Dockerfile`, then `.dockerignore`). All 3 completed successfully in 17-18 seconds each. See the Actions tab on the repository for the run history.
- **Test command used by CI:** `pytest -v` (after `pip install -r requirements.txt`)
- **Shortcut check:** confirmed no `continue-on-error`, no `|| true`, pytest is not skipped or conditionally disabled, Python version is pinned explicitly (`3.12`, not left as a floating/unspecified version), and dependency installation (`pip install -r requirements.txt`) runs before tests.

## Docker evidence

- **Build command:** `docker build -t task-tracker .`
  - Result: `[+] Building 190.6s (11/11) FINISHED` — all 6 build steps completed, image tagged `task-tracker:latest`.
- **Run command:** `docker run -d -p 8000:8000 --name task-tracker-test task-tracker`
  - Result: container started, confirmed via `docker ps` showing status `Up` with port mapping `0.0.0.0:8000->8000/tcp`.
- **/health check:**
  ```
  Invoke-RestMethod -Uri "http://localhost:8000/health"
  status timestamp
  ------ ---------
  ok     2026-07-29T07:32:31.904017+00:00
  ```
  Confirmed the containerized app responds identically to the local (non-Docker) run.
- **Non-root check:** `docker exec task-tracker-test whoami` → `appuser` (not `root`). The Dockerfile creates and switches to a dedicated non-root user before the container's entrypoint runs.
- **No-baked-secrets check:** `docker exec task-tracker-test ls -la /app` → only `app/` and `requirements.txt` are present inside the image. No `.env`, no `tests/`, no `frontend/`, no `docs/`, no `.git/` — confirmed `.dockerignore` correctly excludes everything not required to run the backend.

## Documentation claim-vs-reality log

| Claim checked | Evidence used | Result | Change made, if any |
|---|---|---|---|
| README states the backend starts with `uvicorn app.main:app --reload` and serves on port 8000 | Ran the exact command locally | Confirmed accurate — server started on `http://127.0.0.1:8000` as documented | None needed |
| README/brief implies `GET /health` returns HTTP 200 with a status field | Called the endpoint locally and via the Docker container | Confirmed accurate in both environments — same response shape (`status`, `timestamp`) | None needed |
| `PATCH /tasks/{id}` should reject a `same -> same` status transition with HTTP 422 (Module 2 business rule, carried into this project) | Ran `pytest -k test_patch_same_status_returns_422`, and manually verified via `Invoke-RestMethod` earlier in development | Confirmed accurate — 422 returned with a descriptive error message listing allowed transitions | None needed |
