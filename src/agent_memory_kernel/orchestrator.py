"""High-level runtime orchestration boundary for Agent Memory Kernel.

The store remains the source of truth. This module gives external runtimes a
small service-shaped API for the complete memory turn lifecycle.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .store import MemoryStore


class MemoryOrchestrator:
    """Service facade for Router, prompt context, turn storage, and Keeper."""

    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    @classmethod
    def from_path(
        cls,
        db_path: str | Path = ".memory/memory.db",
        *,
        extractor: Any = None,
    ) -> "MemoryOrchestrator":
        store = MemoryStore(db_path, extractor=extractor)
        store.init_db()
        return cls(store)

    def before_turn(
        self,
        query: str,
        *,
        thread_id: str = "default",
        scope: str = "professional",
        user_id: str = "user_default",
        agent_id: str = "agent",
        model_id: str = "",
        mode: str = "chat",
        token_budget: int = 12000,
        requested_lanes: list[str] | None = None,
        allowed_scopes: list[str] | None = None,
        denied_scopes: list[str] | None = None,
        limit: int = 8,
        recent_messages: int = 6,
        enable_brain_style: bool = True,
    ) -> dict[str, Any]:
        """Build selected memory context before the main agent answers."""
        result = self.store.before_model_call(
            query,
            thread_id=thread_id,
            scope=scope,
            user_id=user_id,
            agent_id=agent_id,
            model_id=model_id,
            mode=mode,
            token_budget=token_budget,
            requested_lanes=requested_lanes,
            allowed_scopes=allowed_scopes,
            denied_scopes=denied_scopes,
            limit=limit,
            recent_messages=recent_messages,
            enable_brain_style=enable_brain_style,
        )
        return {
            "phase": "before_turn",
            "status": "ready",
            "query": query,
            "thread_id": thread_id,
            "scope": scope,
            **result,
        }

    def build_prompt_context(
        self,
        query: str,
        *,
        thread_id: str = "default",
        scope: str = "professional",
        user_id: str = "user_default",
        agent_id: str = "agent",
        model_id: str = "",
        mode: str = "chat",
        token_budget: int = 12000,
        requested_lanes: list[str] | None = None,
        allowed_scopes: list[str] | None = None,
        denied_scopes: list[str] | None = None,
        limit: int = 8,
        recent_messages: int = 6,
        enable_brain_style: bool = True,
    ) -> dict[str, Any]:
        """Return the agent-ready prompt envelope and its Router audit ids."""
        before = self.before_turn(
            query,
            thread_id=thread_id,
            scope=scope,
            user_id=user_id,
            agent_id=agent_id,
            model_id=model_id,
            mode=mode,
            token_budget=token_budget,
            requested_lanes=requested_lanes,
            allowed_scopes=allowed_scopes,
            denied_scopes=denied_scopes,
            limit=limit,
            recent_messages=recent_messages,
            enable_brain_style=enable_brain_style,
        )
        return {
            "phase": "build_prompt_context",
            "status": before["status"],
            "prompt_envelope": before["prompt_envelope"],
            "router_run_id": before["router_run_id"],
            "selected_branch_ids": before["selected_branch_ids"],
            "access_decisions": before["access_decisions"],
            "warnings": before["warnings"],
        }

    def retrieve_context(
        self,
        query: str,
        *,
        scope: str | None = None,
        limit: int = 8,
        depth: int = 1,
        include_raw: bool = True,
        raw_chars: int = 1600,
        actor: str = "agent",
    ) -> dict[str, Any]:
        """Retrieve expanded graph branches plus the markdown tree supplement."""
        tree = self.store.retrieve_tree(
            query,
            scope=scope,
            limit=limit,
            depth=depth,
            include_raw=include_raw,
            raw_chars=raw_chars,
            actor=actor,
        )
        return {
            "phase": "retrieve_context",
            "status": "ready",
            "query": query,
            "scope": tree.get("scope", scope or "all"),
            "tree": tree,
            "memory_tree_supplement": self.store.memory_tree_pack(
                query,
                scope=scope,
                limit=limit,
                depth=depth,
                include_raw=include_raw,
                raw_chars=raw_chars,
                actor=actor,
            ),
        }

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
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Persist one conversation turn through the canonical store path."""
        result = self.store.record_turn(
            content,
            thread_id=thread_id,
            role=role,
            actor=actor,
            scope=scope,
            remember=remember,
            auto_approve=auto_approve,
            metadata={**(metadata or {}), "orchestrator_phase": "record_turn"},
        )
        return {
            "phase": "record_turn",
            "status": "recorded",
            **result,
        }

    def keeper_analyze_turn(
        self,
        *,
        thread_id: str = "default",
        scope: str = "professional",
        user_id: str = "user_default",
        agent_id: str = "agent",
        model_id: str = "",
        user_text: str = "",
        assistant_text: str = "",
        turn_id: str = "",
        auto_approve: bool = False,
        keeper_mode: str = "sync",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Run or queue Keeper analysis for a completed exchange."""
        result = self.store.after_saved_turn(
            thread_id=thread_id,
            scope=scope,
            user_id=user_id,
            agent_id=agent_id,
            model_id=model_id,
            user_text=user_text,
            assistant_text=assistant_text,
            turn_id=turn_id,
            auto_approve=auto_approve,
            keeper_mode=keeper_mode,
            metadata={**(metadata or {}), "orchestrator_phase": "keeper_analyze_turn"},
        )
        return {
            "phase": "keeper_analyze_turn",
            **result,
        }

    def ingest_graph(
        self,
        updates: list[dict[str, Any]],
        *,
        scope: str = "professional",
        actor: str = "agent",
        source_ref: str = "",
        auto_approve: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Apply controlled graph updates through normal memory ingest.

        This baseline accepts Keeper-style update objects and turns each into a
        reviewable memory candidate. Approval then updates graph nodes, edges,
        summaries, and evidence through the same audited store path as any
        other memory.
        """
        if not isinstance(updates, list):
            raise TypeError("updates must be a list of graph update objects")
        results = []
        for index, update in enumerate(updates):
            if not isinstance(update, dict):
                raise TypeError("each graph update must be an object")
            text = self._graph_update_text(update)
            result = self.store.remember(
                text,
                scope=scope,
                actor=actor,
                source_type="system",
                source_ref=source_ref,
                auto_approve=auto_approve,
                metadata={
                    **(metadata or {}),
                    "orchestrator_phase": "ingest_graph",
                    "graph_update_index": index,
                    "graph_update": update,
                },
            )
            results.append(result)
        candidate_ids = [
            candidate["candidate_id"]
            for result in results
            for candidate in result.get("candidates", [])
        ]
        memory_ids = [
            candidate.get("memory_id")
            for result in results
            for candidate in result.get("candidates", [])
            if candidate.get("memory_id")
        ]
        return {
            "phase": "ingest_graph",
            "status": "ingested",
            "update_count": len(updates),
            "candidate_ids": candidate_ids,
            "memory_ids": memory_ids,
            "results": results,
        }

    def after_turn(
        self,
        *,
        thread_id: str = "default",
        scope: str = "professional",
        user_id: str = "user_default",
        agent_id: str = "agent",
        model_id: str = "",
        user_text: str = "",
        assistant_text: str = "",
        turn_id: str = "",
        auto_approve: bool = False,
        keeper_mode: str = "sync",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Persist the exchange and run/queue Keeper after the answer."""
        result = self.keeper_analyze_turn(
            thread_id=thread_id,
            scope=scope,
            user_id=user_id,
            agent_id=agent_id,
            model_id=model_id,
            user_text=user_text,
            assistant_text=assistant_text,
            turn_id=turn_id,
            auto_approve=auto_approve,
            keeper_mode=keeper_mode,
            metadata={**(metadata or {}), "orchestrator_phase": "after_turn"},
        )
        return {
            "phase": "after_turn",
            **{key: value for key, value in result.items() if key != "phase"},
        }

    def close(self) -> None:
        self.store.close()

    @staticmethod
    def _graph_update_text(update: dict[str, Any]) -> str:
        text = str(update.get("text", "") or update.get("memory", "")).strip()
        if text:
            return text

        kind = str(update.get("kind", "") or update.get("type", "fact")).strip() or "fact"
        label = str(update.get("label", "") or update.get("node", "")).strip()
        summary = str(update.get("summary", "") or update.get("description", "")).strip()
        relation = str(update.get("relation", "") or update.get("edge", "")).strip()
        target = str(update.get("target", "") or update.get("to", "")).strip()
        evidence = str(update.get("evidence", "") or update.get("source_quote", "")).strip()

        parts = [f"{kind.title()}:"]
        if label:
            parts.append(label)
        if relation and target:
            parts.append(f"{relation} {target}")
        if summary:
            parts.append(summary)
        if evidence:
            parts.append(f"Evidence: {evidence}")
        rendered = " ".join(parts).strip()
        if rendered == f"{kind.title()}:":
            raise ValueError("graph update must include text, label, summary, relation, or evidence")
        return rendered
