from backend.app.schema_validator import validate_customer


def test_accepts_valid_customer() -> None:
    payload = {
        "customer_id": "cust-001",
        "company_name": "Northstar Logistics",
        "contact_email": "OPS@NORTHSTAR.EXAMPLE",
        "plan": "enterprise",
        "employee_count": 250,
    }

    result = validate_customer(payload)

    assert result.valid is True
    assert result.data is not None
    assert result.data.contact_email == "ops@northstar.example"
    assert result.issues == []


def test_rejects_invalid_customer() -> None:
    payload = {
        "customer_id": "cust-002",
        "contact_email": "invalid-email",
        "plan": "unlimited",
        "employee_count": 0,
        "unexpected_field": "not allowed",
    }

    result = validate_customer(payload)
    invalid_fields = {issue.field for issue in result.issues}

    assert result.valid is False
    assert result.data is None
    assert {
        "company_name",
        "contact_email",
        "plan",
        "employee_count",
        "unexpected_field",
    }.issubset(invalid_fields)