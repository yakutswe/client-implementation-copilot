from typing import Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
)


class CustomerRecord(BaseModel):
    """Validated representation of one fictional customer."""

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    customer_id: str = Field(min_length=1)
    company_name: str = Field(min_length=1)
    contact_email: str
    plan: Literal["starter", "growth", "enterprise"]
    employee_count: int = Field(gt=0)

    @field_validator("contact_email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        local_part, separator, domain = value.partition("@")

        if not separator or not local_part or "." not in domain:
            raise ValueError("must be a valid email address")

        return value.lower()


class ValidationIssue(BaseModel):
    """One understandable validation problem."""

    field: str
    code: str
    message: str


class ValidationResult(BaseModel):
    """Structured result returned by the validator."""

    valid: bool
    data: CustomerRecord | None = None
    issues: list[ValidationIssue] = Field(default_factory=list)


def validate_customer(payload: dict[str, Any]) -> ValidationResult:
    """Validate customer data without using an AI model."""

    try:
        customer = CustomerRecord.model_validate(payload)

        return ValidationResult(
            valid=True,
            data=customer,
        )

    except ValidationError as error:
        issues = [
            ValidationIssue(
                field=".".join(str(part) for part in item["loc"]),
                code=item["type"],
                message=item["msg"],
            )
            for item in error.errors()
        ]

        return ValidationResult(
            valid=False,
            issues=issues,
        )