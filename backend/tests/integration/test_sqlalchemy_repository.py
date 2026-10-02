from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from medvision.domain.entities import ImagingStudy
from medvision.domain.enums import StudyModality, StudyType
from medvision.infrastructure.persistence import (
    Base,
    SqlAlchemyStudyRepository,
    normalize_database_url,
)


def repository_for(tmp_path) -> SqlAlchemyStudyRepository:
    engine = create_engine(f"sqlite:///{tmp_path / 'studies.db'}")
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine, class_=Session)
    return SqlAlchemyStudyRepository(factory)


def make_study() -> ImagingStudy:
    return ImagingStudy(
        id=uuid4(),
        filename="synthetic.nii.gz",
        study_type=StudyType.NIFTI,
        modality=StudyModality.MRI,
        storage_key="studies/generated/source.nii.gz",
        created_at=datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC),
        metadata={"shape": [2, 3, 4], "voxel_spacing": [1.0, 1.0, 2.0]},
    )


def test_sqlalchemy_repository_round_trips_records_across_instances(tmp_path) -> None:
    repository = repository_for(tmp_path)
    study = make_study()
    repository.save(study)

    second_repository = repository_for(tmp_path)
    assert second_repository.get_by_id(study.id) == study
    assert second_repository.list() == [study]


def test_sqlalchemy_repository_updates_and_deletes_records(tmp_path) -> None:
    repository = repository_for(tmp_path)
    study = make_study()
    repository.save(study)
    updated = ImagingStudy(
        id=study.id,
        filename=study.filename,
        study_type=study.study_type,
        modality=StudyModality.CT,
        storage_key=study.storage_key,
        created_at=study.created_at,
        metadata={"shape": [4, 4, 4]},
    )

    repository.save(updated)
    assert repository.get_by_id(study.id) == updated
    repository.delete(study.id)
    repository.delete(study.id)
    assert repository.get_by_id(study.id) is None
    assert repository.list() == []


def test_database_url_uses_psycopg_without_exposing_password() -> None:
    url = normalize_database_url("postgresql://medvision:example-password@localhost/medvision")

    assert url.drivername == "postgresql+psycopg"
    assert url.render_as_string(hide_password=True) == (
        "postgresql+psycopg://medvision:***@localhost/medvision"
    )
