from collections.abc import Iterator
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from medvision.application.commands import (
    CreateTrackingSessionCommand,
    StartTrackingCommand,
)
from medvision.application.services import (
    CreateTrackingSessionService,
    StartTrackingService,
)
from medvision.domain.entities import ImagingStudy
from medvision.domain.enums import (
    JobStatus,
    ObservationSource,
    StudyModality,
    StudyType,
)
from medvision.domain.exceptions import (
    InvalidTrackingStartError,
    InvalidTrackingStudyError,
    TrackingSessionNotFoundError,
)
from medvision.domain.value_objects import (
    BoundingBox,
    TrackingResult,
    VideoFrame,
    VideoMetadata,
)
from medvision.infrastructure.persistence import (
    InMemoryStudyRepository,
    InMemoryTrackingRunRepository,
    InMemoryTrackingSessionRepository,
)


NOW = datetime(2026, 1, 1, tzinfo=UTC)


def make_video_study() -> ImagingStudy:
    return ImagingStudy(
        id=uuid4(),
        filename="synthetic.avi",
        study_type=StudyType.VIDEO,
        modality=StudyModality.ULTRASOUND,
        storage_key="studies/demo/source.avi",
        created_at=NOW,
        metadata={},
    )


class FakeReader:
    def __init__(self, frame_count: int = 4) -> None:
        self.metadata = VideoMetadata(100, 100, 10.0, frame_count, frame_count / 10.0)
        self.closed = False
        self.opened = False

    def open(self, storage_key: str, filename: str) -> None:
        assert storage_key
        assert filename
        self.opened = True

    def get_metadata(self) -> VideoMetadata:
        return self.metadata

    def read_frame(self, frame_number: int) -> VideoFrame:
        return VideoFrame(frame_number, 100, 100, object())

    def iter_frames(self, start_frame: int = 0) -> Iterator[VideoFrame]:
        for frame_number in range(start_frame, self.metadata.frame_count):
            yield VideoFrame(frame_number, 100, 100, object())

    def close(self) -> None:
        self.closed = True


class FakeReaderFactory:
    def __init__(self, reader: FakeReader) -> None:
        self.reader = reader

    def create(self) -> FakeReader:
        return self.reader


class FakeTracker:
    def __init__(self, fail_on_frame: int | None = None, init_error: Exception | None = None) -> None:
        self.fail_on_frame = fail_on_frame
        self.init_error = init_error
        self.initialized = False
        self.reset_called = False

    @property
    def name(self) -> str:
        return "FAKE"

    def initialize(self, frame: VideoFrame, bounding_box: BoundingBox) -> None:
        assert frame.frame_number >= 0
        assert bounding_box.width > 0
        if self.init_error is not None:
            raise self.init_error
        self.initialized = True

    def track(self, frame: VideoFrame) -> TrackingResult:
        assert self.initialized
        if frame.frame_number == self.fail_on_frame:
            return TrackingResult(False, None)
        return TrackingResult(True, BoundingBox(0.1, 0.1, 0.2, 0.2))

    def reset(self) -> None:
        self.reset_called = True


class FakeTrackerFactory:
    def __init__(self, tracker: FakeTracker) -> None:
        self.tracker = tracker

    def create(self, name: str) -> FakeTracker:
        assert name
        return self.tracker


def build_services(frame_count: int = 4, tracker: FakeTracker | None = None):
    studies = InMemoryStudyRepository()
    sessions = InMemoryTrackingSessionRepository()
    runs = InMemoryTrackingRunRepository()
    study = make_video_study()
    studies.save(study)

    session_service = CreateTrackingSessionService(
        studies=studies,
        sessions=sessions,
        clock=lambda: NOW,
    )
    session = session_service.execute(CreateTrackingSessionCommand(study.id))

    reader = FakeReader(frame_count)
    active_tracker = tracker or FakeTracker()
    tracking_service = StartTrackingService(
        studies=studies,
        sessions=sessions,
        runs=runs,
        video_readers=FakeReaderFactory(reader),
        trackers=FakeTrackerFactory(active_tracker),
        clock=lambda: NOW,
    )
    return study, session, runs, reader, active_tracker, tracking_service


def test_create_tracking_session_rejects_non_video_study() -> None:
    studies = InMemoryStudyRepository()
    sessions = InMemoryTrackingSessionRepository()
    study = ImagingStudy(
        id=uuid4(),
        filename="scan.nii.gz",
        study_type=StudyType.NIFTI,
        modality=StudyModality.MRI,
        storage_key="studies/x/source.nii.gz",
        created_at=NOW,
        metadata={},
    )
    studies.save(study)

    with pytest.raises(InvalidTrackingStudyError):
        CreateTrackingSessionService(studies, sessions).execute(
            CreateTrackingSessionCommand(study.id)
        )


def test_tracking_completes_and_preserves_immutable_observations() -> None:
    _, session, runs, reader, tracker, service = build_services()

    result = service.execute(
        StartTrackingCommand(
            session_id=session.id,
            tracker_name="fake",
            start_frame=0,
            initial_bounding_box=BoundingBox(0.1, 0.1, 0.2, 0.2),
        )
    )

    assert result.status is JobStatus.COMPLETED
    assert [item.frame_number for item in result.observations] == [0, 1, 2, 3]
    assert result.observations[0].source is ObservationSource.MANUAL_INITIALIZATION
    assert all(
        item.source is ObservationSource.AUTO_TRACKED
        for item in result.observations[1:]
    )
    assert runs.get_by_id(result.id) is not None
    assert reader.closed is True
    assert tracker.reset_called is True


def test_tracking_can_start_on_last_frame() -> None:
    _, session, _, _, _, service = build_services(frame_count=3)

    result = service.execute(
        StartTrackingCommand(
            session.id,
            "fake",
            2,
            BoundingBox(0.1, 0.1, 0.2, 0.2),
        )
    )

    assert result.status is JobStatus.COMPLETED
    assert [item.frame_number for item in result.observations] == [2]


def test_tracker_loss_returns_failed_run_with_partial_history() -> None:
    tracker = FakeTracker(fail_on_frame=2)
    _, session, runs, _, _, service = build_services(tracker=tracker)

    result = service.execute(
        StartTrackingCommand(
            session.id,
            "fake",
            0,
            BoundingBox(0.1, 0.1, 0.2, 0.2),
        )
    )

    assert result.status is JobStatus.FAILED
    assert [item.frame_number for item in result.observations] == [0, 1]
    assert result.error_message == "Tracker lost target at frame 2"
    persisted = runs.get_by_id(result.id)
    assert persisted is not None
    assert persisted.status is JobStatus.FAILED
    assert persisted.observations == result.observations


def test_invalid_start_frame_does_not_create_run() -> None:
    _, session, runs, reader, tracker, service = build_services(frame_count=3)

    with pytest.raises(InvalidTrackingStartError):
        service.execute(
            StartTrackingCommand(
                session.id,
                "fake",
                3,
                BoundingBox(0.1, 0.1, 0.2, 0.2),
            )
        )

    assert runs.list_by_session(session.id) == []
    assert reader.closed is True
    assert tracker.reset_called is True


def test_missing_session_is_rejected_before_reader_creation() -> None:
    studies = InMemoryStudyRepository()
    sessions = InMemoryTrackingSessionRepository()
    runs = InMemoryTrackingRunRepository()

    service = StartTrackingService(
        studies,
        sessions,
        runs,
        FakeReaderFactory(FakeReader()),
        FakeTrackerFactory(FakeTracker()),
    )

    with pytest.raises(TrackingSessionNotFoundError):
        service.execute(
            StartTrackingCommand(
                uuid4(),
                "fake",
                0,
                BoundingBox(0.1, 0.1, 0.2, 0.2),
            )
        )


def test_initialization_failure_persists_failed_run_then_reraises() -> None:
    tracker = FakeTracker(init_error=RuntimeError("init failed"))
    _, session, runs, reader, _, service = build_services(tracker=tracker)

    with pytest.raises(RuntimeError, match="init failed"):
        service.execute(
            StartTrackingCommand(
                session.id,
                "fake",
                0,
                BoundingBox(0.1, 0.1, 0.2, 0.2),
            )
        )

    saved_runs = runs.list_by_session(session.id)
    assert len(saved_runs) == 1
    assert saved_runs[0].status is JobStatus.FAILED
    assert saved_runs[0].observations == ()
    assert "init failed" in (saved_runs[0].error_message or "")
    assert reader.closed is True


def test_manual_correction_source_is_preserved_for_new_run_segment() -> None:
    _, session, _, _, _, service = build_services(frame_count=2)

    result = service.execute(
        StartTrackingCommand(
            session.id,
            "fake",
            1,
            BoundingBox(0.2, 0.2, 0.2, 0.2),
            initial_source=ObservationSource.MANUAL_CORRECTION,
        )
    )

    assert result.observations[0].source is ObservationSource.MANUAL_CORRECTION
