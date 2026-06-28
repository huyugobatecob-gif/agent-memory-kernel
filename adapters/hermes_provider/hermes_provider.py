"""Minimal Hermes adapter example.

This file is not a Hermes plugin by itself. It shows the intended boundary:
Hermes orchestrates agents, while Agent Memory Kernel owns memory lifecycle.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_memory_kernel import (
    MemoryOrchestrator,
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
        self.orchestrator = MemoryOrchestrator(self.store)

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

    def context_pack(
        self,
        query: str,
        scope: str | None = None,
        limit: int = 8,
        actor: str = "hermes",
    ) -> str:
        return self.store.context_pack(query, scope=scope, limit=limit, actor=actor)

    def tree_pack(
        self,
        query: str,
        scope: str | None = None,
        limit: int = 8,
        depth: int = 1,
        include_raw: bool = True,
        actor: str = "hermes",
    ) -> str:
        return self.store.memory_tree_pack(
            query,
            scope=scope,
            limit=limit,
            depth=depth,
            include_raw=include_raw,
            actor=actor,
        )

    def context_builder_pack(
        self,
        query: str,
        scope: str | None = None,
        thread_id: str = "default",
        limit: int = 8,
        actor: str = "hermes",
    ) -> str:
        return self.store.context_builder_pack(
            query,
            scope=scope,
            thread_id=thread_id,
            limit=limit,
            actor=actor,
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

    def observability_report(
        self,
        *,
        scope: str | None = None,
        thread_id: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        return self.store.memory_observability_report(
            scope=scope,
            thread_id=thread_id,
            limit=limit,
        )

    def current_best_report(
        self,
        query: str = "",
        *,
        scope: str | None = None,
        limit: int = 8,
    ) -> dict[str, Any]:
        return self.store.current_best_report(query, scope=scope, limit=limit)

    def memory_changes(
        self,
        *,
        keeper_job_id: str = "",
        thread_id: str | None = None,
        scope: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        return self.store.memory_changes(
            keeper_job_id=keeper_job_id,
            thread_id=thread_id,
            scope=scope,
            limit=limit,
        )

    def review_inbox(
        self,
        *,
        status: str = "open",
        scope: str | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        return self.store.review_inbox(status=status, scope=scope, limit=limit)

    def notifications(
        self,
        *,
        status: str = "open",
        scope: str | None = None,
        topic: str | None = None,
        severity: str | None = None,
        assigned_to: str | None = None,
        target_type: str | None = None,
        target_id: str | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        return self.store.list_notifications(
            status=status,
            scope=scope,
            topic=topic,
            severity=severity,
            assigned_to=assigned_to,
            target_type=target_type,
            target_id=target_id,
            limit=limit,
        )

    def assign_notification(
        self,
        notification_id: str,
        *,
        assigned_to: str,
        actor: str = "hermes",
        due_at: str = "",
        reason: str = "",
    ) -> dict[str, Any]:
        return self.store.assign_notification(
            notification_id,
            assigned_to=assigned_to,
            actor=actor,
            due_at=due_at,
            reason=reason,
        )

    def ack_notification(
        self,
        notification_id: str,
        *,
        actor: str = "hermes",
        reason: str = "",
    ) -> dict[str, Any]:
        return self.store.ack_notification(notification_id, actor=actor, reason=reason)

    def resolve_notification(
        self,
        notification_id: str,
        *,
        actor: str = "hermes",
        reason: str = "",
    ) -> dict[str, Any]:
        return self.store.resolve_notification(notification_id, actor=actor, reason=reason)

    def review_batch(
        self,
        *,
        action: str,
        candidate_ids: list[str],
        actor: str = "hermes",
        reason: str = "",
        dry_run: bool = False,
        stop_on_error: bool = False,
    ) -> dict[str, Any]:
        return self.store.review_batch(
            action=action,
            candidate_ids=candidate_ids,
            actor=actor,
            reason=reason,
            dry_run=dry_run,
            stop_on_error=stop_on_error,
        )

    def operational_status(
        self,
        *,
        max_db_bytes: int = 512 * 1024 * 1024,
        integrity_check: bool = True,
    ) -> dict[str, Any]:
        return self.store.operational_status(
            max_db_bytes=max_db_bytes,
            integrity_check=integrity_check,
        )

    def migration_status(self, *, integrity_check: bool = True) -> dict[str, Any]:
        return self.store.migration_status(integrity_check=integrity_check)

    def backup_database(
        self,
        out_path: str | Path,
        *,
        actor: str = "hermes",
        overwrite: bool = False,
    ) -> dict[str, Any]:
        return self.store.backup_database(
            out_path,
            actor=actor,
            overwrite=overwrite,
        )

    @staticmethod
    def restore_database(
        backup_path: str | Path,
        target_path: str | Path,
        *,
        actor: str = "hermes",
        overwrite: bool = False,
    ) -> dict[str, Any]:
        return MemoryStore.restore_database(
            backup_path,
            target_path,
            actor=actor,
            overwrite=overwrite,
        )

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
        return self.orchestrator.before_turn(
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

    def before_agent_turn(
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
        return self.orchestrator.before_turn(
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
        return self.orchestrator.after_turn(
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

    def after_agent_turn(
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
        return self.orchestrator.after_turn(
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

    def retrieve_context(
        self,
        query: str,
        *,
        scope: str | None = None,
        limit: int = 8,
        depth: int = 1,
        include_raw: bool = True,
        actor: str = "hermes",
    ) -> dict[str, Any]:
        return self.orchestrator.retrieve_context(
            query,
            scope=scope,
            limit=limit,
            depth=depth,
            include_raw=include_raw,
            actor=actor,
        )

    def build_prompt_context(
        self,
        query: str,
        *,
        thread_id: str = "default",
        scope: str = "professional",
        user_id: str = "user_default",
        agent_id: str = "agent",
        model_id: str = "",
        token_budget: int = 12000,
        limit: int = 8,
    ) -> dict[str, Any]:
        return self.orchestrator.build_prompt_context(
            query,
            thread_id=thread_id,
            scope=scope,
            user_id=user_id,
            agent_id=agent_id,
            model_id=model_id,
            token_budget=token_budget,
            limit=limit,
        )

    def keeper_analyze_turn(self, **kwargs: Any) -> dict[str, Any]:
        return self.orchestrator.keeper_analyze_turn(**kwargs)

    def ingest_graph(self, updates: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
        return self.orchestrator.ingest_graph(updates, **kwargs)

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

    def approve_candidate(
        self,
        candidate_id: str,
        *,
        actor: str = "hermes",
        reason: str = "",
    ) -> dict[str, Any]:
        return {
            "memory_id": self.store.approve_candidate(candidate_id, actor=actor, reason=reason),
            "status": "active",
        }

    def reject_candidate(
        self,
        candidate_id: str,
        *,
        actor: str = "hermes",
        reason: str = "",
    ) -> dict[str, Any]:
        self.store.reject_candidate(candidate_id, actor=actor, reason=reason)
        return {"candidate_id": candidate_id, "status": "rejected"}

    def correct_memory(
        self,
        memory_id: str,
        text: str,
        *,
        actor: str = "hermes",
        reason: str = "",
    ) -> dict[str, Any]:
        self.store.correct_memory(memory_id, text, actor=actor, reason=reason)
        return {"memory_id": memory_id, "status": "corrected"}

    def delete_memory(
        self,
        memory_id: str,
        *,
        actor: str = "hermes",
        reason: str = "",
    ) -> dict[str, Any]:
        self.store.delete_memory(memory_id, actor=actor, reason=reason)
        return {"memory_id": memory_id, "status": "deleted"}

    def distrust_memory(
        self,
        memory_id: str,
        *,
        actor: str = "hermes",
        reason: str = "",
    ) -> dict[str, Any]:
        self.store.distrust_memory(memory_id, actor=actor, reason=reason)
        return {"memory_id": memory_id, "status": "distrusted"}

    def expire_memory(
        self,
        memory_id: str,
        *,
        actor: str = "hermes",
        reason: str = "",
    ) -> dict[str, Any]:
        self.store.expire_memory(memory_id, actor=actor, reason=reason)
        return {"memory_id": memory_id, "status": "expired"}

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

    def export_profile(
        self,
        scope: str | None = None,
        project: str = "",
        actor: str = "hermes",
        redaction_profile: str = "full",
        approval_id: str = "",
        retention_days: int | None = None,
        artifact_ref: str = "",
    ) -> dict[str, Any]:
        return self.store.export_profile(
            scope=scope,
            project=project,
            actor=actor,
            redaction_profile=redaction_profile,
            approval_id=approval_id,
            retention_days=retention_days,
            artifact_ref=artifact_ref,
        )

    def export_encrypted_profile(
        self,
        *,
        passphrase: str,
        scope: str | None = None,
        project: str = "",
        actor: str = "hermes",
        redaction_profile: str = "full",
        approval_id: str = "",
        retention_days: int | None = None,
        artifact_ref: str = "",
    ) -> dict[str, Any]:
        return self.store.export_encrypted_profile(
            passphrase=passphrase,
            scope=scope,
            project=project,
            actor=actor,
            redaction_profile=redaction_profile,
            approval_id=approval_id,
            retention_days=retention_days,
            artifact_ref=artifact_ref,
        )

    def decrypt_encrypted_export(
        self,
        envelope: dict[str, Any],
        *,
        passphrase: str,
    ) -> dict[str, Any]:
        return self.store.decrypt_encrypted_export(envelope, passphrase=passphrase)

    def import_encrypted_profile(
        self,
        envelope: dict[str, Any],
        *,
        passphrase: str,
    ) -> dict[str, int]:
        return self.store.import_encrypted_profile(envelope, passphrase=passphrase)

    def export_control_report(
        self,
        actor: str = "hermes",
        scope: str | None = None,
        project: str = "",
        redaction_profile: str = "full",
        approval_id: str = "",
        retention_days: int | None = None,
    ) -> dict[str, Any]:
        return self.store.export_control_report(
            actor=actor,
            scope=scope,
            project=project,
            redaction_profile=redaction_profile,
            approval_id=approval_id,
            retention_days=retention_days,
        )

    def request_export_approval(
        self,
        *,
        actor: str = "hermes",
        requested_by: str = "reviewer",
        scope: str | None = None,
        project: str = "",
        export_kind: str = "profile",
        redaction_profile: str = "full",
        reason: str = "",
    ) -> dict[str, Any]:
        return self.store.request_export_approval(
            actor=actor,
            requested_by=requested_by,
            scope=scope,
            project=project,
            export_kind=export_kind,
            redaction_profile=redaction_profile,
            reason=reason,
        )

    def export_approvals(
        self,
        *,
        status: str | None = "pending",
        actor: str | None = None,
        scope: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        return self.store.list_export_approvals(
            status=status,
            actor=actor,
            scope=scope,
            limit=limit,
        )

    def approve_export_approval(
        self,
        approval_id: str,
        *,
        actor: str = "reviewer",
        reason: str = "",
    ) -> dict[str, Any]:
        return self.store.approve_export_approval(
            approval_id,
            actor=actor,
            reason=reason,
        )

    def reject_export_approval(
        self,
        approval_id: str,
        *,
        actor: str = "reviewer",
        reason: str = "",
    ) -> dict[str, Any]:
        return self.store.reject_export_approval(
            approval_id,
            actor=actor,
            reason=reason,
        )

    def export_retention_records(
        self,
        *,
        status: str | None = "active",
        actor: str | None = None,
        scope: str | None = None,
        expired_only: bool = False,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        return self.store.list_export_records(
            status=status,
            actor=actor,
            scope=scope,
            expired_only=expired_only,
            limit=limit,
        )

    def enforce_export_retention(self, *, actor: str = "system") -> dict[str, Any]:
        return self.store.enforce_export_retention(actor=actor)

    def purge_export_record(
        self,
        export_id: str,
        *,
        actor: str = "reviewer",
        reason: str = "",
    ) -> dict[str, Any]:
        return self.store.purge_export_record(
            export_id,
            actor=actor,
            reason=reason,
        )

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

    def set_read_policy(
        self,
        *,
        agent_id: str = "*",
        scope: str = "*",
        action: str = "inject",
        decision: str = "allow",
        reason: str = "",
        metadata: dict[str, Any] | None = None,
        actor: str = "hermes-admin",
    ) -> dict[str, Any]:
        return self.store.set_read_policy(
            agent_id=agent_id,
            scope=scope,
            action=action,
            decision=decision,
            reason=reason,
            metadata=metadata,
            actor=actor,
        )

    def read_policies(
        self,
        *,
        agent_id: str | None = None,
        scope: str | None = None,
        action: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        return self.store.list_read_policies(
            agent_id=agent_id,
            scope=scope,
            action=action,
            limit=limit,
        )

    def resolve_read_policy(self, actor: str, scope: str, action: str = "inject") -> dict[str, Any]:
        return self.store.resolve_read_policy(actor, scope, action)

    def capability_report(
        self,
        *,
        actor: str = "hermes",
        scope: str = "professional",
        project: str = "",
        read_actions: list[str] | None = None,
        write_actions: list[str] | None = None,
    ) -> dict[str, Any]:
        return self.store.capability_report(
            actor=actor,
            scope=scope,
            project=project,
            read_actions=read_actions,
            write_actions=write_actions,
        )

    def derived_invalidations(
        self,
        *,
        memory_id: str = "",
        scope: str | None = None,
        action: str = "",
        limit: int = 50,
    ) -> dict[str, Any]:
        return self.store.derived_invalidations(
            memory_id=memory_id,
            scope=scope,
            action=action,
            limit=limit,
        )

    def review_pending(self) -> list[dict[str, Any]]:
        return self.store.list_candidates("pending")

    def close(self) -> None:
        self.store.close()
