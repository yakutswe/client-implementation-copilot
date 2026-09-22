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


def test_maps_customer_aliases() -> None:
    response = client.post(
        "/api/v1/customers/map",
        json={
            "id": "cust-201",
            "company": "Northstar Logistics",
            "email": "ops@northstar.example",
            "tier": "enterprise",
            "headcount": 250,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["ready_for_validation"] is True
    assert body["issues"] == []
    assert body["mapped_data"] == {
        "customer_id": "cust-201",
        "company_name": "Northstar Logistics",
        "contact_email": "ops@northstar.example",
        "plan": "enterprise",
        "employee_count": 250,
    }


def test_reports_incomplete_customer_mapping() -> None:
    response = client.post(
        "/api/v1/customers/map",
        json={
            "id": "cust-202",
            "company": "Harbor Systems",
            "unsupported_field": "not mapped",
        },
    )

    assert response.status_code == 200

    body = response.json()
    issue_codes = {issue["code"] for issue in body["issues"]}
    missing_targets = {
        issue["target_field"]
        for issue in body["issues"]
        if issue["code"] == "missing_target_field"
    }

    assert body["ready_for_validation"] is False
    assert "unmapped_source_field" in issue_codes
    assert missing_targets == {
        "contact_email",
        "employee_count",
        "plan",
    }
    