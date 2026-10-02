from datetime import UTC
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from medvision.domain.entities import ImagingStudy
from medvision.domain.enums import StudyModality, StudyType
from medvision.infrastructure.persistence.models import StudyRecord


class SqlAlchemyStudyRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def save(self, study: ImagingStudy) -> None:
        with self._session_factory.begin() as session:
            record = session.get(StudyRecord, study.id)
            if record is None:
                record = StudyRecord(id=study.id)
                session.add(record)
            record.filename = study.filename
            record.study_type = study.study_type.value
            record.modality = study.modality.value
            record.storage_key = study.storage_key
            record.created_at = study.created_at
            record.study_metadata = study.metadata

    def get_by_id(self, study_id: UUID) -> ImagingStudy | None:
        with self._session_factory() as session:
            record = session.get(StudyRecord, study_id)
            return self._to_entity(record) if record is not None else None

    def list(self) -> list[ImagingStudy]:
        with self._session_factory() as session:
            records = session.scalars(
                select(StudyRecord).order_by(StudyRecord.created_at.desc(), StudyRecord.id)
            )
            return [self._to_entity(record) for record in records]

    def delete(self, study_id: UUID) -> None:
        with self._session_factory.begin() as session:
            record = session.get(StudyRecord, study_id)
            if record is not None:
                session.delete(record)

    @staticmethod
    def _to_entity(record: StudyRecord) -> ImagingStudy:
        created_at = record.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=UTC)
        return ImagingStudy(
            id=record.id,
            filename=record.filename,
            study_type=StudyType(record.study_type),
            modality=StudyModality(record.modality),
            storage_key=record.storage_key,
            created_at=created_at,
            metadata=record.study_metadata,
        )
