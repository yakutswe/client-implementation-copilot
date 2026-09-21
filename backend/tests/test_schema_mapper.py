from backend.app.schema_mapper import map_customer_fields
from backend.app.schema_validator import validate_customer


def test_maps_customer_aliases_into_target_schema() -> None:
    payload = {
        "id": "cust-101",
        "company": "Northstar Logistics",
        "email": "OPS@NORTHSTAR.EXAMPLE",
        "tier": "enterprise",
        "headcount": 250,
    }

    mapping = map_customer_fields(payload)

    assert mapping.ready_for_validation is True
    assert mapping.issues == []
    assert mapping.mapped_data == {
        "customer_id": "cust-101",
        "company_name": "Northstar Logistics",
        "contact_email": "OPS@NORTHSTAR.EXAMPLE",
        "plan": "enterprise",
        "employee_count": 250,
    }

    validation = validate_customer(mapping.mapped_data)

    assert validation.valid is True
    assert validation.data is not None
    assert validation.data.contact_email == "ops@northstar.example"


def test_reports_unknown_and_missing_fields() -> None:
    payload = {
        "id": "cust-102",
        "company": "Harbor Systems",
        "unknown_property": "not supported",
    }

    result = map_customer_fields(payload)
    issue_codes = {issue.code for issue in result.issues}
    missing_targets = {
        issue.target_field
        for issue in result.issues
        if issue.code == "missing_target_field"
    }

    assert result.ready_for_validation is False
    assert "unmapped_source_field" in issue_codes
    assert missing_targets == {
        "contact_email",
        "employee_count",
        "plan",
    }


def test_rejects_duplicate_target_mapping() -> None:
    payload = {
        "id": "cust-103",
        "company": "Original Company",
        "company_name": "Conflicting Company",
        "email": "ops@example.com",
        "tier": "growth",
        "headcount": 40,
    }

    result = map_customer_fields(payload)

    assert result.ready_for_validation is False
    assert any(
        issue.code == "duplicate_target_field"
        and issue.target_field == "company_name"
        for issue in result.issues
    )
    assert result.mapped_data["company_name"] == "Original Company"