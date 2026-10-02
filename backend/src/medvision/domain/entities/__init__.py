from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from medvision.domain.enums import (
    JobStatus,
    ModelStatus,
    ObservationSource,
    StudyModality,
    StudyType,
)
from medvision.domain.value_objects import BoundingBox


@dataclass(frozen=True)
class ImagingStudy:
    id: UUID
    filename: str
    study_type: StudyType
    modality: StudyModality
    storage_key: str
    created_at: datetime
    metadata: dict[str, object]

    @property
    def type(self) -> StudyType:
        """Compatibility alias for the original foundation entity contract."""
        return self.study_type


@dataclass(frozen=True)
class FrameObservation:
    frame_number: int
    bounding_box: BoundingBox
    source: ObservationSource
    confidence: float | None = None

    def __post_init__(self) -> None:
        if self.frame_number < 0:
            raise ValueError("Frame number cannot be negative")
        if self.confidence is not None and not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between zero and one")


@dataclass(frozen=True)
class TrackingRun:
    id: UUID
    study_id: UUID
    algorithm: str
    observations: tuple[FrameObservation, ...]
    created_at: datetime


@dataclass(frozen=True)
class ModelManifest:
    model_id: str
    display_name: str
    version: str
    source_type: str
    framework: str
    task_type: str
    supported_modalities: tuple[StudyModality, ...]
    anatomy: str
    input_dimensionality: str
    preprocessing_profile: str
    output_type: str
    intended_use: str
    status: ModelStatus = ModelStatus.EXPERIMENTAL


@dataclass(frozen=True)
class InferenceRun:
    id: UUID
    study_id: UUID
    use_case_id: str
    model_id: str
    model_version: str
    preprocessing_version: str
    started_at: datetime | None
    completed_at: datetime | None
    status: JobStatus
    result: object | None
    error_details: str | None
    model_hash: str | None
