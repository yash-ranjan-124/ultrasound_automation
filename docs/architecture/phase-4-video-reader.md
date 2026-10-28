# Phase 4 — Video Reader Infrastructure

## Goal

Provide a reusable, storage-agnostic video access layer for later tracking workflows.

This phase does not implement object tracking, tracking APIs, or frontend video controls.

## TODOs

1. Define `VideoMetadata` and `VideoFrame` framework-free value objects.
   - How: typed immutable dataclasses with validation.
   - Why: application/tracking code should not depend on OpenCV capture internals.

2. Define `VideoReaderPort`.
   - How: inward-facing protocol for open, metadata, random frame reads, sequential iteration, and close.
   - Why: future application services must depend on a stable abstraction, not `cv2.VideoCapture`.

3. Implement `OpenCVVideoReader`.
   - How: obtain the source through `StoragePort`, materialize a temporary local working file, and own the `cv2.VideoCapture` lifecycle.
   - Why: OpenCV expects filesystem-oriented media access while storage may later be local, Replit object storage, or S3-compatible.

4. Support deterministic random access and sequential iteration.
   - How: use `CAP_PROP_POS_FRAMES`, validate frame bounds, and return typed frame records.
   - Why: ROI initialization, tracking restarts, and manual corrections need exact frame addressing.

5. Add explicit video-reader errors.
   - How: dedicated not-open, invalid-frame, and unreadable-video errors.
   - Why: later tracking services need predictable failure semantics.

6. Guarantee resource cleanup.
   - How: idempotent `close()`, capture release, temporary-file deletion, and context-manager support.
   - Why: long-running workers must not leak file descriptors or temporary media.

7. Add synthetic integration tests.
   - How: generate a tiny AVI at test runtime and verify metadata, random reads, iteration, bounds, reopen, and cleanup.
   - Why: reproducible tests without committing binary fixtures.

## Out of scope

- CSRT/KCF tracker adapters
- tracking sessions/services
- tracking REST APIs
- frontend playback/ROI UI
- background jobs
