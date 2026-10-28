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


class TrackingSessionNotFoundError(MedVisionDomainError):
    def __init__(self, session_id: object) -> None:
        super().__init__(f"Tracking session not found: {session_id}")
        self.session_id = session_id


class TrackingRunNotFoundError(MedVisionDomainError):
    def __init__(self, run_id: object) -> None:
        super().__init__(f"Tracking run not found: {run_id}")
        self.run_id = run_id


class InvalidTrackingStudyError(MedVisionDomainError):
    """Raised when tracking is requested for a non-video study."""


class InvalidTrackingStartError(MedVisionDomainError):
    """Raised when the requested start frame is invalid for the video."""


class InvalidBoundingBoxError(MedVisionDomainError):
    """Raised when normalized bounding-box coordinates are invalid."""


class StorageError(MedVisionDomainError):
    """Raised when an uploaded source cannot be safely stored."""


class MetadataExtractionError(MedVisionDomainError):
    """Raised when a supported file cannot be read as its declared type."""


class VideoReadError(MedVisionDomainError):
    """Raised when a stored video cannot be opened or decoded reliably."""


class VideoNotOpenError(VideoReadError):
    """Raised when video operations are attempted before opening a source."""


class InvalidVideoFrameError(VideoReadError):
    """Raised when a requested frame number is outside the video bounds."""


class TrackerError(MedVisionDomainError):
    """Base error for object-tracking failures."""


class UnsupportedTrackerError(TrackerError):
    """Raised when the requested tracker name is not registered."""


class TrackerUnavailableError(TrackerError):
    """Raised when a requested tracker is unavailable in the OpenCV build."""


class TrackerInitializationError(TrackerError):
    """Raised when a tracker cannot initialize from the supplied frame and ROI."""


class TrackerNotInitializedError(TrackerError):
    """Raised when tracking is attempted before initialization."""
