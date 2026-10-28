class MedVisionDomainError(Exception):
    """Base class for expected application errors."""


class UnsupportedStudyTypeError(MedVisionDomainError):
    def __init__(self, filename: str) -> None:
        super().__init__(f"Unsupported imaging study file: {filename}")
        self.filename = filename


class StudyNotFoundError(MedVisionDomainError):
    def __init__(self, study_id: object) -> None:
        super().__init__(f"Imaging study not found: {study_id}")
        self.study_id = study_id


class InvalidBoundingBoxError(MedVisionDomainError):
    """Raised when normalized bounding-box coordinates are invalid."""


class StorageError(MedVisionDomainError):
    """Raised when an uploaded source cannot be safely stored."""


class MetadataExtractionError(MedVisionDomainError):
    """Raised when a supported file cannot be read as its declared type."""
