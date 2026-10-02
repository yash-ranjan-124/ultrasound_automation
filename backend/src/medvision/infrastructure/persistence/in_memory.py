from threading import Lock
from uuid import UUID

from medvision.domain.entities import ImagingStudy


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
            return sorted(self._studies.values(), key=lambda study: study.created_at, reverse=True)

    def delete(self, study_id: UUID) -> None:
        with self._lock:
            self._studies.pop(study_id, None)
