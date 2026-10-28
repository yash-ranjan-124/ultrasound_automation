# Phase 5 — Tracker Strategy

## Goal

Introduce interchangeable object-tracking strategies behind a typed application-facing contract.

This phase deliberately stops before tracking orchestration, persistence, REST APIs, and browser ROI workflows.

## TODOs

1. Replace the loose `object -> object` tracker protocol with typed `VideoFrame`, `BoundingBox`, and `TrackingResult` contracts.
   - How: define an immutable result value object and update `ObjectTracker`.
   - Why: Phase 6 should compile against explicit semantics rather than OpenCV-shaped values.

2. Add explicit tracker errors.
   - How: define unsupported-tracker, initialization, and lifecycle errors.
   - Why: application services need predictable failures without interpreting OpenCV behavior.

3. Implement CSRT and KCF adapters.
   - How: confine OpenCV constructors, `init`, and `update` inside infrastructure.
   - Why: algorithm/library details must not leak into domain or application code.

4. Convert normalized bounding boxes only at the adapter boundary.
   - How: use `BoundingBox.to_pixels()` on initialization and `BoundingBox.from_pixels()` on updates.
   - Why: domain/history remain resolution independent.

5. Add an OpenCV compatibility shim.
   - How: resolve constructors from modern `cv2` first and `cv2.legacy` second.
   - Why: tracker placement differs across OpenCV builds.

6. Add `TrackerRegistry`.
   - How: centralize supported names and factories.
   - Why: later API/application code selects strategies without constructor conditionals.

7. Add synthetic integration tests.
   - How: generate high-contrast moving rectangles in memory.
   - Why: verify real tracker smoke behavior without relying on repository sample videos.

## Out of scope

- TrackingSession/TrackingRun repositories
- StartTrackingService
- manual correction/retracking
- REST endpoints
- background jobs
- frontend ROI and overlay UI
