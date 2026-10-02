# MedVision AI Lab

A browser-based foundation for a medical-imaging **research and education** workstation. This project is **not intended for clinical diagnosis**. Model predictions, when implemented in later phases, must be treated as experimental outputs requiring expert review.

## Current phase: study ingestion

The app supports uploading and registering MP4/AVI videos, NIfTI `.nii`/`.nii.gz` volumes, DICOM `.dcm` files, and PNG/JPG/JPEG images. Uploads require an explicit modality (`ULTRASOUND`, `MRI`, `CT`, `XRAY`, or `UNKNOWN`) and are available through:

- `POST /api/v1/studies` — multipart form fields `file` and `modality`
- `GET /api/v1/studies` — list studies
- `GET /api/v1/studies/{study_id}` — fetch one study

Technical metadata is extracted for supported files. DICOM responses use an allowlist of technical fields and omit patient identity fields. Uploaded content is written to local storage under generated study IDs; user-provided filenames are metadata only.

Study records and extracted metadata are stored in PostgreSQL; uploaded files remain in local storage. Configure `DATABASE_URL` and run `cd backend && uv run --locked --no-sync alembic upgrade head` against the development database before using the study endpoints. On Replit, Publish manages the production schema from the development schema. Set `STORAGE_ROOT` to change the local file-storage directory (default: `data/storage` relative to the backend working directory). Study viewing, tracking, inference, model registry, jobs, and export are not implemented yet. The overview marks workflows as planned and does not simulate results.

## Run on Replit

The configured workflows start the FastAPI backend on port 8000 and the Vite frontend on port 5000. Open the web preview to view the frontend. Its `/api` requests proxy to the backend.

Frontend setup from the repository root:

```sh
cd frontend && npm ci
```

In Replit, Python dependencies are managed from the project manifests. The Python package environment is shared with the imported root prototype, so use `uv run --locked --no-sync` rather than `uv sync` there; a sync from the backend can remove packages used only by the prototype. Outside Replit, use `uv sync --locked` in an isolated backend environment.

In separate terminals:

```sh
cd backend && uv run --locked --no-sync uvicorn medvision.main:app --host 0.0.0.0 --port 8000
cd frontend && npm run dev -- --host 0.0.0.0 --port 5000
```

`DATABASE_URL` must point to PostgreSQL. Apply the development migration with `cd backend && uv run --locked --no-sync alembic upgrade head` before using study endpoints. The Replit post-merge setup does this for development; Publish manages the production schema. Check API health at `GET /api/v1/health`.

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