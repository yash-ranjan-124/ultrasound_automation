from __future__ import annotations

from collections.abc import Callable

from medvision.domain.exceptions import UnsupportedTrackerError
from medvision.domain.ports import ObjectTracker
from medvision.infrastructure.tracking.opencv import OpenCVCSRTTracker, OpenCVKCFTracker

TrackerBuilder = Callable[[], ObjectTracker]


class TrackerRegistry:
    def __init__(self, builders: dict[str, TrackerBuilder] | None = None) -> None:
        self._builders = {
            name.upper(): builder
            for name, builder in (
                builders
                if builders is not None
                else {
                    "CSRT": OpenCVCSRTTracker,
                    "KCF": OpenCVKCFTracker,
                }
            ).items()
        }

    def supported_names(self) -> tuple[str, ...]:
        return tuple(sorted(self._builders))

    def create(self, name: str) -> ObjectTracker:
        normalized = name.strip().upper()
        builder = self._builders.get(normalized)
        if builder is None:
            raise UnsupportedTrackerError(
                f"Unsupported tracker '{name}'. Supported trackers: "
                + ", ".join(self.supported_names())
            )
        return builder()
