from typing import Any, Literal

from pydantic import BaseModel, Field

from backend.app.schema_mapper import (
    MappingIssue,
    map_customer_fields,
)
from backend.app.schema_validator import (
    CustomerRecord,
    ValidationIssue,
    validate_customer,
)


class CustomerPreparationResult(BaseModel):
    status: Literal[
        "mapping_failed",
        "validation_failed",
        "ready",
    ]
    ready_for_planning: bool
    mapped_data: dict[str, Any] = Field(default_factory=dict)
    customer: CustomerRecord | None = None
    mapping_issues: list[MappingIssue] = Field(default_factory=list)
    validation_issues: list[ValidationIssue] = Field(default_factory=list)


def prepare_customer(payload: dict[str, Any]) -> CustomerPreparationResult:
    """Map and validate customer data before implementation planning."""

    mapping = map_customer_fields(payload)

    if not mapping.ready_for_validation:
        return CustomerPreparationResult(
            status="mapping_failed",
            ready_for_planning=False,
            mapped_data=mapping.mapped_data,
            mapping_issues=mapping.issues,
        )

    validation = validate_customer(mapping.mapped_data)

    if not validation.valid:
        return CustomerPreparationResult(
            status="validation_failed",
            ready_for_planning=False,
            mapped_data=mapping.mapped_data,
            validation_issues=validation.issues,
        )

    return CustomerPreparationResult(
        status="ready",
        ready_for_planning=True,
        mapped_data=mapping.mapped_data,
        customer=validation.data,
    )
    