from dataclasses import dataclass
from math import isfinite
from typing import Any

from medvision.domain.exceptions import InvalidBoundingBoxError


@dataclass(frozen=True)
class BoundingBox:
    """Normalized coordinates within an image, independent of pixel dimensions."""

    x: float
    y: float
    width: float
    height: float

    def __post_init__(self) -> None:
        if not all(isfinite(value) for value in (self.x, self.y, self.width, self.height)):
            raise InvalidBoundingBoxError("Bounding box coordinates must be finite")
        if not (0 <= self.x <= 1 and 0 <= self.y <= 1):
            raise InvalidBoundingBoxError("Bounding box origin must lie within the image")
        if not (0 < self.width <= 1 and 0 < self.height <= 1):
            raise InvalidBoundingBoxError(
                "Bounding box dimensions must be positive and at most one"
            )
        if self.x + self.width > 1 or self.y + self.height > 1:
            raise InvalidBoundingBoxError("Bounding box must fit within the image")

    @classmethod
    def from_pixels(
        cls,
        x: float,
        y: float,
        width: float,
        height: float,
        frame_width: int,
        frame_height: int,
    ) -> "BoundingBox":
        if frame_width <= 0 or frame_height <= 0:
            raise InvalidBoundingBoxError("Frame dimensions must be positive")
        return cls(
            x=x / frame_width,
            y=y / frame_height,
            width=width / frame_width,
            height=height / frame_height,
        )

    def to_pixels(self, frame_width: int, frame_height: int) -> tuple[int, int, int, int]:
        if frame_width <= 0 or frame_height <= 0:
            raise InvalidBoundingBoxError("Frame dimensions must be positive")
        return (
            round(self.x * frame_width),
            round(self.y * frame_height),
            round(self.width * frame_width),
            round(self.height * frame_height),
        )


@dataclass(frozen=True)
class VideoMetadata:
    width: int
    height: int
    fps: float
    frame_count: int
    duration_seconds: float

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Video dimensions must be positive")
        if self.fps <= 0 or not isfinite(self.fps):
            raise ValueError("Video FPS must be finite and positive")
        if self.frame_count <= 0:
            raise ValueError("Video frame count must be positive")
        if self.duration_seconds <= 0 or not isfinite(self.duration_seconds):
            raise ValueError("Video duration must be finite and positive")


@dataclass(frozen=True)
class VideoFrame:
    frame_number: int
    width: int
    height: int
    pixels: Any

    def __post_init__(self) -> None:
        if self.frame_number < 0:
            raise ValueError("Frame number cannot be negative")
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Frame dimensions must be positive")
