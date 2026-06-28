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

    def tree_pack(
        self,
        query: str,
        scope: str | None = None,
        limit: int = 8,
        depth: int = 1,
        include_raw: bool = True,
    ) -> str:
        return self.store.memory_tree_pack(
            query,
            scope=scope,
            limit=limit,
            depth=depth,
            include_raw=include_raw,
        )

    def context_builder_pack(
        self,
        query: str,
        scope: str | None = None,
        thread_id: str = "default",
        limit: int = 8,
    ) -> str:
        return self.store.context_builder_pack(
            query,
            scope=scope,
            thread_id=thread_id,
            limit=limit,
        )

    def record_turn(
        self,
        content: str,
        *,
        thread_id: str = "default",
        role: str = "user",
        actor: str = "user",
        scope: str = "professional",
        remember: bool = False,
        auto_approve: bool = False,
    ) -> dict[str, Any]:
        return self.store.record_turn(
            content,
            thread_id=thread_id,
            role=role,
            actor=actor,
            scope=scope,
            remember=remember,
            auto_approve=auto_approve,
        )

    def graph_nodes(
        self,
        scope: str | None = None,
        node_type: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        return self.store.list_graph_nodes(scope=scope, node_type=node_type, limit=limit)

    def optimize_graph(self, mode: str, scope: str = "professional") -> dict[str, Any]:
        return self.store.optimize_graph(mode, scope=scope)

    def export_profile(self, scope: str | None = None, project: str = "") -> dict[str, Any]:
        return self.store.export_profile(scope=scope, project=project)

    def import_profile(self, payload: dict[str, Any]) -> dict[str, int]:
        return self.store.import_profile(payload)

    def record_usage(
        self,
        *,
        provider: str = "openai",
        model: str,
        scope: str = "professional",
        thread_id: str = "",
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        cost: float = 0.0,
    ) -> str:
        return self.store.record_llm_usage(
            provider=provider,
            model=model,
            scope=scope,
            thread_id=thread_id,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost=cost,
        )

    def set_intro(self, content: str, scope: str = "professional") -> str:
        return self.store.upsert_profile_note(content, scope=scope, note_type="intro")

    def add_rule(self, content: str, scope: str = "professional") -> str:
        return self.store.upsert_profile_note(content, scope=scope, note_type="rule")

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
