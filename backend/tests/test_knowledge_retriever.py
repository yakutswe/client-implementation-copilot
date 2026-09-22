from backend.app.knowledge_retriever import (
    load_knowledge_documents,
    search_knowledge,
)


def test_loads_valid_knowledge_documents() -> None:
    documents = load_knowledge_documents()

    assert len(documents) == 4
    assert len({document.id for document in documents}) == 4
    assert all(document.source.startswith("docs://") for document in documents)


def test_ranks_mapping_guide_first() -> None:
    result = search_knowledge(
        "mapping schema fields integration",
    )

    assert result.matches
    assert result.matches[0].id == "KB-MAP-001"
    assert result.matches[0].score > 0
    assert "schema" in result.matches[0].matched_terms
    assert result.matches[0].citation == (
        "KB-MAP-001 — docs://deploybridge/field-mapping"
    )


def test_ranks_safety_policy_first() -> None:
    result = search_knowledge(
        "production approval audit safety",
    )

    assert result.matches
    assert result.matches[0].id == "KB-SAFE-001"
    assert {
        "production",
        "approval",
        "audit",
        "safety",
    }.issubset(set(result.matches[0].matched_terms))


def test_respects_result_limit() -> None:
    result = search_knowledge(
        "customer implementation",
        top_k=2,
    )

    assert len(result.matches) <= 2
    assert all(match.citation.startswith(match.id) for match in result.matches)


def test_returns_no_results_for_unrelated_query() -> None:
    result = search_knowledge(
        "weather forecast rainfall",
    )

    assert result.query == "weather forecast rainfall"
    assert result.matches == []