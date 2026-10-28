from collections.abc import Iterator
from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from medvision.config import Settings
from medvision.domain.entities import ImagingStudy
from medvision.domain.enums import StudyModality, StudyType
from medvision.domain.exceptions import UnsupportedTrackerError
from medvision.domain.value_objects import BoundingBox, TrackingResult, VideoFrame, VideoMetadata
from medvision.infrastructure.persistence import (
    InMemoryStudyRepository,
    InMemoryTrackingRunRepository,
    InMemoryTrackingSessionRepository,
)
from medvision.main import create_app


NOW = datetime(2026, 1, 1, tzinfo=UTC)


class FakeReader:
    def open(self, storage_key: str, filename: str) -> None:
        assert storage_key
        assert filename

    def get_metadata(self) -> VideoMetadata:
        return VideoMetadata(100, 100, 10.0, 3, 0.3)

    def read_frame(self, frame_number: int) -> VideoFrame:
        return VideoFrame(frame_number, 100, 100, object())

    def iter_frames(self, start_frame: int = 0) -> Iterator[VideoFrame]:
        for frame_number in range(start_frame, 3):
            yield VideoFrame(frame_number, 100, 100, object())

    def close(self) -> None:
        return None


class FakeReaderFactory:
    def create(self) -> FakeReader:
        return FakeReader()


class FakeTracker:
    @property
    def name(self) -> str:
        return "FAKE"

    def initialize(self, frame: VideoFrame, bounding_box: BoundingBox) -> None:
        assert frame.frame_number >= 0
        assert bounding_box.width > 0

    def track(self, frame: VideoFrame) -> TrackingResult:
        return TrackingResult(True, BoundingBox(0.1, 0.1, 0.2, 0.2))

    def reset(self) -> None:
        return None


class FakeTrackerFactory:
    def create(self, name: str) -> FakeTracker:
        if name.strip().upper() != "FAKE":
            raise UnsupportedTrackerError(name)
        return FakeTracker()


def make_client(tmp_path):
    studies = InMemoryStudyRepository()
    sessions = InMemoryTrackingSessionRepository()
    runs = InMemoryTrackingRunRepository()
    app = create_app(
        Settings(storage_root=tmp_path / "storage"),
        repository=studies,
        tracking_sessions=sessions,
        tracking_runs=runs,
        video_reader_factory=FakeReaderFactory(),
        tracker_factory=FakeTrackerFactory(),
    )
    return TestClient(app), studies


def add_video(studies: InMemoryStudyRepository) -> ImagingStudy:
    study = ImagingStudy(
        id=uuid4(),
        filename="synthetic.avi",
        study_type=StudyType.VIDEO,
        modality=StudyModality.ULTRASOUND,
        storage_key="studies/demo/source.avi",
        created_at=NOW,
        metadata={},
    )
    studies.save(study)
    return study


def test_tracking_session_and_run_api_flow(tmp_path) -> None:
    client, studies = make_client(tmp_path)
    study = add_video(studies)

    create_session = client.post(f"/api/v1/studies/{study.id}/tracking-sessions")
    assert create_session.status_code == 201
    session = create_session.json()
    assert session["study_id"] == str(study.id)

    assert client.get(f"/api/v1/studies/{study.id}/tracking-sessions").json() == [session]
    assert client.get(f"/api/v1/tracking-sessions/{session['id']}").json() == session

    start = client.post(
        f"/api/v1/tracking-sessions/{session['id']}/runs",
        json={
            "tracker_name": "FAKE",
            "start_frame": 0,
            "initial_bounding_box": {
                "x": 0.1,
                "y": 0.1,
                "width": 0.2,
                "height": 0.2,
            },
        },
    )
    assert start.status_code == 201
    run = start.json()
    assert run["status"] == "COMPLETED"
    assert [item["frame_number"] for item in run["observations"]] == [0, 1, 2]

    assert client.get(
        f"/api/v1/tracking-sessions/{session['id']}/runs"
    ).json() == [run]
    assert client.get(f"/api/v1/tracking-runs/{run['id']}").json() == run


def test_create_tracking_session_rejects_non_video_study(tmp_path) -> None:
    client, studies = make_client(tmp_path)
    study = ImagingStudy(
        id=uuid4(),
        filename="brain.nii.gz",
        study_type=StudyType.NIFTI,
        modality=StudyModality.MRI,
        storage_key="studies/demo/source.nii.gz",
        created_at=NOW,
        metadata={},
    )
    studies.save(study)

    response = client.post(f"/api/v1/studies/{study.id}/tracking-sessions")

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_TRACKING_STUDY"


def test_tracking_api_returns_stable_not_found_errors(tmp_path) -> None:
    client, _ = make_client(tmp_path)

    session_response = client.get(f"/api/v1/tracking-sessions/{uuid4()}")
    run_response = client.get(f"/api/v1/tracking-runs/{uuid4()}")

    assert session_response.status_code == 404
    assert session_response.json()["error"]["code"] == "TRACKING_SESSION_NOT_FOUND"
    assert run_response.status_code == 404
    assert run_response.json()["error"]["code"] == "TRACKING_RUN_NOT_FOUND"


def test_tracking_api_rejects_unsupported_tracker(tmp_path) -> None:
    client, studies = make_client(tmp_path)
    study = add_video(studies)
    session = client.post(
        f"/api/v1/studies/{study.id}/tracking-sessions"
    ).json()

    response = client.post(
        f"/api/v1/tracking-sessions/{session['id']}/runs",
        json={
            "tracker_name": "MOSSE",
            "start_frame": 0,
            "initial_bounding_box": {
                "x": 0.1,
                "y": 0.1,
                "width": 0.2,
                "height": 0.2,
            },
        },
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "UNSUPPORTED_TRACKER"


def test_tracking_api_validates_bounding_box_shape(tmp_path) -> None:
    client, studies = make_client(tmp_path)
    study = add_video(studies)
    session = client.post(
        f"/api/v1/studies/{study.id}/tracking-sessions"
    ).json()

    response = client.post(
        f"/api/v1/tracking-sessions/{session['id']}/runs",
        json={
            "tracker_name": "FAKE",
            "start_frame": 0,
            "initial_bounding_box": {
                "x": 0.9,
                "y": 0.1,
                "width": 0.2,
                "height": 0.2,
            },
        },
    )

    assert response.status_code in {400, 422}
