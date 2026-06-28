"""Provider-neutral embedding helpers for memory retrieval.

The default path is deterministic and dependency-free. Hosted deployments can
pass an embedding provider with the same small interface when they need larger
corpora or model-native vectors.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any, Protocol, Sequence


TOKEN_RE = re.compile(r"[A-Za-zА-Яа-яЁё0-9_.-]{2,}")
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "be",
    "but",
    "by",
    "for",
    "from",
    "has",
    "have",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "what",
    "when",
    "where",
    "was",
    "were",
    "with",
    "you",
    "your",
    "и",
    "в",
    "во",
    "на",
    "по",
    "с",
    "со",
    "для",
    "это",
    "как",
    "что",
    "не",
    "или",
    "вот",
    "при",
    "про",
    "чтобы",
}

SEMANTIC_GROUPS: dict[str, set[str]] = {
    "agent": {
        "agent",
        "agents",
        "assistant",
        "assistants",
        "бот",
        "агент",
        "агенты",
        "ассистент",
    },
    "failure": {
        "avoid",
        "bad",
        "blocked",
        "broken",
        "bug",
        "error",
        "fail",
        "failed",
        "failure",
        "failing",
        "gotcha",
        "issue",
        "negative",
        "outdated",
        "problem",
        "regression",
        "risk",
        "stale",
        "unsuccessful",
        "worse",
        "неудача",
        "неудачный",
        "ошибка",
        "проблема",
        "провал",
    },
    "loop": {
        "attempt",
        "experiment",
        "iteration",
        "loop",
        "plan",
        "planning",
        "trial",
        "workflow",
        "итерация",
        "луп",
        "петля",
        "план",
        "попытка",
    },
    "memory": {
        "context",
        "history",
        "memory",
        "provenance",
        "recall",
        "remember",
        "retrieve",
        "source",
        "вспомнить",
        "история",
        "контекст",
        "память",
    },
    "project": {
        "client",
        "domain",
        "project",
        "repo",
        "site",
        "workspace",
        "домен",
        "клиент",
        "проект",
        "репозиторий",
        "сайт",
    },
    "success": {
        "better",
        "effective",
        "good",
        "improved",
        "positive",
        "reusable",
        "success",
        "successful",
        "succeed",
        "worked",
        "winning",
        "wins",
        "выигрыш",
        "удачно",
        "успех",
    },
    "seo": {
        "content",
        "indexing",
        "internal",
        "keyword",
        "keywords",
        "link",
        "links",
        "organic",
        "page",
        "refresh",
        "seo",
        "serp",
        "title",
        "titles",
        "контент",
        "ключи",
        "семантика",
        "сео",
    },
}
SEMANTIC_ALIASES = {
    alias: group
    for group, aliases in SEMANTIC_GROUPS.items()
    for alias in aliases
}


class EmbeddingProvider(Protocol):
    """Minimal provider contract for optional hosted embedding backends."""

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        """Return one vector per input text."""


@dataclass(frozen=True)
class EmbeddedDocument:
    document_id: str
    text: str
    embedding: list[float] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class LocalEmbeddingProvider:
    """Deterministic fallback provider used by tests and local operation."""

    def __init__(self, *, dims: int = 32) -> None:
        self.dims = dims

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        return [lexical_embedding(text, dims=self.dims) for text in texts]


def query_tokens(text: str) -> list[str]:
    tokens: list[str] = []
    for token in TOKEN_RE.findall((text or "").lower()):
        if token not in STOPWORDS and token not in tokens:
            tokens.append(token)
    return tokens[:40]


def semantic_terms(text: str) -> set[str]:
    """Return dependency-free semantic terms for local reranking."""
    terms: set[str] = set()
    for token in query_tokens(text):
        terms.add(token)
        alias = SEMANTIC_ALIASES.get(token)
        if alias:
            terms.add(alias)
        if token.endswith("ing") and len(token) > 5:
            terms.add(token[:-3])
        if token.endswith("ed") and len(token) > 4:
            terms.add(token[:-2])
        if token.endswith("s") and len(token) > 4:
            terms.add(token[:-1])
    return terms


def semantic_similarity(left: str, right: str) -> float:
    """Return a small deterministic similarity score between two texts."""
    left_terms = semantic_terms(left)
    right_terms = semantic_terms(right)
    if not left_terms or not right_terms:
        return 0.0
    intersection = left_terms & right_terms
    if not intersection:
        return 0.0
    denominator = (len(left_terms) * len(right_terms)) ** 0.5
    return round(len(intersection) / denominator, 6)


def lexical_embedding(text: str, *, dims: int = 32) -> list[float]:
    """Small local embedding placeholder compatible with future vector search."""
    vector = [0.0] * dims
    tokens = query_tokens(text)
    if not tokens:
        return vector
    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = digest[0] % dims
        sign = 1.0 if digest[1] % 2 == 0 else -1.0
        vector[index] += sign
    magnitude = sum(value * value for value in vector) ** 0.5
    if not magnitude:
        return vector
    return [round(value / magnitude, 6) for value in vector]


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    """Return cosine similarity for two vectors with defensive shape handling."""
    size = min(len(left), len(right))
    if not size:
        return 0.0
    dot = sum(float(left[index]) * float(right[index]) for index in range(size))
    left_norm = sum(float(left[index]) ** 2 for index in range(size)) ** 0.5
    right_norm = sum(float(right[index]) ** 2 for index in range(size)) ** 0.5
    if not left_norm or not right_norm:
        return 0.0
    return round(dot / (left_norm * right_norm), 6)


def rank_documents(
    query: str,
    documents: Sequence[EmbeddedDocument],
    *,
    provider: EmbeddingProvider | None = None,
    dims: int = 32,
    limit: int = 8,
    min_similarity: float = 0.0,
) -> list[dict[str, Any]]:
    """Rank documents with local vectors or a caller-supplied provider.

    If a provider is supplied, query and document vectors are computed together
    to avoid mixing vector spaces. Without a provider, stored document vectors
    can be reused and missing ones fall back to `lexical_embedding`.
    """
    if not query.strip() or not documents:
        return []
    limit = max(1, int(limit or 1))
    if provider is not None:
        vectors = provider.embed([query, *[document.text for document in documents]])
        if len(vectors) != len(documents) + 1:
            raise ValueError("embedding provider must return one vector per input text")
        query_vector = vectors[0]
        document_vectors = vectors[1:]
        source = "provider"
    else:
        query_vector = lexical_embedding(query, dims=dims)
        document_vectors = [
            document.embedding
            if document.embedding is not None
            else lexical_embedding(document.text, dims=dims)
            for document in documents
        ]
        source = "local"

    ranked: list[dict[str, Any]] = []
    for document, vector in zip(documents, document_vectors):
        similarity = cosine_similarity(query_vector, vector)
        if similarity < min_similarity:
            continue
        ranked.append(
            {
                "document_id": document.document_id,
                "score": round(similarity * 100.0, 4),
                "similarity": similarity,
                "embedding_source": source,
                "metadata": dict(document.metadata),
            }
        )
    ranked.sort(key=lambda item: (-item["score"], item["document_id"]))
    return ranked[:limit]
