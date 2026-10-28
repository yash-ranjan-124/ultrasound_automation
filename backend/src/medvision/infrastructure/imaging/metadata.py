import re
from pathlib import Path
from shutil import copyfileobj
from tempfile import NamedTemporaryFile
from typing import Any, BinaryIO, Protocol, cast

import cv2
import nibabel as nib
import pydicom
from PIL import Image

from medvision.domain.enums import StudyType
from medvision.domain.exceptions import MetadataExtractionError


class _NiftiHeader(Protocol):
    def get_zooms(self) -> tuple[float, ...]: ...


class _NiftiVolume(Protocol):
    shape: tuple[int, ...]
    header: _NiftiHeader


class LocalStudyMetadataReader:
    """Extract metadata from a storage-agnostic binary stream.

    Some imaging libraries require a filesystem path, so the adapter materializes
    a short-lived local working copy. The caller remains coupled only to StoragePort.
    """

    def extract(
        self,
        study_type: StudyType,
        content: BinaryIO,
        filename: str,
    ) -> dict[str, object]:
        suffix = self._suffix_for(filename)
        temporary_path: Path | None = None
        try:
            with NamedTemporaryFile(suffix=suffix, delete=False) as temporary:
                temporary_path = Path(temporary.name)
                copyfileobj(content, temporary)
                temporary.flush()

            if study_type is StudyType.VIDEO:
                return self._video_metadata(temporary_path)
            if study_type is StudyType.IMAGE:
                return self._image_metadata(temporary_path)
            if study_type is StudyType.NIFTI:
                return self._nifti_metadata(temporary_path)
            if study_type is StudyType.DICOM:
                return self._dicom_metadata(temporary_path)
        except MetadataExtractionError:
            raise
        except Exception as exc:
            raise MetadataExtractionError("Unable to read supported imaging file") from exc
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
        raise MetadataExtractionError("Unsupported imaging study type")

    @staticmethod
    def _suffix_for(filename: str) -> str:
        lowered = filename.lower()
        if lowered.endswith(".nii.gz"):
            return ".nii.gz"
        return Path(filename).suffix.lower()

    @staticmethod
    def _video_metadata(path: Path) -> dict[str, object]:
        capture = cv2.VideoCapture(str(path))
        try:
            if not capture.isOpened():
                raise MetadataExtractionError("Unable to read uploaded video")
            width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = float(capture.get(cv2.CAP_PROP_FPS))
            frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
            if width <= 0 or height <= 0 or frame_count <= 0:
                raise MetadataExtractionError("Uploaded video has invalid technical metadata")
            return {
                "width": width,
                "height": height,
                "fps": fps if fps > 0 else None,
                "frame_count": frame_count,
                "duration_seconds": frame_count / fps if fps > 0 else None,
            }
        finally:
            capture.release()

    @staticmethod
    def _image_metadata(path: Path) -> dict[str, object]:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            return {"width": int(image.width), "height": int(image.height)}

    @staticmethod
    def _nifti_metadata(path: Path) -> dict[str, object]:
        image = cast(_NiftiVolume, nib.load(str(path)))
        return {
            "shape": [int(dimension) for dimension in image.shape],
            "voxel_spacing": [float(value) for value in image.header.get_zooms()],
        }

    @staticmethod
    def _dicom_metadata(path: Path) -> dict[str, object]:
        dataset = pydicom.dcmread(path, stop_before_pixels=True)
        metadata: dict[str, object] = {}
        allowed = {
            "Modality": "modality",
            "Rows": "rows",
            "Columns": "columns",
            "NumberOfFrames": "number_of_frames",
        }
        for dicom_name, key in allowed.items():
            value: Any = getattr(dataset, dicom_name, None)
            if value is not None:
                if key in {"rows", "columns", "number_of_frames"}:
                    try:
                        metadata[key] = int(value)
                    except (TypeError, ValueError):
                        continue
                else:
                    metadata[key] = str(value)
        description = getattr(dataset, "SeriesDescription", None)
        if description:
            sanitized = re.sub(r"[^A-Za-z0-9 ._-]", "", str(description))[:128].strip()
            if sanitized:
                metadata["series_description"] = sanitized
        return metadata
