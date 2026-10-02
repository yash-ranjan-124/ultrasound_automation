from io import BytesIO
from uuid import uuid4

from fastapi.testclient import TestClient
from PIL import Image

from medvision.config import Settings
from medvision.infrastructure.persistence import InMemoryStudyRepository
from medvision.main import create_app


def png_bytes() -> bytes:
    image = Image.new("RGB", (7, 5), color=(10, 20, 30))
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def client_for(tmp_path) -> TestClient:
    return TestClient(
        create_app(
            Settings(storage_root=tmp_path / "storage"),
            repository=InMemoryStudyRepository(),
        )
    )


def test_create_list_and_get_image_study(tmp_path) -> None:
    client = client_for(tmp_path)
    response = client.post(
        "/api/v1/studies",
        data={"modality": "MRI"},
        files={"file": ("synthetic.png", png_bytes(), "image/png")},
    )

    assert response.status_code == 201
    study = response.json()
    assert study["filename"] == "synthetic.png"
    assert study["study_type"] == "IMAGE"
    assert study["modality"] == "MRI"
    assert study["metadata"] == {"width": 7, "height": 5}
    assert "storage_key" not in study
    assert "path" not in study

    assert client.get("/api/v1/studies").json() == [study]
    assert client.get(f"/api/v1/studies/{study['id']}").json() == study


def test_unsupported_file_has_standard_error_and_is_not_stored(tmp_path) -> None:
    client = client_for(tmp_path)
    response = client.post(
        "/api/v1/studies",
        data={"modality": "UNKNOWN"},
        files={"file": ("payload.exe", b"not a study", "application/octet-stream")},
    )

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "code": "UNSUPPORTED_STUDY_TYPE",
            "message": "The uploaded file type is not supported.",
            "details": {},
        }
    }
    assert list((tmp_path / "storage").rglob("source*")) == []


def test_invalid_modality_is_rejected_with_error_envelope(tmp_path) -> None:
    response = client_for(tmp_path).post(
        "/api/v1/studies",
        data={"modality": "BRAIN"},
        files={"file": ("synthetic.png", png_bytes(), "image/png")},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_REQUEST"


def test_invalid_image_cleans_up_storage_and_is_not_listed(tmp_path) -> None:
    client = client_for(tmp_path)
    response = client.post(
        "/api/v1/studies",
        data={"modality": "UNKNOWN"},
        files={"file": ("broken.png", b"not really png", "image/png")},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_STUDY_FILE"
    assert client.get("/api/v1/studies").json() == []
    assert list((tmp_path / "storage").rglob("source*")) == []


def test_unknown_study_has_standard_404_error(tmp_path) -> None:
    response = client_for(tmp_path).get(f"/api/v1/studies/{uuid4()}")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "STUDY_NOT_FOUND"
