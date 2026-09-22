import pytest

from evals.retrieval_evaluator import (
    RetrievalEvaluationCase,
    evaluate_retrieval,
    load_retrieval_evaluation_cases,
)


def test_loads_retrieval_evaluation_cases() -> None:
    cases = load_retrieval_evaluation_cases()

    assert len(cases) == 9
    assert len({case.case_id for case in cases}) == 9


def test_baseline_retrieval_evaluation_passes() -> None:
    report = evaluate_retrieval(top_k=3)

    assert report.total_cases == 9
    assert report.top_1_correct_count == 9
    assert report.hit_at_k_count == 9
    assert report.top_1_accuracy == 1.0
    assert report.hit_rate_at_k == 1.0


def test_reports_failed_retrieval_case() -> None:
    cases = [
        RetrievalEvaluationCase(
            case_id="RET-FAIL",
            query="mapping schema fields",
            expected_document_id="KB-SAFE-001",
        )
    ]

    report = evaluate_retrieval(
        cases=cases,
        top_k=1,
    )

    assert report.total_cases == 1
    assert report.top_1_correct_count == 0
    assert report.hit_at_k_count == 0
    assert report.top_1_accuracy == 0.0
    assert report.hit_rate_at_k == 0.0
    assert report.cases[0].top_1_correct is False
    assert report.cases[0].hit_at_k is False


def test_handles_empty_evaluation_dataset() -> None:
    report = evaluate_retrieval(
        cases=[],
        top_k=3,
    )

    assert report.total_cases == 0
    assert report.top_1_accuracy == 0.0
    assert report.hit_rate_at_k == 0.0
    assert report.cases == []


def test_rejects_invalid_evaluation_limit() -> None:
    with pytest.raises(
        ValueError,
        match="top_k must be at least 1",
    ):
        evaluate_retrieval(top_k=0)