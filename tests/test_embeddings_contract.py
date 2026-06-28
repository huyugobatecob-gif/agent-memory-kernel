from __future__ import annotations

import unittest
from typing import Sequence

from agent_memory_kernel.embeddings import (
    EmbeddedDocument,
    LocalEmbeddingProvider,
    cosine_similarity,
    lexical_embedding,
    rank_documents,
    semantic_similarity,
)


class FakeProvider:
    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def _embed(self, text: str) -> list[float]:
        lowered = text.lower()
        vector = [0.0, 0.0, 0.0]
        if any(term in lowered for term in ["conversion", "signup", "uplift"]):
            vector[0] = 1.0
        if any(term in lowered for term in ["backup", "restore", "sqlite"]):
            vector[1] = 1.0
        if any(term in lowered for term in ["style", "tone", "voice"]):
            vector[2] = 1.0
        return vector


class EmbeddingsContractTests(unittest.TestCase):
    def test_local_embedding_provider_is_deterministic(self) -> None:
        provider = LocalEmbeddingProvider(dims=16)

        first = provider.embed(["SEO loop success"])
        second = provider.embed(["SEO loop success"])

        self.assertEqual(first, second)
        self.assertEqual(len(first[0]), 16)
        self.assertGreater(cosine_similarity(first[0], second[0]), 0.99)

    def test_semantic_similarity_keeps_dependency_free_rerank(self) -> None:
        self.assertGreater(
            semantic_similarity("successful SEO loop", "winning content iteration"),
            0,
        )

    def test_rank_documents_uses_stored_local_embeddings_without_provider(self) -> None:
        documents = [
            EmbeddedDocument(
                "mem_success",
                "Decision: SEO loop success came from title refresh.",
                embedding=lexical_embedding("Decision: SEO loop success came from title refresh."),
            ),
            EmbeddedDocument(
                "mem_backup",
                "Decision: backup before SQLite migration.",
                embedding=lexical_embedding("Decision: backup before SQLite migration."),
            ),
        ]

        ranked = rank_documents("SEO success loop", documents, limit=2)

        self.assertEqual(ranked[0]["document_id"], "mem_success")
        self.assertEqual(ranked[0]["embedding_source"], "local")

    def test_rank_documents_can_use_provider_embeddings(self) -> None:
        documents = [
            EmbeddedDocument("mem_signup", "Pattern: signup uplift after copy rewrite."),
            EmbeddedDocument("mem_backup", "Rule: backup SQLite before restore."),
        ]

        ranked = rank_documents(
            "conversion lift",
            documents,
            provider=FakeProvider(),
            limit=2,
            min_similarity=0.1,
        )

        self.assertEqual(ranked[0]["document_id"], "mem_signup")
        self.assertEqual(ranked[0]["embedding_source"], "provider")


if __name__ == "__main__":
    unittest.main()
