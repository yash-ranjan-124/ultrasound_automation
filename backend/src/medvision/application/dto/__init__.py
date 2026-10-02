from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from medvision.domain.entities import ImagingStudy
from medvision.domain.enums import StudyModality, StudyType


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
