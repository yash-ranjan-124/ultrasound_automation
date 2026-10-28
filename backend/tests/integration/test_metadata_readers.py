import json
from io import BytesIO
from pathlib import Path

import cv2
import nibabel as nib
import numpy as np
import pydicom
import pytest
from PIL import Image
from pydicom.dataset import FileDataset, FileMetaDataset
from pydicom.uid import (
    ExplicitVRLittleEndian,
    SecondaryCaptureImageStorage,
    generate_uid,
)

from medvision.domain.enums import StudyType
from medvision.domain.exceptions import MetadataExtractionError
from medvision.infrastructure.imaging import LocalStudyMetadataReader


def test_image_metadata_reads_dimensions_without_storage_dependency(tmp_path) -> None:
    image_path = tmp_path / "synthetic.png"
    Image.new("RGB", (12, 9)).save(image_path)

    with image_path.open("rb") as source:
        metadata = LocalStudyMetadataReader().extract(
            StudyType.IMAGE,
            source,
            "synthetic.png",
        )

    assert metadata == {"width": 12, "height": 9}


def test_video_metadata_reads_technical_properties_without_retaining_frames(tmp_path) -> None:
    video_path = tmp_path / "synthetic.avi"
    writer = cv2.VideoWriter(str(video_path), cv2.VideoWriter_fourcc(*"MJPG"), 5.0, (16, 12))
    assert writer.isOpened()
    for color in ((0, 0, 0), (255, 255, 255), (40, 80, 120)):
        writer.write(np.full((12, 16, 3), color, dtype=np.uint8))
    writer.release()

    with video_path.open("rb") as source:
        metadata = LocalStudyMetadataReader().extract(
            StudyType.VIDEO,
            source,
            "synthetic.avi",
        )

    assert metadata["width"] == 16
    assert metadata["height"] == 12
    assert metadata["frame_count"] == 3
    assert metadata["fps"] == 5.0
    assert metadata["duration_seconds"] == 0.6


def test_nifti_metadata_reads_shape_spacing_and_preserves_double_suffix(tmp_path) -> None:
    nifti_path = tmp_path / "synthetic.nii.gz"
    image = nib.Nifti1Image(np.zeros((2, 3, 4), dtype=np.uint8), np.diag([2, 3, 4, 1]))
    nib.save(image, nifti_path)

    with nifti_path.open("rb") as source:
        metadata = LocalStudyMetadataReader().extract(
            StudyType.NIFTI,
            source,
            "synthetic.nii.gz",
        )

    assert metadata == {"shape": [2, 3, 4], "voxel_spacing": [2.0, 3.0, 4.0]}


def make_dicom(path: Path) -> None:
    file_meta = FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = SecondaryCaptureImageStorage
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    file_meta.ImplementationClassUID = generate_uid()
    dataset = FileDataset(str(path), {}, file_meta=file_meta, preamble=b"\0" * 128)
    dataset.PatientName = "SECRET NAME"
    dataset.PatientID = "SECRET-ID"
    dataset.PatientBirthDate = "19700101"
    dataset.PatientAddress = "Private address"
    dataset.AccessionNumber = "PRIVATE-ACC"
    dataset.Modality = "MR"
    dataset.Rows = 64
    dataset.Columns = 64
    dataset.NumberOfFrames = "2"
    dataset.SeriesDescription = "MR research"
    pydicom.dcmwrite(path, dataset, enforce_file_format=True)


def test_dicom_reader_only_emits_allowlisted_sanitized_fields(tmp_path) -> None:
    dicom_path = tmp_path / "synthetic.dcm"
    make_dicom(dicom_path)

    with dicom_path.open("rb") as source:
        metadata = LocalStudyMetadataReader().extract(
            StudyType.DICOM,
            source,
            "synthetic.dcm",
        )
    serialized = json.dumps(metadata)

    assert metadata == {
        "modality": "MR",
        "rows": 64,
        "columns": 64,
        "number_of_frames": 2,
        "series_description": "MR research",
    }
    for private_value in (
        "PatientName",
        "PatientID",
        "PatientBirthDate",
        "PatientAddress",
        "AccessionNumber",
        "SECRET NAME",
        "SECRET-ID",
        "PRIVATE-ACC",
    ):
        assert private_value not in serialized


def test_metadata_reader_rejects_invalid_image_file() -> None:
    with pytest.raises(MetadataExtractionError, match="Unable to read supported imaging file"):
        LocalStudyMetadataReader().extract(
            StudyType.IMAGE,
            BytesIO(b"not an image"),
            "broken.png",
        )
