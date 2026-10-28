from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from shutil import copyfileobj
from tempfile import NamedTemporaryFile
from typing import BinaryIO

import cv2

from medvision.domain.exceptions import (
    InvalidVideoFrameError,
    VideoNotOpenError,
    VideoReadError,
)
from medvision.domain.ports import StoragePort
from medvision.domain.value_objects import VideoFrame, VideoMetadata


class OpenCVVideoReader:
    """Storage-agnostic video reader backed by OpenCV."""

    def __init__(self, storage: StoragePort) -> None:
        self._storage = storage
        self._capture: cv2.VideoCapture | None = None
        self._working_path: Path | None = None
        self._metadata: VideoMetadata | None = None

    def open(self, storage_key: str, filename: str) -> None:
        self.close()
        suffix = Path(filename).suffix.lower() or ".video"
        working_path: Path | None = None
        capture: cv2.VideoCapture | None = None
        try:
            with self._storage.open(storage_key) as source:
                working_path = self._materialize(source, suffix)

            capture = cv2.VideoCapture(str(working_path))
            if not capture.isOpened():
                raise VideoReadError("Unable to open stored video")

            metadata = self._read_metadata(capture)
            self._capture = capture
            self._working_path = working_path
            self._metadata = metadata
            capture = None
            working_path = None
        except Exception:
            if capture is not None:
                capture.release()
            if working_path is not None:
                working_path.unlink(missing_ok=True)
            raise

    def get_metadata(self) -> VideoMetadata:
        self._require_open()
        assert self._metadata is not None
        return self._metadata

    def read_frame(self, frame_number: int) -> VideoFrame:
        capture = self._require_open()
        metadata = self.get_metadata()
        self._validate_frame_number(frame_number, metadata)

        if not capture.set(cv2.CAP_PROP_POS_FRAMES, float(frame_number)):
            raise VideoReadError(f"Unable to seek to frame {frame_number}")

        success, pixels = capture.read()
        if not success or pixels is None:
            raise VideoReadError(f"Unable to read frame {frame_number}")

        return VideoFrame(
            frame_number=frame_number,
            width=int(pixels.shape[1]),
            height=int(pixels.shape[0]),
            pixels=pixels,
        )

    def iter_frames(self, start_frame: int = 0) -> Iterator[VideoFrame]:
        capture = self._require_open()
        metadata = self.get_metadata()
        self._validate_frame_number(start_frame, metadata)

        if not capture.set(cv2.CAP_PROP_POS_FRAMES, float(start_frame)):
            raise VideoReadError(f"Unable to seek to frame {start_frame}")

        frame_number = start_frame
        while frame_number < metadata.frame_count:
            success, pixels = capture.read()
            if not success or pixels is None:
                raise VideoReadError(f"Unable to read frame {frame_number}")
            yield VideoFrame(
                frame_number=frame_number,
                width=int(pixels.shape[1]),
                height=int(pixels.shape[0]),
                pixels=pixels,
            )
            frame_number += 1

    def close(self) -> None:
        capture = self._capture
        working_path = self._working_path
        self._capture = None
        self._working_path = None
        self._metadata = None

        if capture is not None:
            capture.release()
        if working_path is not None:
            working_path.unlink(missing_ok=True)

    def __enter__(self) -> OpenCVVideoReader:
        return self

    def __exit__(self, _exc_type: object, _exc: object, _traceback: object) -> None:
        self.close()

    def _require_open(self) -> cv2.VideoCapture:
        if self._capture is None or not self._capture.isOpened():
            raise VideoNotOpenError("Video reader is not open")
        return self._capture

    @staticmethod
    def _materialize(source: BinaryIO, suffix: str) -> Path:
        with NamedTemporaryFile(suffix=suffix, delete=False) as destination:
            copyfileobj(source, destination)
            destination.flush()
            return Path(destination.name)

    @staticmethod
    def _read_metadata(capture: cv2.VideoCapture) -> VideoMetadata:
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = float(capture.get(cv2.CAP_PROP_FPS))
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        if width <= 0 or height <= 0 or frame_count <= 0 or fps <= 0:
            raise VideoReadError("Stored video has invalid technical metadata")
        return VideoMetadata(
            width=width,
            height=height,
            fps=fps,
            frame_count=frame_count,
            duration_seconds=frame_count / fps,
        )

    @staticmethod
    def _validate_frame_number(frame_number: int, metadata: VideoMetadata) -> None:
        if frame_number < 0 or frame_number >= metadata.frame_count:
            raise InvalidVideoFrameError(
                f"Frame {frame_number} is outside valid range 0..{metadata.frame_count - 1}"
            )
