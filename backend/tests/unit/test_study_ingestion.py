from io import BytesIO
from uuid import UUID, uuid4

import pytest

from medvision.application.commands import CreateStudyCommand
from medvision.application.services import CreateStudyService, StudyTypeResolver
from medvision.domain.enums import StudyModality, StudyType
from medvision.domain.exceptions import MetadataExtractionError, UnsupportedStudyTypeError
from medvision.infrastructure.persistence import InMemoryStudyRepository


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        ("movie.mp4", StudyType.VIDEO),
        ("MOVIE.MP4", StudyType.VIDEO),
        ("scan.avi", StudyType.VIDEO),
        ("brain.nii", StudyType.NIFTI),
        ("brain.nii.gz", StudyType.NIFTI),
        ("BRAIN.NII.GZ", StudyType.NIFTI),
        ("scan.dcm", StudyType.DICOM),
        ("SCAN.DCM", StudyType.DICOM),
        ("image.png", StudyType.IMAGE),
        ("image.jpg", StudyType.IMAGE),
        ("image.jpeg", StudyType.IMAGE),
    ],
)
def test_study_type_resolver(filename: str, expected: StudyType) -> None:
    assert StudyTypeResolver().resolve(filename) is expected


@pytest.mark.parametrize("filename", ["malware.exe", "no-extension", "", "../../"])
def test_study_type_resolver_rejects_unsupported_names(filename: str) -> None:
    with pytest.raises(UnsupportedStudyTypeError):
        StudyTypeResolver().resolve(filename)


class FakeStorage:
    def __init__(self) -> None:
        self.files: dict[str, bytes] = {}
        self.deleted: list[str] = []
        self.fail = False

    def save(self, key: str, content: BytesIO) -> None:
        if self.fail:
            raise OSError("storage unavailable")
        content.seek(0)
        self.files[key] = content.read()

    def open(self, key: str) -> BytesIO:
        return BytesIO(self.files[key])

    def delete(self, key: str) -> None:
        self.deleted.append(key)
        self.files.pop(key, None)

    def exists(self, key: str) -> bool:
        return key in self.files


class FakeMetadataReader:
    def __init__(self) -> None:
        self.result: dict[str, object] = {"width": 10, "height": 8}
        self.fail = False
        self.seen_type: StudyType | None = None

    def extract(self, study_type: StudyType, _storage_key: str) -> dict[str, object]:
        self.seen_type = study_type
        if self.fail:
            raise MetadataExtractionError("invalid study")
        return self.result


def make_service() -> tuple[
    CreateStudyService, FakeStorage, InMemoryStudyRepository, FakeMetadataReader
]:
    storage = FakeStorage()
    repository = InMemoryStudyRepository()
    metadata = FakeMetadataReader()
    service = CreateStudyService(storage, repository, metadata, StudyTypeResolver())
    return service, storage, repository, metadata


def test_create_study_registers_metadata_and_keeps_user_filename_out_of_storage_key() -> None:
    service, storage, repository, metadata = make_service()
    study = service.execute(
        CreateStudyCommand(
            filename="../../etc/passwd.png",
            modality=StudyModality.MRI,
            content_type="image/png",
            content=BytesIO(b"synthetic image"),
        )
    )

    assert study.filename == "passwd.png"
    assert study.study_type is StudyType.IMAGE
    assert study.modality is StudyModality.MRI
    assert study.metadata == {"width": 10, "height": 8}
    assert metadata.seen_type is StudyType.IMAGE
    storage_key = f"studies/{study.id}/source.png"
    assert list(storage.files) == [storage_key]
    assert ".." not in storage_key
    assert storage.exists(storage_key)
    assert repository.get_by_id(study.id) is not None


def test_create_study_uses_generated_uuid_and_preserves_gz_extension() -> None:
    study_id = uuid4()
    storage = FakeStorage()
    repository = InMemoryStudyRepository()
    service = CreateStudyService(
        storage,
        repository,
        FakeMetadataReader(),
        StudyTypeResolver(),
        id_factory=lambda: study_id,
    )

    study = service.execute(
        CreateStudyCommand("brain.nii.gz", StudyModality.MRI, None, BytesIO(b"synthetic NIfTI"))
    )

    assert study.id == study_id
    assert list(storage.files) == [f"studies/{study_id}/source.nii.gz"]
    assert study.study_type is StudyType.NIFTI


def test_unsupported_extension_does_not_store_or_register() -> None:
    service, storage, repository, _ = make_service()
    with pytest.raises(UnsupportedStudyTypeError):
        service.execute(
            CreateStudyCommand("payload.exe", StudyModality.UNKNOWN, None, BytesIO(b"no"))
        )
    assert storage.files == {}
    assert repository.list() == []


def test_storage_failure_does_not_persist_study() -> None:
    service, storage, repository, _ = make_service()
    storage.fail = True
    with pytest.raises(OSError):
        service.execute(
            CreateStudyCommand("image.png", StudyModality.UNKNOWN, None, BytesIO(b"data"))
        )
    assert repository.list() == []


def test_metadata_failure_compensates_by_deleting_uploaded_file() -> None:
    service, storage, repository, metadata = make_service()
    metadata.fail = True
    with pytest.raises(MetadataExtractionError):
        service.execute(
            CreateStudyCommand("image.png", StudyModality.UNKNOWN, None, BytesIO(b"data"))
        )
    assert len(storage.deleted) == 1
    assert storage.files == {}
    assert repository.list() == []


def test_in_memory_repository_get_list_delete() -> None:
    service, _, repository, _ = make_service()
    study = service.execute(
        CreateStudyCommand("image.png", StudyModality.CT, None, BytesIO(b"data"))
    )
    assert repository.get_by_id(UUID(str(study.id))) is not None
    assert [item.id for item in repository.list()] == [study.id]
    repository.delete(study.id)
    assert repository.get_by_id(study.id) is None
    assert repository.list() == []


def test_filename_is_metadata_only_and_path_is_reduced_to_basename() -> None:
    service, storage, _, _ = make_service()
    study = service.execute(
        CreateStudyCommand(r"..\..\tmp\secret.jpg", StudyModality.UNKNOWN, None, BytesIO(b"data"))
    )
    assert study.filename == "secret.jpg"
    assert all("secret.jpg" not in key for key in storage.files)
