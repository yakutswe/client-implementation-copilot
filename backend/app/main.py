from typing import Any

from fastapi import FastAPI

from backend.app.schema_validator import (
    ValidationResult,
    validate_customer,
)


app = FastAPI(
    title="DeployBridge API",
    description="Customer implementation validation and planning API.",
    version="0.1.0",
)

@app.get("/")
def root() -> dict[str, str]:
    """Provide basic API information."""

    return {
        "name": "DeployBridge API",
        "status": "running",
        "documentation": "/docs",
    }
    
@app.get("/health")
def health_check() -> dict[str, str]:
    """Confirm that the API is running."""

    return {
        "status": "ok",
        "service": "deploybridge-api",
    }


@app.post(
    "/api/v1/customers/validate",
    response_model=ValidationResult,
)
def validate_customer_payload(
    payload: dict[str, Any],
) -> ValidationResult:
    """Validate fictional customer data."""

    return validate_customer(payload)
