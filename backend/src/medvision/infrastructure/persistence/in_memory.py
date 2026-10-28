from threading import Lock
from uuid import UUID

from medvision.domain.entities import ImagingStudy, TrackingRun, TrackingSession


class InMemoryStudyRepository:
    def __init__(self) -> None:
        self._studies: dict[UUID, ImagingStudy] = {}
        self._lock = Lock()

    def save(self, study: ImagingStudy) -> None:
        with self._lock:
            self._studies[study.id] = study

    def get_by_id(self, study_id: UUID) -> ImagingStudy | None:
        with self._lock:
            return self._studies.get(study_id)

    def list(self) -> list[ImagingStudy]:
        with self._lock:
            return sorted(
                self._studies.values(),
                key=lambda study: study.created_at,
                reverse=True,
            )

    def delete(self, study_id: UUID) -> None:
        with self._lock:
            self._studies.pop(study_id, None)


class InMemoryTrackingSessionRepository:
    def __init__(self) -> None:
        self._sessions: dict[UUID, TrackingSession] = {}
        self._lock = Lock()

    def save(self, session: TrackingSession) -> None:
        with self._lock:
            self._sessions[session.id] = session

    def get_by_id(self, session_id: UUID) -> TrackingSession | None:
        with self._lock:
            return self._sessions.get(session_id)

    def list_by_study(self, study_id: UUID) -> list[TrackingSession]:
        with self._lock:
            return sorted(
                (session for session in self._sessions.values() if session.study_id == study_id),
                key=lambda session: session.created_at,
            )


class InMemoryTrackingRunRepository:
    def __init__(self) -> None:
        self._runs: dict[UUID, TrackingRun] = {}
        self._lock = Lock()

    def save(self, run: TrackingRun) -> None:
        with self._lock:
            self._runs[run.id] = run

    def get_by_id(self, run_id: UUID) -> TrackingRun | None:
        with self._lock:
            return self._runs.get(run_id)

    def list_by_session(self, session_id: UUID) -> list[TrackingRun]:
        with self._lock:
            return sorted(
                (run for run in self._runs.values() if run.session_id == session_id),
                key=lambda run: run.created_at,
            )
