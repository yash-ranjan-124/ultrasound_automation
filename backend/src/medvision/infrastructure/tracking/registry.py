from __future__ import annotations

from collections.abc import Callable

from medvision.domain.exceptions import UnsupportedTrackerError
from medvision.domain.ports import ObjectTracker
from medvision.infrastructure.tracking.opencv import OpenCVCSRTTracker, OpenCVKCFTracker

TrackerBuilder = Callable[[], ObjectTracker]


class TrackerRegistry:
    def __init__(self, builders: dict[str, TrackerBuilder] | None = None) -> None:
        default_builders: dict[str, TrackerBuilder] = {
            "CSRT": OpenCVCSRTTracker,
            "KCF": OpenCVKCFTracker,
        }
        selected_builders = builders if builders is not None else default_builders
        self._builders = {
            name.strip().upper(): builder for name, builder in selected_builders.items()
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
