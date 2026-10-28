from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from medvision.domain.enums import JobStatus, ObservationSource, StudyModality, StudyType
from medvision.domain.value_objects import BoundingBox


class StudyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    study_type: StudyType
    modality: StudyModality
    metadata: dict[str, object]
    created_at: datetime


class BoundingBoxSchema(BaseModel):
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)
    width: float = Field(gt=0, le=1)
    height: float = Field(gt=0, le=1)

    def to_domain(self) -> BoundingBox:
        return BoundingBox(self.x, self.y, self.width, self.height)


class StartTrackingRequest(BaseModel):
    tracker_name: str = Field(min_length=1)
    start_frame: int = Field(ge=0)
    initial_bounding_box: BoundingBoxSchema
    initial_source: ObservationSource = ObservationSource.MANUAL_INITIALIZATION


class TrackingSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    study_id: UUID
    created_at: datetime


class FrameObservationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    frame_number: int
    bounding_box: BoundingBoxSchema
    source: ObservationSource
    confidence: float | None


class TrackingRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    session_id: UUID
    tracker_name: str
    start_frame: int
    status: JobStatus
    observations: tuple[FrameObservationResponse, ...]
    created_at: datetime
    completed_at: datetime | None
    error_message: str | None
