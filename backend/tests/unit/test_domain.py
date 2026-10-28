from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from medvision.domain.entities import (
    AIUseCase,
    FrameObservation,
    ModelManifest,
    TrackingRun,
    TrackingSession,
)
from medvision.domain.enums import (
    AITaskType,
    JobStatus,
    ModelStatus,
    ObservationSource,
    StudyModality,
)
from medvision.domain.exceptions import InvalidBoundingBoxError
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
    with pytest.raises(InvalidBoundingBoxError):
        BoundingBox(x, y, width, height)


def test_bounding_box_converts_between_pixels_and_normalized_coordinates() -> None:
    box = BoundingBox.from_pixels(20, 10, 40, 30, frame_width=200, frame_height=100)

    assert box == BoundingBox(0.1, 0.1, 0.2, 0.3)
    assert box.to_pixels(200, 100) == (20, 10, 40, 30)


@pytest.mark.parametrize(("width", "height"), [(0, 100), (100, 0), (-1, 100)])
def test_bounding_box_rejects_invalid_frame_dimensions(width: int, height: int) -> None:
    with pytest.raises(InvalidBoundingBoxError):
        BoundingBox.from_pixels(0, 0, 10, 10, width, height)


def test_tracking_history_is_immutable_and_scoped_to_session() -> None:
    now = datetime.now(UTC)
    session = TrackingSession(uuid4(), uuid4(), now)
    observation = FrameObservation(
        0, BoundingBox(0, 0, 1, 1), ObservationSource.MANUAL_INITIALIZATION
    )
    run = TrackingRun(
        id=uuid4(),
        session_id=session.id,
        tracker_name="CSRT",
        start_frame=0,
        status=JobStatus.COMPLETED,
        observations=(observation,),
        created_at=now,
        completed_at=now,
    )

    assert run.session_id == session.id
    with pytest.raises(FrozenInstanceError):
        run.tracker_name = "KCF"  # type: ignore[misc]


def test_ai_use_case_models_modality_and_task_explicitly() -> None:
    use_case = AIUseCase(
        id="brain-mri-research-segmentation",
        name="Brain MRI Research Segmentation",
        task_type=AITaskType.SEGMENTATION,
        supported_modalities=(StudyModality.MRI,),
        anatomy="brain",
        description="Research segmentation workflow",
        intended_use="Research visualization only",
    )

    assert use_case.task_type is AITaskType.SEGMENTATION
    assert use_case.supported_modalities == (StudyModality.MRI,)


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
