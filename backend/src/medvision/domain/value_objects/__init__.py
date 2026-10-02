from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class BoundingBox:
    """Normalized coordinates within an image, independent of its pixel dimensions."""

    x: float
    y: float
    width: float
    height: float

    def __post_init__(self) -> None:
        if not all(isfinite(value) for value in (self.x, self.y, self.width, self.height)):
            raise ValueError("Bounding box coordinates must be finite")
        if not (0 <= self.x <= 1 and 0 <= self.y <= 1):
            raise ValueError("Bounding box origin must lie within the image")
        if not (0 < self.width <= 1 and 0 < self.height <= 1):
            raise ValueError("Bounding box dimensions must be positive and at most one")
        if self.x + self.width > 1 or self.y + self.height > 1:
            raise ValueError("Bounding box must fit within the image")
