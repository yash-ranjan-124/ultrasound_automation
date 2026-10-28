# Phase 7 — Tracking REST API

## Goal

Expose the tracking orchestration layer through versioned HTTP endpoints while preserving clean architecture boundaries.

## Endpoints

- `POST /api/v1/studies/{study_id}/tracking-sessions`
- `GET /api/v1/studies/{study_id}/tracking-sessions`
- `GET /api/v1/tracking-sessions/{session_id}`
- `POST /api/v1/tracking-sessions/{session_id}/runs`
- `GET /api/v1/tracking-sessions/{session_id}/runs`
- `GET /api/v1/tracking-runs/{run_id}`

## Design

The FastAPI router only translates HTTP requests into application commands and DTO responses.

```
HTTP
 |
 v
FastAPI router
 |
 v
application services
 |
 +--> repositories
 +--> VideoReaderFactory
 +--> TrackerFactory
```

OpenCV and persistence details remain outside the API layer.

## Validation

- tracking is restricted to video studies
- start frame must be within video bounds
- bounding boxes use normalized coordinates
- only manual initialization/correction may be supplied as the initial observation source
- unsupported trackers return a stable 400 error
- unavailable OpenCV trackers return 503
- missing studies/sessions/runs return stable 404 envelopes

## Persistence limitation

Tracking sessions and runs are currently wired to in-memory repositories.

Study metadata remains PostgreSQL-backed in the default application wiring.

Tracking history therefore resets when the API process restarts. PostgreSQL tracking tables and migrations belong to the next persistence phase.

## Out of scope

- asynchronous/background tracking
- SSE progress
- cancellation
- PostgreSQL tracking persistence
- browser video playback
- ROI drawing
- result overlay UI
