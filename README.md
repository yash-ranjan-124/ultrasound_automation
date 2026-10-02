# MedVision AI Lab

A browser-based foundation for a medical-imaging **research and education** workstation. This project is **not intended for clinical diagnosis**. Model predictions, when implemented in later phases, must be treated as experimental outputs requiring expert review.

## Current phase

This initial architecture phase provides a FastAPI health endpoint, a React research-workstation overview, independent domain types and ports, and tests. **Study upload, video playback, DICOM/NIfTI viewing, tracking, model execution, persistence, and export are not implemented yet.** The overview marks them as planned rather than simulating results.

## Run on Replit

The configured workflows start the FastAPI backend on port 8000 and the Vite frontend on port 5000. Open the web preview to view the frontend. Its `/api` requests proxy to the backend.

Manual setup from the repository root:

```sh
cd backend && uv sync --locked
cd ../frontend && npm ci
```

In separate terminals:

```sh
cd backend && uv run --locked uvicorn medvision.main:app --host 0.0.0.0 --port 8000
cd frontend && npm run dev -- --host 0.0.0.0 --port 5000
```

Check the API with `GET /api/v1/health`. The foundation does not require database credentials to start. PostgreSQL connections and Alembic migrations are deferred until a persistence workflow is implemented.

## Checks

```sh
cd backend
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked mypy src
uv run --locked pytest

cd ../frontend
npm run lint
npm run test
npm run build
```

## Imported prototype

The root-level Python files and sample videos are the original imported research prototype, **not** the browser application. Its original usage is:

```sh
python object_tracker.py --video us_bp.mp4 --tracker csrt --slow 1
```

Keys in the prototype: `s` select region, `n`/`p` next/previous frame after pausing, `q` quit, `c` cancel selector, Enter/Space play, `x` pause, `i`/`d` adjust speed, `t`/`y` change tracker.

See [architecture](docs/architecture/overview.md) and [ADR 001](docs/adr/0001-foundation.md).