from typing import Any

from pydantic import BaseModel, Field

from backend.app.schema_validator import CustomerRecord


DEFAULT_FIELD_MAP = {
    "id": "customer_id",
    "company": "company_name",
    "email": "contact_email",
    "tier": "plan",
    "headcount": "employee_count",
}


class MappingIssue(BaseModel):
    source_field: str | None = None
    target_field: str | None = None
    code: str
    message: str


class MappingResult(BaseModel):
    ready_for_validation: bool
    mapped_data: dict[str, Any] = Field(default_factory=dict)
    issues: list[MappingIssue] = Field(default_factory=list)


def map_customer_fields(
    payload: dict[str, Any],
    field_map: dict[str, str] | None = None,
) -> MappingResult:
    """Map customer fields into the DeployBridge customer schema."""

    active_map = field_map or DEFAULT_FIELD_MAP
    target_fields = set(CustomerRecord.model_fields)
    mapped_data: dict[str, Any] = {}
    issues: list[MappingIssue] = []

    for source_field, value in payload.items():
        if source_field in target_fields:
            target_field = source_field
        else:
            target_field = active_map.get(source_field)

        if target_field is None:
            issues.append(
                MappingIssue(
                    source_field=source_field,
                    code="unmapped_source_field",
                    message=f"No mapping exists for '{source_field}'.",
                )
            )
            continue

        if target_field not in target_fields:
            issues.append(
                MappingIssue(
                    source_field=source_field,
                    target_field=target_field,
                    code="invalid_target_field",
                    message=f"'{target_field}' is not supported by the target schema.",
                )
            )
            continue

        if target_field in mapped_data:
            issues.append(
                MappingIssue(
                    source_field=source_field,
                    target_field=target_field,
                    code="duplicate_target_field",
                    message=f"Multiple source fields map to '{target_field}'.",
                )
            )
            continue

        mapped_data[target_field] = value

    missing_fields = target_fields - set(mapped_data)

    for target_field in sorted(missing_fields):
        issues.append(
            MappingIssue(
                target_field=target_field,
                code="missing_target_field",
                message=f"Required target field '{target_field}' is missing.",
            )
        )

    return MappingResult(
        ready_for_validation=not issues,
        mapped_data=mapped_data,
        issues=issues,
    )