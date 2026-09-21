from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "deploybridge-api",
    }


def test_validation_endpoint_accepts_valid_customer() -> None:
    response = client.post(
        "/api/v1/customers/validate",
        json={
            "customer_id": "cust-001",
            "company_name": "Northstar Logistics",
            "contact_email": "OPS@NORTHSTAR.EXAMPLE",
            "plan": "enterprise",
            "employee_count": 250,
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["valid"] is True
    assert body["data"]["contact_email"] == "ops@northstar.example"
    assert body["issues"] == []


def test_validation_endpoint_rejects_invalid_customer() -> None:
    response = client.post(
        "/api/v1/customers/validate",
        json={
            "customer_id": "cust-002",
            "contact_email": "invalid-email",
            "plan": "unlimited",
            "employee_count": 0,
        },
    )

    body = response.json()
    invalid_fields = {
        issue["field"]
        for issue in body["issues"]
    }

    assert response.status_code == 200
    assert body["valid"] is False
    assert body["data"] is None
    assert {
        "company_name",
        "contact_email",
        "plan",
        "employee_count",
    }.issubset(invalid_fields)

def test_root() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "name": "DeployBridge API",
        "status": "running",
        "documentation": "/docs",
    }
    