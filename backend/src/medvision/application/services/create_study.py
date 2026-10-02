from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import PurePosixPath
from uuid import UUID, uuid4

from medvision.application.commands import CreateStudyCommand
from medvision.application.dto import StudyDTO
from medvision.domain.entities import ImagingStudy
from medvision.domain.enums import StudyType
from medvision.domain.exceptions import UnsupportedStudyTypeError
from medvision.domain.ports import StoragePort, StudyMetadataReader, StudyRepository


class StudyTypeResolver:
    _extensions: tuple[tuple[str, StudyType], ...] = (
        (".nii.gz", StudyType.NIFTI),
        (".mp4", StudyType.VIDEO),
        (".avi", StudyType.VIDEO),
        (".nii", StudyType.NIFTI),
        (".dcm", StudyType.DICOM),
        (".png", StudyType.IMAGE),
        (".jpg", StudyType.IMAGE),
        (".jpeg", StudyType.IMAGE),
    )

    def resolve(self, filename: str) -> StudyType:
        normalized = filename.replace("\\", "/").lower()
        for extension, study_type in self._extensions:
            if normalized.endswith(extension):
                return study_type
        raise UnsupportedStudyTypeError(filename)

    def storage_suffix(self, filename: str, study_type: StudyType) -> str:
        normalized = filename.replace("\\", "/").lower()
        for extension, candidate_type in self._extensions:
            if candidate_type is study_type and normalized.endswith(extension):
                return extension
        raise UnsupportedStudyTypeError(filename)


def _safe_filename(filename: str) -> str:
    if not filename or "\x00" in filename:
        raise UnsupportedStudyTypeError(filename)
    basename = PurePosixPath(filename.replace("\\", "/")).name
    if basename in {"", ".", ".."}:
        raise UnsupportedStudyTypeError(filename)
    return basename


@dataclass
class CreateStudyService:
    storage: StoragePort
    repository: StudyRepository
    metadata_reader: StudyMetadataReader
    resolver: StudyTypeResolver
    id_factory: Callable[[], UUID] = uuid4
    clock: Callable[[], datetime] = lambda: datetime.now(UTC)

    def execute(self, command: CreateStudyCommand) -> StudyDTO:
        filename = _safe_filename(command.filename)
        study_type = self.resolver.resolve(filename)
        study_id = self.id_factory()
        storage_key = (
            f"studies/{study_id}/source{self.resolver.storage_suffix(filename, study_type)}"
        )
        stored = False
        try:
            self.storage.save(storage_key, command.content)
            stored = True
            metadata = self.metadata_reader.extract(study_type, storage_key)
            study = ImagingStudy(
                id=study_id,
                filename=filename,
                study_type=study_type,
                modality=command.modality,
                storage_key=storage_key,
                created_at=self.clock(),
                metadata=metadata,
            )
            self.repository.save(study)
            return StudyDTO.from_entity(study)
        except Exception:
            if stored:
                self.storage.delete(storage_key)
            raise
