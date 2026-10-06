from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == (
        "Enterprise AI Operations Agent is running"
    )


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy"
    }


def test_invalid_short_message():
    response = client.post(
        "/analyze",
        json={
            "customer_id": "CUST-TEST",
            "customer_email": "test@example.com",
            "message": "a"
        }
    )

    assert response.status_code == 422


def test_invalid_email():
    response = client.post(
        "/analyze",
        json={
            "customer_id": "CUST-TEST",
            "customer_email": "not-an-email",
            "message": "I cannot access my account."
        }
    )

    assert response.status_code == 422


def test_missing_customer_id():
    response = client.post(
        "/analyze",
        json={
            "customer_email": "test@example.com",
            "message": "I cannot access my account."
        }
    )

    assert response.status_code == 422


def test_unknown_task():
    response = client.get(
        "/tasks/TASK-DOES-NOT-EXIST"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_invalid_task_status():
    response = client.patch(
        "/tasks/TASK-DOES-NOT-EXIST",
        json={
            "status": "pizza"
        }
    )

    assert response.status_code == 422


def test_unknown_approval():
    response = client.get(
        "/approvals/APR-DOES-NOT-EXIST"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Approval not found"


def test_invalid_approval_status():
    response = client.patch(
        "/approvals/APR-DOES-NOT-EXIST",
        json={
            "status": "Maybe"
        }
    )

    assert response.status_code == 422


def test_audit_logs_endpoint():
    response = client.get("/audit-logs")

    assert response.status_code == 200
    assert "audit_logs" in response.json()