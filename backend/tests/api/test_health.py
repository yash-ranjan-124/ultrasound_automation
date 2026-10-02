from fastapi.testclient import TestClient

from medvision.main import app


def test_health() -> None:
    response = TestClient(app).get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "medvision-api"}


def test_missing_route_does_not_leak_stack_trace() -> None:
    response = TestClient(app).get("/api/v1/not-found")
    assert response.status_code == 404
    assert response.json() == {
        "error": {"code": "HTTP_ERROR", "message": "Not Found", "details": {}}
    }
