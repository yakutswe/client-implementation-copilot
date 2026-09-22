from typing import Any

from fastapi import FastAPI

from backend.app.schema_mapper import MappingResult, map_customer_fields
from backend.app.schema_validator import ValidationResult, validate_customer


app = FastAPI(
    title="DeployBridge API",
    description="Customer implementation validation and planning API.",
    version="0.2.0",
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": "DeployBridge API",
        "status": "running",
        "documentation": "/docs",
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "deploybridge-api",
    }


@app.post(
    "/api/v1/customers/map",
    response_model=MappingResult,
)
def map_customer_payload(payload: dict[str, Any]) -> MappingResult:
    """Map source customer fields into the DeployBridge schema."""

    return map_customer_fields(payload)


@app.post(
    "/api/v1/customers/validate",
    response_model=ValidationResult,
)
def validate_customer_payload(payload: dict[str, Any]) -> ValidationResult:
    """Validate customer data already using the DeployBridge schema."""

    return validate_customer(payload)
