"""Black-box style API tests through HTTP requests."""

from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_read_update_and_delete_task(client: TestClient) -> None:
    create_response = client.post(
        "/api/tasks",
        json={"title": "GitHub Actions beállítása", "description": "CI workflow"},
    )
    assert create_response.status_code == 201
    task = create_response.json()

    read_response = client.get(f"/api/tasks/{task['id']}")
    assert read_response.json()["title"] == "GitHub Actions beállítása"

    update_response = client.patch(f"/api/tasks/{task['id']}", json={"completed": True})
    assert update_response.status_code == 200
    assert update_response.json()["completed"] is True

    delete_response = client.delete(f"/api/tasks/{task['id']}")
    assert delete_response.status_code == 204
    assert client.get(f"/api/tasks/{task['id']}").status_code == 404


def test_rejects_invalid_task(client: TestClient) -> None:
    response = client.post("/api/tasks", json={"title": "x"})

    assert response.status_code == 422


def test_missing_task_returns_not_found(client: TestClient) -> None:
    response = client.patch("/api/tasks/999", json={"completed": True})

    assert response.status_code == 404


def test_task_statistics(client: TestClient) -> None:
    first = client.post("/api/tasks", json={"title": "Első feladat"}).json()
    client.post("/api/tasks", json={"title": "Második feladat"})
    client.patch(f"/api/tasks/{first['id']}", json={"completed": True})

    assert client.get("/api/stats").json() == {"total": 2, "completed": 1, "pending": 1}
