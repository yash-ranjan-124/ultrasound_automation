from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from medvision.domain.enums import StudyModality, StudyType


class StudyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    study_type: StudyType
    modality: StudyModality
    metadata: dict[str, object]
    created_at: datetime
