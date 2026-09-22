import json
from pathlib import Path

from pydantic import BaseModel, Field

from backend.app.knowledge_retriever import search_knowledge


EVALUATION_PATH = Path(__file__).resolve().parent / "retrieval_cases.json"


class RetrievalEvaluationCase(BaseModel):
    case_id: str
    query: str
    expected_document_id: str | None


class RetrievalCaseResult(BaseModel):
    case_id: str
    query: str
    expected_document_id: str | None
    retrieved_document_ids: list[str] = Field(default_factory=list)
    top_1_correct: bool
    hit_at_k: bool


class RetrievalEvaluationReport(BaseModel):
    total_cases: int
    top_1_correct_count: int
    hit_at_k_count: int
    top_1_accuracy: float
    hit_rate_at_k: float
    cases: list[RetrievalCaseResult] = Field(default_factory=list)


def load_retrieval_evaluation_cases(
    path: Path = EVALUATION_PATH,
) -> list[RetrievalEvaluationCase]:
    """Load and validate the retrieval evaluation dataset."""

    raw_cases = json.loads(path.read_text(encoding="utf-8"))

    return [
        RetrievalEvaluationCase.model_validate(case)
        for case in raw_cases
    ]


def evaluate_retrieval(
    cases: list[RetrievalEvaluationCase] | None = None,
    top_k: int = 3,
) -> RetrievalEvaluationReport:
    """Evaluate deterministic retrieval against expected documents."""

    if top_k < 1:
        raise ValueError("top_k must be at least 1")

    active_cases = (
        cases
        if cases is not None
        else load_retrieval_evaluation_cases()
    )

    case_results: list[RetrievalCaseResult] = []

    for case in active_cases:
        retrieval = search_knowledge(
            query=case.query,
            top_k=top_k,
        )
        retrieved_ids = [
            match.id
            for match in retrieval.matches
        ]

        if case.expected_document_id is None:
            top_1_correct = not retrieved_ids
            hit_at_k = not retrieved_ids
        else:
            top_1_correct = (
                bool(retrieved_ids)
                and retrieved_ids[0] == case.expected_document_id
            )
            hit_at_k = case.expected_document_id in retrieved_ids

        case_results.append(
            RetrievalCaseResult(
                case_id=case.case_id,
                query=case.query,
                expected_document_id=case.expected_document_id,
                retrieved_document_ids=retrieved_ids,
                top_1_correct=top_1_correct,
                hit_at_k=hit_at_k,
            )
        )

    total_cases = len(case_results)
    top_1_correct_count = sum(
        result.top_1_correct
        for result in case_results
    )
    hit_at_k_count = sum(
        result.hit_at_k
        for result in case_results
    )

    return RetrievalEvaluationReport(
        total_cases=total_cases,
        top_1_correct_count=top_1_correct_count,
        hit_at_k_count=hit_at_k_count,
        top_1_accuracy=(
            top_1_correct_count / total_cases
            if total_cases
            else 0.0
        ),
        hit_rate_at_k=(
            hit_at_k_count / total_cases
            if total_cases
            else 0.0
        ),
        cases=case_results,
    )


if __name__ == "__main__":
    report = evaluate_retrieval()
    print(report.model_dump_json(indent=2))