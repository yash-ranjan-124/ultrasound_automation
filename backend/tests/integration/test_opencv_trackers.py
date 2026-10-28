import cv2
import numpy as np
import pytest

from medvision.domain.exceptions import (
    TrackerInitializationError,
    TrackerNotInitializedError,
)
from medvision.domain.value_objects import BoundingBox, VideoFrame
from medvision.infrastructure.tracking import OpenCVCSRTTracker, OpenCVKCFTracker


class StubTracker:
    def __init__(
        self,
        *,
        init_result: bool | None = None,
        update_result: tuple[bool, tuple[float, float, float, float]] = (
            True,
            (20.0, 10.0, 40.0, 30.0),
        ),
    ) -> None:
        self.init_result = init_result
        self.update_result = update_result
        self.initial_box: tuple[int, int, int, int] | None = None

    def init(self, _pixels: object, box: tuple[int, int, int, int]) -> bool | None:
        self.initial_box = box
        return self.init_result

    def update(self, _pixels: object) -> tuple[bool, tuple[float, float, float, float]]:
        return self.update_result


def make_frame(frame_number: int = 0) -> VideoFrame:
    pixels = np.zeros((100, 200, 3), dtype=np.uint8)
    cv2.rectangle(pixels, (20, 10), (60, 40), (255, 255, 255), -1)
    return VideoFrame(
        frame_number=frame_number,
        width=200,
        height=100,
        pixels=pixels,
    )


def test_adapter_converts_normalized_roi_to_pixels_and_back() -> None:
    stub = StubTracker()
    tracker = OpenCVCSRTTracker(factory=lambda: stub)
    frame = make_frame()

    tracker.initialize(frame, BoundingBox(0.1, 0.1, 0.2, 0.3))
    result = tracker.track(frame)

    assert stub.initial_box == (20, 10, 40, 30)
    assert result.success is True
    assert result.bounding_box == BoundingBox(0.1, 0.1, 0.2, 0.3)
    assert result.confidence is None


def test_adapter_accepts_opencv_none_init_result_as_success() -> None:
    stub = StubTracker(init_result=None)
    tracker = OpenCVCSRTTracker(factory=lambda: stub)

    tracker.initialize(make_frame(), BoundingBox(0.1, 0.1, 0.2, 0.3))

    assert tracker.track(make_frame(1)).success is True


def test_failed_reinitialization_clears_previous_tracker_state() -> None:
    healthy = StubTracker()
    failing = StubTracker(init_result=False)
    factories = iter((healthy, failing))
    tracker = OpenCVCSRTTracker(factory=lambda: next(factories))
    frame = make_frame()

    tracker.initialize(frame, BoundingBox(0.1, 0.1, 0.2, 0.3))
    with pytest.raises(TrackerInitializationError):
        tracker.initialize(frame, BoundingBox(0.1, 0.1, 0.2, 0.3))

    with pytest.raises(TrackerNotInitializedError):
        tracker.track(frame)


def test_failed_update_returns_failed_result_without_invented_confidence() -> None:
    stub = StubTracker(update_result=(False, (0.0, 0.0, 0.0, 0.0)))
    tracker = OpenCVCSRTTracker(factory=lambda: stub)
    frame = make_frame()
    tracker.initialize(frame, BoundingBox(0.1, 0.1, 0.2, 0.3))

    result = tracker.track(frame)

    assert result.success is False
    assert result.bounding_box is None
    assert result.confidence is None


def test_tracker_clips_out_of_frame_opencv_box_to_normalized_domain() -> None:
    stub = StubTracker(update_result=(True, (-5.0, -5.0, 30.0, 30.0)))
    tracker = OpenCVCSRTTracker(factory=lambda: stub)
    frame = make_frame()
    tracker.initialize(frame, BoundingBox(0.1, 0.1, 0.2, 0.3))

    result = tracker.track(frame)

    assert result.success is True
    assert result.bounding_box == BoundingBox(0.0, 0.0, 0.125, 0.25)


@pytest.mark.parametrize("tracker_type", [OpenCVCSRTTracker, OpenCVKCFTracker])
def test_real_opencv_tracker_smoke_on_static_high_contrast_object(tracker_type) -> None:
    frame = make_frame()
    tracker = tracker_type()
    tracker.initialize(frame, BoundingBox(0.1, 0.1, 0.2, 0.3))

    result = tracker.track(make_frame(1))

    assert result.success is True
    assert result.bounding_box is not None
    assert 0 <= result.bounding_box.x <= 1
    assert 0 <= result.bounding_box.y <= 1
