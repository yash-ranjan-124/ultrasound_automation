from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from medvision.domain.entities import FrameObservation, ModelManifest, TrackingRun
from medvision.domain.enums import ModelStatus, ObservationSource, StudyModality
from medvision.domain.value_objects import BoundingBox


@pytest.mark.parametrize(
    ("x", "y", "width", "height"),
    [
        (1, 0, 0.1, 0.1),
        (-0.1, 0, 0.2, 0.2),
        (0, 0, 0, 1),
        (0.8, 0, 0.3, 0.2),
        (0, 0.9, 0.2, 0.2),
        (float("nan"), 0, 0.1, 0.1),
    ],
)
def test_invalid_bounding_boxes(x: float, y: float, width: float, height: float) -> None:
    with pytest.raises(ValueError):
        BoundingBox(x, y, width, height)


def test_tracking_history_is_immutable() -> None:
    observation = FrameObservation(
        0, BoundingBox(0, 0, 1, 1), ObservationSource.MANUAL_INITIALIZATION
    )
    run = TrackingRun(uuid4(), uuid4(), "CSRT", (observation,), datetime.now(UTC))
    with pytest.raises(FrozenInstanceError):
        run.algorithm = "KCF"  # type: ignore[misc]


def test_custom_model_defaults_to_experimental() -> None:
    manifest = ModelManifest(
        "demo",
        "Demo",
        "1.0",
        "local",
        "mock",
        "segmentation",
        (StudyModality.MRI,),
        "brain",
        "3D",
        "none",
        "mask",
        "Research only",
    )
    assert manifest.status is ModelStatus.EXPERIMENTAL
