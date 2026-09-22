from backend.app.implementation_planner import build_implementation_plan


VALID_CUSTOMER = {
    "id": "cust-501",
    "company": "Northstar Logistics",
    "email": "ops@northstar.example",
    "tier": "enterprise",
    "headcount": 250,
}


def test_refuses_plan_when_customer_is_not_ready() -> None:
    result = build_implementation_plan(
        payload={
            "id": "cust-502",
            "company": "Incomplete Customer",
        },
        objective="implementation planning",
    )

    assert result.status == "customer_not_ready"
    assert result.preparation.ready_for_planning is False
    assert result.evidence == []
    assert result.steps == []
    assert result.requires_human_approval is False
    assert result.ready_for_execution is False


def test_refuses_plan_when_evidence_is_unavailable() -> None:
    result = build_implementation_plan(
        payload=VALID_CUSTOMER,
        objective="weather forecast rainfall",
    )

    assert result.status == "insufficient_evidence"
    assert result.preparation.ready_for_planning is True
    assert result.evidence == []
    assert result.steps == []
    assert result.citations == []
    assert result.ready_for_execution is False


def test_builds_grounded_plan_for_human_review() -> None:
    result = build_implementation_plan(
        payload=VALID_CUSTOMER,
        objective=(
            "Prepare implementation onboarding with sandbox, "
            "rollback, safety, and approval"
        ),
    )

    evidence_ids = {
        match.id
        for match in result.evidence
    }

    assert result.status == "ready_for_review"
    assert result.preparation.ready_for_planning is True
    assert "KB-PLAN-001" in evidence_ids
    assert "KB-SAFE-001" in evidence_ids
    assert result.steps
    assert result.risks
    assert result.citations
    assert result.requires_human_approval is True
    assert result.ready_for_execution is False


def test_plan_is_deterministic_and_fully_cited() -> None:
    objective = "implementation planning deployment safety approval"

    first = build_implementation_plan(
        payload=VALID_CUSTOMER,
        objective=objective,
    )
    second = build_implementation_plan(
        payload=VALID_CUSTOMER,
        objective=objective,
    )

    assert first.model_dump() == second.model_dump()
    assert len(first.citations) == len(first.evidence)
    assert all(
        citation.startswith(match.id)
        for citation, match in zip(
            first.citations,
            first.evidence,
            strict=True,
        )
    )
    assert all(
        risk.severity == "high"
        for risk in first.risks
    )
    assert first.ready_for_execution is False