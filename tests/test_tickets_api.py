from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_ticket_crud_flow() -> None:
    create_res = client.post(
        "/tickets",
        json={
            "title": "Cannot login",
            "description": "User receives 401",
            "status": "open",
        },
    )
    assert create_res.status_code == 201
    created = create_res.json()
    ticket_id = created["id"]

    list_res = client.get("/tickets")
    assert list_res.status_code == 200
    assert any(t["id"] == ticket_id for t in list_res.json())

    get_res = client.get(f"/tickets/{ticket_id}")
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Cannot login"

    update_res = client.patch(
        f"/tickets/{ticket_id}",
        json={"status": "in_progress", "description": "Investigating auth service"},
    )
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["status"] == "in_progress"
    assert updated["description"] == "Investigating auth service"

    clear_res = client.patch(f"/tickets/{ticket_id}", json={"description": None})
    assert clear_res.status_code == 200
    assert clear_res.json()["description"] is None

    delete_res = client.delete(f"/tickets/{ticket_id}")
    assert delete_res.status_code == 204

    missing_res = client.get(f"/tickets/{ticket_id}")
    assert missing_res.status_code == 404


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "database_backend" in payload
