"""Minimal Hermes adapter example.

This file is not a Hermes plugin by itself. It shows the intended boundary:
Hermes orchestrates agents, while Agent Memory Kernel owns memory lifecycle.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_memory_kernel import (
    MemoryStore,
    assert_acceptance_suite,
    assert_conformance_spec_shape,
    assert_conformance_suite,
    assert_contract_shape,
    conformance_spec,
    memory_contract,
    run_acceptance_suite,
    run_conformance_suite,
    seed_acceptance_fixture,
    seed_conformance_fixture,
)


class HermesMemoryProvider:
    """Thin provider wrapper around MemoryStore."""

    def __init__(self, db_path: str | Path = ".memory/hermes-memory.db", *, extractor: Any = None):
        self.store = MemoryStore(db_path, extractor=extractor)
        self.store.init_db()

    def memory_contract(self) -> dict[str, Any]:
        return memory_contract()

    def assert_contract(self) -> dict[str, Any]:
        return assert_contract_shape()

    def seed_acceptance(self) -> dict[str, Any]:
        return seed_acceptance_fixture(self.store)

    def run_acceptance(self) -> dict[str, Any]:
        return run_acceptance_suite(self.store)

    def assert_acceptance(self) -> dict[str, Any]:
        return assert_acceptance_suite(self.store)

    def conformance_spec(self) -> dict[str, Any]:
        return conformance_spec()

    def assert_conformance_spec(self) -> dict[str, Any]:
        return assert_conformance_spec_shape()

    def seed_conformance(self) -> dict[str, Any]:
        return seed_conformance_fixture(self.store)

    def run_conformance(self) -> dict[str, Any]:
        return run_conformance_suite(self.store)

    def assert_conformance(self) -> dict[str, Any]:
        return assert_conformance_suite(self.store)

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

    def brain_style_append(self, scope: str = "professional") -> dict[str, Any]:
        return self.store.brain_style_append(scope=scope)

    def read_time_policy(
        self,
        *,
        scope: str | None = None,
        token_budget: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        return self.store.read_time_policy(
            scope=scope,
            token_budget=token_budget,
            limit=limit,
        )

    def router_runs(
        self,
        *,
        thread_id: str | None = None,
        scope: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        return self.store.list_router_runs(thread_id=thread_id, scope=scope, limit=limit)

    def explain_router_run(self, router_run_id: str) -> dict[str, Any]:
        return self.store.explain_router_run(router_run_id)

    def record_router_feedback(
        self,
        router_run_id: str,
        *,
        memory_id: str = "",
        branch_id: str = "",
        rating: str = "neutral",
        score: float | None = None,
        actor: str = "reviewer",
        reason: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self.store.record_router_feedback(
            router_run_id,
            memory_id=memory_id,
            branch_id=branch_id,
            rating=rating,
            score=score,
            actor=actor,
            reason=reason,
            metadata=metadata,
        )

    def router_feedback(
        self,
        *,
        router_run_id: str | None = None,
        memory_id: str | None = None,
        rating: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        return self.store.list_router_feedback(
            router_run_id=router_run_id,
            memory_id=memory_id,
            rating=rating,
            limit=limit,
        )

    def memory_quality_report(
        self,
        *,
        scope: str | None = None,
        limit: int = 10,
    ) -> dict[str, Any]:
        return self.store.memory_quality_report(scope=scope, limit=limit)

    def current_best_report(
        self,
        query: str = "",
        *,
        scope: str | None = None,
        limit: int = 8,
    ) -> dict[str, Any]:
        return self.store.current_best_report(query, scope=scope, limit=limit)

    def before_model_call(
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
        enable_brain_style: bool = True,
    ) -> dict[str, Any]:
        return self.store.before_model_call(
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
            enable_brain_style=enable_brain_style,
        )

    def after_saved_turn(
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
        return self.store.after_saved_turn(
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
            metadata=metadata,
        )

    def shadow_turn(
        self,
        query: str,
        *,
        thread_id: str = "default",
        scope: str = "professional",
        user_id: str = "user_default",
        agent_id: str = "agent",
        model_id: str = "",
        mode: str = "shadow",
        token_budget: int = 12000,
        requested_lanes: list[str] | None = None,
        allowed_scopes: list[str] | None = None,
        denied_scopes: list[str] | None = None,
        limit: int = 8,
        user_text: str = "",
        assistant_text: str = "",
        keeper_mode: str = "sync",
        enable_brain_style: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self.store.shadow_turn(
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
            user_text=user_text,
            assistant_text=assistant_text,
            keeper_mode=keeper_mode,
            enable_brain_style=enable_brain_style,
            metadata=metadata,
        )

    def shadow_traces(
        self,
        *,
        thread_id: str | None = None,
        scope: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        return self.store.list_shadow_traces(thread_id=thread_id, scope=scope, limit=limit)

    def evaluate_shadow_trace(
        self,
        shadow_trace_id: str,
        *,
        expected: dict[str, Any] | None = None,
        actor: str = "reviewer",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self.store.evaluate_shadow_trace(
            shadow_trace_id,
            expected=expected,
            actor=actor,
            metadata=metadata,
        )

    def shadow_evals(
        self,
        *,
        shadow_trace_id: str | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        return self.store.list_shadow_evals(
            shadow_trace_id=shadow_trace_id,
            status=status,
            limit=limit,
        )

    def supersede_memory(
        self,
        old_memory_id: str,
        new_memory_id: str,
        *,
        actor: str = "hermes",
        reason: str = "",
    ) -> dict[str, Any]:
        return self.store.supersede_memory(
            old_memory_id,
            new_memory_id,
            actor=actor,
            reason=reason,
        )

    def record_memory_conflict(
        self,
        memory_id: str,
        other_memory_id: str,
        *,
        relation: str = "conflicts_with",
        winner_memory_id: str = "",
        actor: str = "hermes",
        reason: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self.store.record_memory_conflict(
            memory_id,
            other_memory_id,
            relation=relation,
            winner_memory_id=winner_memory_id,
            actor=actor,
            reason=reason,
            metadata=metadata,
        )

    def memory_revisions(self, memory_id: str, limit: int = 50) -> list[dict[str, Any]]:
        return self.store.list_memory_revisions(memory_id, limit=limit)

    def rollback_memory(
        self,
        memory_id: str,
        *,
        revision_id: str = "",
        actor: str = "hermes",
        reason: str = "",
    ) -> dict[str, Any]:
        return self.store.rollback_memory(
            memory_id,
            revision_id=revision_id,
            actor=actor,
            reason=reason,
        )

    def memory_conflicts(
        self,
        *,
        status: str | None = None,
        scope: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        return self.store.list_memory_conflicts(status=status, scope=scope, limit=limit)

    def record_outcome(
        self,
        *,
        project: str,
        outcome_status: str,
        hypothesis: str = "",
        action: str = "",
        result: str = "",
        cause: str = "",
        lesson: str = "",
        next_recommendation: str = "",
        loop_id: str = "",
        score: float = 0.0,
        scope: str = "professional",
        actor: str = "hermes",
        auto_approve: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self.store.record_outcome(
            project=project,
            outcome_status=outcome_status,
            hypothesis=hypothesis,
            action=action,
            result=result,
            cause=cause,
            lesson=lesson,
            next_recommendation=next_recommendation,
            loop_id=loop_id,
            score=score,
            scope=scope,
            actor=actor,
            auto_approve=auto_approve,
            metadata=metadata,
        )

    def outcome_pack(self, project: str, scope: str = "professional", limit: int = 8) -> str:
        return self.store.outcome_pack(project=project, scope=scope, limit=limit)

    def outcomes(
        self,
        *,
        project: str | None = None,
        outcome_status: str | None = None,
        scope: str | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        return self.store.list_outcomes(
            project=project,
            outcome_status=outcome_status,
            scope=scope,
            status=status,
            limit=limit,
        )

    def process_keeper_jobs(self, limit: int = 10, actor: str = "hermes-worker") -> dict[str, Any]:
        return self.store.process_keeper_jobs(limit=limit, actor=actor)

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

    def set_write_policy(
        self,
        *,
        agent_id: str = "*",
        scope: str = "*",
        action: str = "*",
        decision: str = "allow",
        reason: str = "",
        metadata: dict[str, Any] | None = None,
        actor: str = "hermes-admin",
    ) -> dict[str, Any]:
        return self.store.set_write_policy(
            agent_id=agent_id,
            scope=scope,
            action=action,
            decision=decision,
            reason=reason,
            metadata=metadata,
            actor=actor,
        )

    def write_policies(
        self,
        *,
        agent_id: str | None = None,
        scope: str | None = None,
        action: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        return self.store.list_write_policies(
            agent_id=agent_id,
            scope=scope,
            action=action,
            limit=limit,
        )

    def resolve_write_policy(self, actor: str, scope: str, action: str) -> dict[str, Any]:
        return self.store.resolve_write_policy(actor, scope, action)

    def review_pending(self) -> list[dict[str, Any]]:
        return self.store.list_candidates("pending")

    def close(self) -> None:
        self.store.close()
