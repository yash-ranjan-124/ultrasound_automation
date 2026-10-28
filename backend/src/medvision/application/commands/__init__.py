from dataclasses import dataclass
from typing import BinaryIO
from uuid import UUID

from medvision.domain.enums import ObservationSource, StudyModality
from medvision.domain.value_objects import BoundingBox


@dataclass(frozen=True)
class CreateStudyCommand:
    filename: str
    modality: StudyModality
    content_type: str | None
    content: BinaryIO


@dataclass(frozen=True)
class CreateTrackingSessionCommand:
    study_id: UUID


@dataclass(frozen=True)
class StartTrackingCommand:
    session_id: UUID
    tracker_name: str
    start_frame: int
    initial_bounding_box: BoundingBox
    initial_source: ObservationSource = ObservationSource.MANUAL_INITIALIZATION
