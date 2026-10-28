from io import BytesIO

import cv2
import numpy as np
import pytest

from medvision.domain.exceptions import (
    InvalidVideoFrameError,
    VideoNotOpenError,
    VideoReadError,
)
from medvision.domain.ports import VideoReaderPort
from medvision.infrastructure.imaging import OpenCVVideoReader
from medvision.infrastructure.storage import LocalFileStorageAdapter


def make_video_bytes(tmp_path) -> bytes:
    video_path = tmp_path / "synthetic.avi"
    writer = cv2.VideoWriter(
        str(video_path),
        cv2.VideoWriter_fourcc(*"MJPG"),
        5.0,
        (16, 12),
    )
    assert writer.isOpened()
    for value in (0, 60, 120, 180):
        frame = np.full((12, 16, 3), value, dtype=np.uint8)
        writer.write(frame)
    writer.release()
    return video_path.read_bytes()


def make_reader(tmp_path) -> OpenCVVideoReader:
    storage = LocalFileStorageAdapter(tmp_path / "storage")
    storage.save("studies/video/source.avi", BytesIO(make_video_bytes(tmp_path)))
    reader: VideoReaderPort = OpenCVVideoReader(storage)
    assert isinstance(reader, OpenCVVideoReader)
    return reader


def test_video_reader_requires_open_source(tmp_path) -> None:
    reader = make_reader(tmp_path)

    with pytest.raises(VideoNotOpenError):
        reader.get_metadata()
    with pytest.raises(VideoNotOpenError):
        reader.read_frame(0)


def test_video_reader_extracts_metadata_and_reads_random_frames(tmp_path) -> None:
    reader = make_reader(tmp_path)
    reader.open("studies/video/source.avi", "source.avi")

    metadata = reader.get_metadata()
    assert metadata.width == 16
    assert metadata.height == 12
    assert metadata.fps == pytest.approx(5.0)
    assert metadata.frame_count == 4
    assert metadata.duration_seconds == pytest.approx(0.8)

    first = reader.read_frame(0)
    third = reader.read_frame(2)

    assert first.frame_number == 0
    assert first.width == 16
    assert first.height == 12
    assert third.frame_number == 2
    assert float(np.mean(third.pixels)) > float(np.mean(first.pixels))

    reader.close()


def test_video_reader_iterates_from_requested_frame(tmp_path) -> None:
    reader = make_reader(tmp_path)
    reader.open("studies/video/source.avi", "source.avi")

    frames = list(reader.iter_frames(start_frame=2))

    assert [frame.frame_number for frame in frames] == [2, 3]
    assert all(frame.width == 16 and frame.height == 12 for frame in frames)
    reader.close()


@pytest.mark.parametrize("frame_number", [-1, 4, 100])
def test_video_reader_rejects_out_of_range_frame(tmp_path, frame_number: int) -> None:
    reader = make_reader(tmp_path)
    reader.open("studies/video/source.avi", "source.avi")

    with pytest.raises(InvalidVideoFrameError):
        reader.read_frame(frame_number)

    reader.close()


def test_video_reader_close_is_idempotent_and_removes_working_file(tmp_path) -> None:
    reader = make_reader(tmp_path)
    reader.open("studies/video/source.avi", "source.avi")
    working_path = reader._working_path

    assert working_path is not None
    assert working_path.exists()

    reader.close()
    reader.close()

    assert not working_path.exists()
    with pytest.raises(VideoNotOpenError):
        reader.get_metadata()


def test_video_reader_can_reopen_after_close(tmp_path) -> None:
    reader = make_reader(tmp_path)

    reader.open("studies/video/source.avi", "source.avi")
    reader.close()
    reader.open("studies/video/source.avi", "source.avi")

    assert reader.read_frame(1).frame_number == 1
    reader.close()


def test_video_reader_rejects_unreadable_video(tmp_path) -> None:
    storage = LocalFileStorageAdapter(tmp_path / "storage")
    storage.save("studies/video/broken.avi", BytesIO(b"not a video"))
    reader = OpenCVVideoReader(storage)

    with pytest.raises(VideoReadError):
        reader.open("studies/video/broken.avi", "broken.avi")

    with pytest.raises(VideoNotOpenError):
        reader.get_metadata()
