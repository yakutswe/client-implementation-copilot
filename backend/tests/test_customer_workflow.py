from backend.app.customer_workflow import prepare_customer


def test_stops_when_mapping_fails() -> None:
    payload = {
        "id": "cust-301",
        "company": "Northstar Logistics",
        "unsupported_field": "not mapped",
    }

    result = prepare_customer(payload)
    issue_codes = {issue.code for issue in result.mapping_issues}

    assert result.status == "mapping_failed"
    assert result.ready_for_planning is False
    assert result.customer is None
    assert "unmapped_source_field" in issue_codes
    assert result.validation_issues == []


def test_stops_when_validation_fails() -> None:
    payload = {
        "id": "cust-302",
        "company": "Harbor Systems",
        "email": "invalid-email",
        "tier": "unlimited",
        "headcount": 0,
    }

    result = prepare_customer(payload)
    invalid_fields = {
        issue.field
        for issue in result.validation_issues
    }

    assert result.status == "validation_failed"
    assert result.ready_for_planning is False
    assert result.customer is None
    assert result.mapping_issues == []
    assert {
        "contact_email",
        "plan",
        "employee_count",
    }.issubset(invalid_fields)


def test_returns_ready_customer_after_mapping_and_validation() -> None:
    payload = {
        "id": "cust-303",
        "company": "Atlas Freight",
        "email": "OPS@ATLAS.EXAMPLE",
        "tier": "enterprise",
        "headcount": 180,
    }

    result = prepare_customer(payload)

    assert result.status == "ready"
    assert result.ready_for_planning is True
    assert result.mapping_issues == []
    assert result.validation_issues == []
    assert result.customer is not None
    assert result.customer.customer_id == "cust-303"
    assert result.customer.company_name == "Atlas Freight"
    assert result.customer.contact_email == "ops@atlas.example"
    