# ADR 001: Keep the imported desktop prototype separate

**Status:** Accepted for the initial architecture phase.

The original OpenCV/PyQt scripts and sample videos are retained at repository root. The new browser application lives in `backend/` and `frontend/`. This avoids silently rewriting working research scripts while establishing a clean, independently testable modular-monolith boundary.

No database schema or inference/tracking runner is created until the phase implementing those workflows. Health and overview are functional today; planned workflows are explicitly labelled unavailable.