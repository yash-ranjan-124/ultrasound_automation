from dataclasses import dataclass

import pytest

from medvision.domain.exceptions import (
    TrackerNotInitializedError,
    UnsupportedTrackerError,
)
from medvision.domain.ports import ObjectTracker
from medvision.domain.value_objects import BoundingBox, TrackingResult, VideoFrame
from medvision.infrastructure.tracking import OpenCVCSRTTracker, TrackerRegistry


def test_tracking_result_invariants() -> None:
    box = BoundingBox(0.1, 0.1, 0.2, 0.2)
    assert TrackingResult(True, box).bounding_box == box
    assert TrackingResult(False, None).bounding_box is None

    with pytest.raises(ValueError):
        TrackingResult(True, None)
    with pytest.raises(ValueError):
        TrackingResult(False, box)
    with pytest.raises(ValueError):
        TrackingResult(True, box, confidence=1.5)


@dataclass
class FakeTracker:
    tracker_name: str = "FAKE"

    @property
    def name(self) -> str:
        return self.tracker_name

    def initialize(self, frame: VideoFrame, bounding_box: BoundingBox) -> None:
        del frame, bounding_box

    def track(self, frame: VideoFrame) -> TrackingResult:
        del frame
        return TrackingResult(False, None)

    def reset(self) -> None:
        return None


def test_tracker_registry_is_case_insensitive_and_reports_supported_names() -> None:
    registry = TrackerRegistry({"fake": FakeTracker})

    tracker = registry.create("  FaKe  ")

    assert isinstance(tracker, FakeTracker)
    assert registry.supported_names() == ("FAKE",)


def test_tracker_registry_rejects_unknown_tracker() -> None:
    registry = TrackerRegistry({"CSRT": OpenCVCSRTTracker})

    with pytest.raises(UnsupportedTrackerError, match="KCF"):
        registry.create("KCF")


def test_opencv_tracker_requires_initialization() -> None:
    frame = VideoFrame(0, 20, 20, object())
    tracker: ObjectTracker = OpenCVCSRTTracker(factory=lambda: object())

    with pytest.raises(TrackerNotInitializedError):
        tracker.track(frame)
