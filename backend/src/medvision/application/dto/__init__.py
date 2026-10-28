from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from medvision.domain.entities import (
    FrameObservation,
    ImagingStudy,
    TrackingRun,
    TrackingSession,
)
from medvision.domain.enums import JobStatus, StudyModality, StudyType


@dataclass(frozen=True)
class StudyDTO:
    id: UUID
    filename: str
    study_type: StudyType
    modality: StudyModality
    metadata: dict[str, object]
    created_at: datetime

    @classmethod
    def from_entity(cls, study: ImagingStudy) -> "StudyDTO":
        return cls(
            id=study.id,
            filename=study.filename,
            study_type=study.study_type,
            modality=study.modality,
            metadata=dict(study.metadata),
            created_at=study.created_at,
        )


@dataclass(frozen=True)
class TrackingSessionDTO:
    id: UUID
    study_id: UUID
    created_at: datetime

    @classmethod
    def from_entity(cls, session: TrackingSession) -> "TrackingSessionDTO":
        return cls(
            id=session.id,
            study_id=session.study_id,
            created_at=session.created_at,
        )


@dataclass(frozen=True)
class TrackingRunDTO:
    id: UUID
    session_id: UUID
    tracker_name: str
    start_frame: int
    status: JobStatus
    observations: tuple[FrameObservation, ...]
    created_at: datetime
    completed_at: datetime | None
    error_message: str | None

    @classmethod
    def from_entity(cls, run: TrackingRun) -> "TrackingRunDTO":
        return cls(
            id=run.id,
            session_id=run.session_id,
            tracker_name=run.tracker_name,
            start_frame=run.start_frame,
            status=run.status,
            observations=run.observations,
            created_at=run.created_at,
            completed_at=run.completed_at,
            error_message=run.error_message,
        )
