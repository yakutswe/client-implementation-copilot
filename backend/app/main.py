from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from backend.app.customer_workflow import (
    CustomerPreparationResult,
    prepare_customer,
)
from backend.app.knowledge_retriever import (
    RetrievalResult,
    search_knowledge,
)
from backend.app.schema_mapper import MappingResult, map_customer_fields
from backend.app.schema_validator import ValidationResult, validate_customer


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(min_length=2, max_length=500)
    top_k: int = Field(default=3, ge=1, le=10)


app = FastAPI(
    title="DeployBridge API",
    description="Customer implementation validation and planning API.",
    version="0.4.0",
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
    "/api/v1/knowledge/search",
    response_model=RetrievalResult,
)
def search_implementation_knowledge(
    request: KnowledgeSearchRequest,
) -> RetrievalResult:
    """Search cited implementation knowledge."""

    return search_knowledge(
        query=request.query,
        top_k=request.top_k,
    )


@app.post(
    "/api/v1/customers/prepare",
    response_model=CustomerPreparationResult,
)
def prepare_customer_payload(
    payload: dict[str, Any],
) -> CustomerPreparationResult:
    """Map and validate customer data before planning."""

    return prepare_customer(payload)


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