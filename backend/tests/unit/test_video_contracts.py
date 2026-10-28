import pytest

from medvision.domain.value_objects import VideoFrame, VideoMetadata


def test_video_metadata_accepts_valid_values() -> None:
    metadata = VideoMetadata(
        width=1920,
        height=1080,
        fps=30.0,
        frame_count=300,
        duration_seconds=10.0,
    )

    assert metadata.duration_seconds == 10.0


@pytest.mark.parametrize(
    ("width", "height", "fps", "frame_count", "duration_seconds"),
    [
        (0, 1080, 30.0, 300, 10.0),
        (1920, 0, 30.0, 300, 10.0),
        (1920, 1080, 0.0, 300, 10.0),
        (1920, 1080, float("nan"), 300, 10.0),
        (1920, 1080, 30.0, 0, 10.0),
        (1920, 1080, 30.0, 300, 0.0),
    ],
)
def test_video_metadata_rejects_invalid_values(
    width: int,
    height: int,
    fps: float,
    frame_count: int,
    duration_seconds: float,
) -> None:
    with pytest.raises(ValueError):
        VideoMetadata(width, height, fps, frame_count, duration_seconds)


def test_video_frame_validates_number_and_dimensions() -> None:
    with pytest.raises(ValueError):
        VideoFrame(-1, 16, 12, object())
    with pytest.raises(ValueError):
        VideoFrame(0, 0, 12, object())
