from dataclasses import dataclass
from uuid import UUID

from medvision.application.dto import TrackingRunDTO, TrackingSessionDTO
from medvision.domain.exceptions import TrackingRunNotFoundError, TrackingSessionNotFoundError
from medvision.domain.ports import TrackingRunRepository, TrackingSessionRepository


@dataclass
class TrackingCatalogService:
    sessions: TrackingSessionRepository
    runs: TrackingRunRepository

    def get_session(self, session_id: UUID) -> TrackingSessionDTO:
        session = self.sessions.get_by_id(session_id)
        if session is None:
            raise TrackingSessionNotFoundError(session_id)
        return TrackingSessionDTO.from_entity(session)

    def list_sessions(self, study_id: UUID) -> list[TrackingSessionDTO]:
        return [
            TrackingSessionDTO.from_entity(session)
            for session in self.sessions.list_by_study(study_id)
        ]

    def get_run(self, run_id: UUID) -> TrackingRunDTO:
        run = self.runs.get_by_id(run_id)
        if run is None:
            raise TrackingRunNotFoundError(run_id)
        return TrackingRunDTO.from_entity(run)

    def list_runs(self, session_id: UUID) -> list[TrackingRunDTO]:
        if self.sessions.get_by_id(session_id) is None:
            raise TrackingSessionNotFoundError(session_id)
        return [
            TrackingRunDTO.from_entity(run)
            for run in self.runs.list_by_session(session_id)
        ]
