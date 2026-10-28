from __future__ import annotations

from collections.abc import Callable
from typing import Any, cast

import cv2

from medvision.domain.exceptions import (
    TrackerInitializationError,
    TrackerNotInitializedError,
    TrackerUnavailableError,
)
from medvision.domain.value_objects import BoundingBox, TrackingResult, VideoFrame

TrackerFactory = Callable[[], Any]


def _resolve_constructor(name: str) -> TrackerFactory:
    constructor_name = f"Tracker{name}_create"
    constructor = getattr(cv2, constructor_name, None)
    if callable(constructor):
        return cast(TrackerFactory, constructor)

    legacy = getattr(cv2, "legacy", None)
    legacy_constructor = getattr(legacy, constructor_name, None) if legacy is not None else None
    if callable(legacy_constructor):
        return cast(TrackerFactory, legacy_constructor)

    raise TrackerUnavailableError(
        f"OpenCV tracker {name} is unavailable in the installed OpenCV build"
    )


class _OpenCVTracker:
    tracker_name: str

    def __init__(self, factory: TrackerFactory | None = None) -> None:
        self._factory = factory
        self._tracker: Any | None = None

    @property
    def name(self) -> str:
        return self.tracker_name

    def initialize(self, frame: VideoFrame, bounding_box: BoundingBox) -> None:
        self._tracker = None
        tracker = self._create_tracker()
        pixel_box = bounding_box.to_pixels(frame.width, frame.height)

        try:
            result = tracker.init(frame.pixels, pixel_box)
        except Exception as exc:
            raise TrackerInitializationError(
                f"{self.name} tracker failed to initialize"
            ) from exc

        if result is False:
            raise TrackerInitializationError(
                f"{self.name} tracker rejected the initial bounding box"
            )

        self._tracker = tracker

    def track(self, frame: VideoFrame) -> TrackingResult:
        if self._tracker is None:
            raise TrackerNotInitializedError(
                f"{self.name} tracker must be initialized before tracking"
            )

        try:
            success, pixel_box = self._tracker.update(frame.pixels)
        except Exception:
            return TrackingResult(success=False, bounding_box=None, confidence=None)

        if not success:
            return TrackingResult(success=False, bounding_box=None, confidence=None)

        normalized_box = self._normalize_box(pixel_box, frame.width, frame.height)
        if normalized_box is None:
            return TrackingResult(success=False, bounding_box=None, confidence=None)

        return TrackingResult(
            success=True,
            bounding_box=normalized_box,
            confidence=None,
        )

    def reset(self) -> None:
        self._tracker = None

    def _create_tracker(self) -> Any:
        factory = self._factory or _resolve_constructor(self.name)
        try:
            return factory()
        except TrackerUnavailableError:
            raise
        except Exception as exc:
            raise TrackerInitializationError(
                f"Unable to create {self.name} tracker"
            ) from exc

    @staticmethod
    def _normalize_box(
        pixel_box: tuple[float, float, float, float],
        frame_width: int,
        frame_height: int,
    ) -> BoundingBox | None:
        x, y, width, height = (float(value) for value in pixel_box)
        if width <= 0 or height <= 0:
            return None

        left = max(0.0, min(x, float(frame_width)))
        top = max(0.0, min(y, float(frame_height)))
        right = max(left, min(x + width, float(frame_width)))
        bottom = max(top, min(y + height, float(frame_height)))

        clipped_width = right - left
        clipped_height = bottom - top
        if clipped_width <= 0 or clipped_height <= 0:
            return None

        return BoundingBox.from_pixels(
            left,
            top,
            clipped_width,
            clipped_height,
            frame_width,
            frame_height,
        )


class OpenCVCSRTTracker(_OpenCVTracker):
    tracker_name = "CSRT"


class OpenCVKCFTracker(_OpenCVTracker):
    tracker_name = "KCF"
