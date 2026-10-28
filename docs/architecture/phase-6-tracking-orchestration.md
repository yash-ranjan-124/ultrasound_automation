# Phase 6 — Tracking Orchestration

## Goal

Turn the Phase 4 video reader and Phase 5 tracker strategies into application-level tracking workflows without exposing OpenCV or storage details to the application layer.

## TODOs

1. Model run lifecycle explicitly.
   - How: enrich `TrackingRun` with tracker name, start frame, status, completion time, failure reason, and immutable observations.
   - Why: every run must be reproducible and inspectable after success or failure.

2. Add session/run repository ports.
   - How: application-facing `TrackingSessionRepository` and `TrackingRunRepository`, with in-memory adapters for this phase.
   - Why: orchestration must not depend on SQLAlchemy or database schemas.

3. Add factory ports.
   - How: `VideoReaderFactoryPort` and `TrackerFactoryPort`.
   - Why: the application must not import `OpenCVVideoReader` or `TrackerRegistry`.

4. Implement `CreateTrackingSessionService`.
   - How: validate that the study exists and is a VIDEO, then create an immutable session.
   - Why: a tracking session is the stable parent for multiple future runs/retracks.

5. Implement `StartTrackingService`.
   - How: resolve session/study, validate start frame, open video, initialize tracker from the initial ROI, create the initial observation, then iterate remaining frames.
   - Why: this is the core business orchestration previously embedded inside the legacy OpenCV script.

6. Define tracker-loss semantics.
   - How: stop at the first failed update, persist a FAILED run, preserve all observations collected before failure, and record a safe failure reason.
   - Why: partial history is useful for replay/debugging and must not be discarded.

7. Preserve provenance.
   - How: initial ROI observation uses `MANUAL_INITIALIZATION`; future manual correction will create a separate immutable run segment rather than overwrite history.
   - Why: tracking history must remain auditable.

8. Add deterministic service tests with fakes.
   - How: fake video readers, tracker factory, and repositories; no OpenCV dependency in application tests.
   - Why: business logic should be fast and stable to test.

## Out of scope

- SQLAlchemy tracking tables
- REST endpoints
- background jobs / SSE
- frontend ROI selection
- manual correction API
- annotated video export
