from dataclasses import dataclass
from uuid import UUID

from medvision.application.dto import StudyDTO
from medvision.domain.exceptions import StudyNotFoundError
from medvision.domain.ports import StudyRepository


@dataclass
class StudyCatalogService:
    repository: StudyRepository

    def list(self) -> list[StudyDTO]:
        return [StudyDTO.from_entity(study) for study in self.repository.list()]

    def get(self, study_id: UUID) -> StudyDTO:
        study = self.repository.get_by_id(study_id)
        if study is None:
            raise StudyNotFoundError(study_id)
        return StudyDTO.from_entity(study)
