import json
import re
from pathlib import Path

from pydantic import BaseModel, Field


KNOWLEDGE_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "knowledge"
    / "implementation_articles.json"
)

STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "for",
    "how",
    "in",
    "is",
    "of",
    "on",
    "the",
    "to",
    "what",
    "when",
    "with",
}


class KnowledgeDocument(BaseModel):
    id: str
    title: str
    source: str
    tags: list[str]
    content: str


class KnowledgeMatch(BaseModel):
    id: str
    title: str
    source: str
    citation: str
    content: str
    score: int
    matched_terms: list[str] = Field(default_factory=list)


class RetrievalResult(BaseModel):
    query: str
    matches: list[KnowledgeMatch] = Field(default_factory=list)


def tokenize(text: str) -> set[str]:
    """Convert text into normalized searchable terms."""

    terms = re.findall(r"[a-z0-9_]+", text.lower())

    return {
        term
        for term in terms
        if len(term) > 1 and term not in STOP_WORDS
    }


def load_knowledge_documents(
    path: Path = KNOWLEDGE_PATH,
) -> list[KnowledgeDocument]:
    """Load and validate the local implementation knowledge base."""

    raw_documents = json.loads(path.read_text(encoding="utf-8"))

    return [
        KnowledgeDocument.model_validate(document)
        for document in raw_documents
    ]


def search_knowledge(
    query: str,
    top_k: int = 3,
    documents: list[KnowledgeDocument] | None = None,
) -> RetrievalResult:
    """Return the highest-scoring documents with citations."""

    query_terms = tokenize(query)

    if not query_terms or top_k < 1:
        return RetrievalResult(query=query)

    active_documents = documents or load_knowledge_documents()
    matches: list[KnowledgeMatch] = []

    for document in active_documents:
        title_terms = tokenize(document.title)
        tag_terms = tokenize(" ".join(document.tags))
        content_terms = tokenize(document.content)

        title_matches = query_terms & title_terms
        tag_matches = query_terms & tag_terms
        content_matches = query_terms & content_terms

        score = (
            len(title_matches) * 3
            + len(tag_matches) * 2
            + len(content_matches)
        )

        if score == 0:
            continue

        matched_terms = sorted(
            title_matches | tag_matches | content_matches
        )

        matches.append(
            KnowledgeMatch(
                id=document.id,
                title=document.title,
                source=document.source,
                citation=f"{document.id} — {document.source}",
                content=document.content,
                score=score,
                matched_terms=matched_terms,
            )
        )

    matches.sort(key=lambda match: (-match.score, match.id))

    return RetrievalResult(
        query=query,
        matches=matches[:top_k],
    )