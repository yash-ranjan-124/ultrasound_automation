# MedVision AI Lab contributor contract

- This is a research/education/portfolio application, not a clinical diagnostic tool. Label any future model outputs as experimental research predictions requiring expert review; never assert disease diagnosis.
- Work in requested phases only. Read this file and existing code before editing; do not implement later phases speculatively.
- Keep a modular monolith: API -> application -> domain. Infrastructure implements inward-facing ports. Domain must not import web, ORM, imaging, or model frameworks.
- Use Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, PostgreSQL, uv/pyproject.toml; React, TypeScript, Vite, React Router, TanStack Query, Tailwind CSS. No requirements.txt.
- Never log patient identifiers, patient metadata, uploaded file contents, or raw medical images. Use synthetic demo data. No authentication, external queues, paid APIs, microservices, or clinical claims without a separately requested phase.
- Version HTTP routes under `/api/v1/` and return consistent JSON errors. Store large medical files outside PostgreSQL.
- For each phase: add focused tests; run backend lint, format check, mypy, pytest and frontend lint, test, build where applicable. Document remaining limitations and stop.
- Legacy root Python scripts and sample videos are retained as imported reference material; do not silently delete or restructure them.