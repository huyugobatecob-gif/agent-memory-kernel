"""Minimal Hermes adapter example.

This file is not a Hermes plugin by itself. It shows the intended boundary:
Hermes orchestrates agents, while Agent Memory Kernel owns memory lifecycle.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_memory_kernel import MemoryStore


class HermesMemoryProvider:
    """Thin provider wrapper around MemoryStore."""

    def __init__(self, db_path: str | Path = ".memory/hermes-memory.db"):
        self.store = MemoryStore(db_path)
        self.store.init_db()

    def context_pack(self, query: str, scope: str | None = None, limit: int = 8) -> str:
        return self.store.context_pack(query, scope=scope, limit=limit)

    def remember(
        self,
        text: str,
        *,
        scope: str = "professional",
        actor: str = "hermes",
        source_ref: str = "",
        auto_approve: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self.store.remember(
            text,
            scope=scope,
            actor=actor,
            source_type="system",
            source_ref=source_ref,
            auto_approve=auto_approve,
            metadata=metadata,
        )

    def review_pending(self) -> list[dict[str, Any]]:
        return self.store.list_candidates("pending")

    def close(self) -> None:
        self.store.close()
