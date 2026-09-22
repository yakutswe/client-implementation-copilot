from typing import Any, Literal

from pydantic import BaseModel, Field

from backend.app.customer_workflow import (
    CustomerPreparationResult,
    prepare_customer,
)
from backend.app.knowledge_retriever import (
    KnowledgeMatch,
    search_knowledge,
)


class ImplementationStep(BaseModel):
    order: int
    title: str
    description: str


class ImplementationRisk(BaseModel):
    code: str
    severity: Literal["low", "medium", "high"]
    description: str
    mitigation: str


class ImplementationPlanResult(BaseModel):
    status: Literal[
        "customer_not_ready",
        "insufficient_evidence",
        "ready_for_review",
    ]
    objective: str
    preparation: CustomerPreparationResult
    evidence: list[KnowledgeMatch] = Field(default_factory=list)
    steps: list[ImplementationStep] = Field(default_factory=list)
    risks: list[ImplementationRisk] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)
    requires_human_approval: bool = False
    ready_for_execution: bool = False


ACTION_TEMPLATES = {
    "KB-MAP-001": ImplementationStep(
        order=1,
        title="Review schema mapping",
        description=(
            "Confirm that customer source fields map to the approved "
            "platform schema without unsupported or duplicate targets."
        ),
    ),
    "KB-VAL-001": ImplementationStep(
        order=2,
        title="Confirm validated customer record",
        description=(
            "Verify required customer fields, plan values, email format, "
            "and employee count before implementation planning."
        ),
    ),
    "KB-PLAN-001": ImplementationStep(
        order=3,
        title="Define implementation scope",
        description=(
            "Confirm data ownership, integration scope, sandbox access, "
            "success criteria, rollback expectations, and approver."
        ),
    ),
    "KB-SAFE-001": ImplementationStep(
        order=4,
        title="Request approval before execution",
        description=(
            "Present the proposed scope for human approval before any "
            "production write, configuration change, or integration action."
        ),
    ),
}


def build_implementation_plan(
    payload: dict[str, Any],
    objective: str,
) -> ImplementationPlanResult:
    """Build a cited plan proposal without executing external actions."""

    preparation = prepare_customer(payload)

    if not preparation.ready_for_planning:
        return ImplementationPlanResult(
            status="customer_not_ready",
            objective=objective,
            preparation=preparation,
        )

    primary_retrieval = search_knowledge(
        query=objective,
        top_k=3,
    )

    if not primary_retrieval.matches:
        return ImplementationPlanResult(
            status="insufficient_evidence",
            objective=objective,
            preparation=preparation,
        )

    policy_retrieval = search_knowledge(
        query="implementation planning deployment safety approval",
        top_k=4,
    )

    evidence_by_id = {
        match.id: match
        for match in (
            primary_retrieval.matches
            + policy_retrieval.matches
        )
    }
    evidence = sorted(
        evidence_by_id.values(),
        key=lambda match: match.id,
    )

    steps = [
        ACTION_TEMPLATES[document_id].model_copy()
        for document_id in ACTION_TEMPLATES
        if document_id in evidence_by_id
    ]

    risks = [
        ImplementationRisk(
            code="scope_drift",
            severity="high",
            description=(
                "The proposed implementation may move beyond the "
                "reviewed customer scope."
            ),
            mitigation=(
                "Require a new review whenever fields, permissions, "
                "or deployment actions change."
            ),
        ),
        ImplementationRisk(
            code="production_change",
            severity="high",
            description=(
                "A production change could affect customer systems."
            ),
            mitigation=(
                "Keep execution disabled until an authorized human "
                "approves the exact reviewed plan."
            ),
        ),
    ]

    return ImplementationPlanResult(
        status="ready_for_review",
        objective=objective,
        preparation=preparation,
        evidence=evidence,
        steps=steps,
        risks=risks,
        citations=[
            match.citation
            for match in evidence
        ],
        requires_human_approval=True,
        ready_for_execution=False,
    )