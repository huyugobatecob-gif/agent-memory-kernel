"""Command line interface."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from .acceptance import assert_acceptance_suite, run_acceptance_suite, seed_acceptance_fixture
from .conformance import (
    assert_conformance_spec_shape,
    assert_conformance_suite,
    conformance_certification_report,
    conformance_registry_entry,
    conformance_spec,
    run_conformance_suite,
    seed_conformance_fixture,
)
from .contract import assert_contract_shape, memory_contract
from .evals import keeper_eval_spec, run_keeper_eval
from .mcp_server import run_mcp_stdio
from .server import run_server
from .slice import assert_vertical_slice, run_vertical_slice, seed_vertical_slice
from .store import MemoryStore
from .worker import run_keeper_worker_daemon


DEFAULT_DB = ".memory/memory.db"


def add_common_db(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--db", default=DEFAULT_DB, help=f"SQLite database path (default: {DEFAULT_DB})")


def print_json(data: object) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True))


def parse_csv(value: str) -> list[str] | None:
    items = [item.strip() for item in (value or "").split(",") if item.strip()]
    return items or None


def read_passphrase(args: argparse.Namespace) -> str:
    if getattr(args, "passphrase_file", ""):
        return Path(args.passphrase_file).read_text(encoding="utf-8").strip()
    env_name = getattr(args, "passphrase_env", "") or "AGENT_MEMORY_EXPORT_PASSPHRASE"
    value = os.environ.get(env_name, "")
    if not value:
        raise ValueError(f"passphrase not found in environment variable: {env_name}")
    return value


def cmd_init(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    store.close()
    print(f"initialized {args.db}")
    return 0


def cmd_remember(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    result = store.remember(
        args.text,
        scope=args.scope,
        actor=args.actor,
        source_type=args.source_type,
        source_ref=args.source_ref,
        sensitivity=args.sensitivity,
        auto_approve=args.approve,
    )
    store.close()
    print_json(result)
    return 0


def cmd_write_policy_set(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    result = store.set_write_policy(
        agent_id=args.agent_id,
        scope=args.scope,
        action=args.action,
        decision=args.decision,
        reason=args.reason,
        metadata=json.loads(args.metadata_json),
        actor=args.actor,
    )
    store.close()
    print_json(result)
    return 0


def cmd_write_policy_list(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.list_write_policies(
            agent_id=args.agent_id,
            scope=args.scope,
            action=args.action,
            limit=args.limit,
        )
    )
    store.close()
    return 0


def cmd_read_policy_set(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    result = store.set_read_policy(
        agent_id=args.agent_id,
        scope=args.scope,
        action=args.action,
        decision=args.decision,
        reason=args.reason,
        metadata=json.loads(args.metadata_json),
        actor=args.actor,
    )
    store.close()
    print_json(result)
    return 0


def cmd_read_policy_list(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.list_read_policies(
            agent_id=args.agent_id,
            scope=args.scope,
            action=args.action,
            limit=args.limit,
        )
    )
    store.close()
    return 0


def cmd_capability(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.capability_report(
            actor=args.actor,
            scope=args.scope,
            project=args.project,
            read_actions=parse_csv(args.read_actions),
            write_actions=parse_csv(args.write_actions),
        )
    )
    store.close()
    return 0


def cmd_identity_delegation(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.identity_delegation_report(
            actor=args.actor,
            scope=args.scope,
            project=args.project,
            tenant_id=args.tenant_id,
        )
    )
    store.close()
    return 0


def cmd_review_list(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(store.list_candidates(args.status))
    store.close()
    return 0


def cmd_review_inbox(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(store.review_inbox(status=args.status, scope=args.scope, limit=args.limit))
    store.close()
    return 0


def cmd_review_batch(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.review_batch(
            action=args.action,
            candidate_ids=args.candidate_ids,
            actor=args.actor,
            reason=args.reason,
            dry_run=args.dry_run,
            stop_on_error=args.stop_on_error,
        )
    )
    store.close()
    return 0


def cmd_review_approve(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    memory_id = store.approve_candidate(args.candidate_id, actor=args.actor, reason=args.reason)
    store.close()
    print_json({"memory_id": memory_id, "status": "active"})
    return 0


def cmd_review_reject(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    store.reject_candidate(args.candidate_id, actor=args.actor, reason=args.reason)
    store.close()
    print_json({"candidate_id": args.candidate_id, "status": "rejected"})
    return 0


def cmd_notifications_list(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.list_notifications(
            status=args.status,
            scope=args.scope,
            topic=args.topic,
            severity=args.severity,
            assigned_to=args.assigned_to,
            sla_status=args.sla_status,
            target_type=args.target_type,
            target_id=args.target_id,
            limit=args.limit,
        )
    )
    store.close()
    return 0


def cmd_notifications_escalations(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.notification_escalations(
            scope=args.scope,
            assigned_to=args.assigned_to,
            include_acknowledged=not args.open_only,
            limit=args.limit,
        )
    )
    store.close()
    return 0


def cmd_notifications_transport(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.notification_transport_payloads(
            transport=args.transport,
            status=args.status,
            scope=args.scope,
            topic=args.topic,
            severity=args.severity,
            assigned_to=args.assigned_to,
            sla_status=args.sla_status,
            limit=args.limit,
        )
    )
    store.close()
    return 0


def cmd_notifications_delivery_enqueue(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.enqueue_notification_deliveries(
            transport=args.transport,
            destination=args.destination,
            status=args.status,
            scope=args.scope,
            topic=args.topic,
            severity=args.severity,
            assigned_to=args.assigned_to,
            sla_status=args.sla_status,
            actor=args.actor,
            limit=args.limit,
            dedupe=not args.no_dedupe,
        )
    )
    store.close()
    return 0


def cmd_notifications_delivery_list(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.list_notification_deliveries(
            status=args.status,
            transport=args.transport,
            notification_id=args.notification_id,
            destination=args.destination,
            limit=args.limit,
        )
    )
    store.close()
    return 0


def cmd_notifications_delivery_mark(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.mark_notification_delivery(
            args.delivery_id,
            status=args.status,
            actor=args.actor,
            error=args.error,
        )
    )
    store.close()
    return 0


def cmd_notifications_assign(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.assign_notification(
            args.notification_id,
            assigned_to=args.assigned_to,
            actor=args.actor,
            due_at=args.due_at,
            reason=args.reason,
        )
    )
    store.close()
    return 0


def cmd_notifications_ack(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.ack_notification(
            args.notification_id,
            actor=args.actor,
            reason=args.reason,
        )
    )
    store.close()
    return 0


def cmd_notifications_resolve(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.resolve_notification(
            args.notification_id,
            actor=args.actor,
            reason=args.reason,
        )
    )
    store.close()
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(store.search(args.query, scope=args.scope, limit=args.limit, actor=args.actor))
    store.close()
    return 0


def cmd_context_pack(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print(store.context_pack(args.query, scope=args.scope, limit=args.limit, actor=args.actor))
    store.close()
    return 0


def cmd_build_context(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print(
        store.context_builder_pack(
            args.query,
            scope=args.scope,
            thread_id=args.thread_id,
            limit=args.limit,
            recent_messages=args.recent_messages,
            actor=args.actor,
        )
    )
    store.close()
    return 0


def cmd_before_model_call(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.before_model_call(
            args.query,
            thread_id=args.thread_id,
            scope=args.scope,
            user_id=args.user_id,
            agent_id=args.agent_id,
            model_id=args.model_id,
            mode=args.mode,
            token_budget=args.token_budget,
            requested_lanes=parse_csv(args.requested_lanes),
            allowed_scopes=parse_csv(args.allowed_scopes),
            denied_scopes=parse_csv(args.denied_scopes),
            limit=args.limit,
            recent_messages=args.recent_messages,
            enable_brain_style=not args.disable_brain_style,
            prompt_format=args.prompt_format,
        )
    )
    store.close()
    return 0


def cmd_read_time_policy(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.read_time_policy(
            scope=args.scope,
            token_budget=args.token_budget,
            model_id=args.model_id,
            limit=args.limit,
        )
    )
    store.close()
    return 0


def cmd_prompt_budget(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.prompt_budget_profile(
            model_id=args.model_id,
            requested_token_budget=args.token_budget,
        )
    )
    store.close()
    return 0


def cmd_prompt_format_certify(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.prompt_formatter_certification(
            providers=parse_csv(args.providers),
            model_id=args.model_id,
        )
    )
    store.close()
    return 0


def cmd_embedding_certify(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.embedding_certification_report(
            provider_name=args.provider,
            dims=args.dims,
        )
    )
    store.close()
    return 0


def cmd_router_runs(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.list_router_runs(
            thread_id=args.thread_id,
            scope=args.scope,
            limit=args.limit,
        )
    )
    store.close()
    return 0


def cmd_router_explain(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(store.explain_router_run(args.router_run_id))
    store.close()
    return 0


def cmd_memory_explain(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(store.explain_memory(args.memory_id))
    store.close()
    return 0


def cmd_router_feedback_record(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.record_router_feedback(
            args.router_run_id,
            memory_id=args.memory_id,
            branch_id=args.branch_id,
            rating=args.rating,
            score=args.score,
            actor=args.actor,
            reason=args.reason,
            metadata=json.loads(args.metadata_json),
        )
    )
    store.close()
    return 0


def cmd_router_feedback_list(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.list_router_feedback(
            router_run_id=args.router_run_id,
            memory_id=args.memory_id,
            rating=args.rating,
            limit=args.limit,
        )
    )
    store.close()
    return 0


def cmd_memory_quality(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(store.memory_quality_report(scope=args.scope, limit=args.limit))
    store.close()
    return 0


def cmd_observability(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.memory_observability_report(
            scope=args.scope,
            thread_id=args.thread_id,
            limit=args.limit,
            router_latency_slo_ms=args.router_latency_slo_ms,
            keeper_latency_slo_ms=args.keeper_latency_slo_ms,
        )
    )
    store.close()
    return 0


def cmd_dashboard(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.operations_dashboard(
            scope=args.scope,
            thread_id=args.thread_id,
            limit=args.limit,
            stale_after_seconds=args.stale_after_seconds,
            include_details=not args.summary_only,
        )
    )
    store.close()
    return 0


def cmd_billing_reconcile(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.billing_reconciliation_report(
            scope=args.scope,
            thread_id=args.thread_id,
            provider=args.provider,
            currency=args.currency,
            since=args.since,
            until=args.until,
            expected_cost=args.expected_cost,
            expected_currency=args.expected_currency,
            tolerance=args.tolerance,
            max_cost_per_1k=args.max_cost_per_1k,
            limit=args.limit,
        )
    )
    store.close()
    return 0


def cmd_billing_invoice_import(args: argparse.Namespace) -> int:
    payload = json.loads(Path(args.file).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("billing invoice file must contain a JSON object")
    line_items = payload.get("line_items", [])
    if not isinstance(line_items, list):
        raise ValueError("billing invoice line_items must be a list")
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.import_billing_invoice(
            invoice_id=str(payload.get("invoice_id") or args.invoice_id),
            provider=str(payload.get("provider") or args.provider),
            line_items=line_items,
            period_start=str(payload.get("period_start") or args.period_start),
            period_end=str(payload.get("period_end") or args.period_end),
            currency=str(payload.get("currency") or args.currency),
            actor=args.actor,
            source_ref=str(payload.get("source_ref") or args.source_ref),
            metadata=payload.get("metadata") if isinstance(payload.get("metadata"), dict) else None,
            overwrite=args.overwrite,
        )
    )
    store.close()
    return 0


def cmd_billing_invoice_list(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.list_billing_invoice_items(
            invoice_id=args.invoice_id,
            provider=args.provider,
            scope=args.scope,
            thread_id=args.thread_id,
            currency=args.currency,
            since=args.since,
            until=args.until,
            status=args.status,
            limit=args.limit,
        )
    )
    store.close()
    return 0


def cmd_migration_status(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(store.migration_status(integrity_check=not args.skip_integrity_check))
    store.close()
    return 0


def cmd_kernel_status(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(store.kernel_status(integrity_check=not args.skip_integrity_check))
    store.close()
    return 0


def cmd_audit_integrity(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(store.audit_integrity_report(limit=args.limit))
    store.close()
    return 0


def cmd_migration_changelog(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(store.migration_changelog(limit=args.limit))
    store.close()
    return 0


def cmd_backup(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.backup_database(
            args.out,
            actor=args.actor,
            overwrite=args.overwrite,
        )
    )
    store.close()
    return 0


def cmd_restore(args: argparse.Namespace) -> int:
    print_json(
        MemoryStore.restore_database(
            args.backup,
            args.target_db,
            overwrite=args.overwrite,
            actor=args.actor,
        )
    )
    return 0


def cmd_restore_drill(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.restore_drill(
            backup_path=args.backup_path,
            target_path=args.target_db,
            scope=args.scope,
            probe_query=args.probe_query,
            actor=args.actor,
            overwrite=args.overwrite,
        )
    )
    store.close()
    return 0


def cmd_restore_drill_schedule_set(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.set_restore_drill_schedule(
            name=args.name,
            interval_hours=args.interval_hours,
            scope=args.scope,
            probe_query=args.probe_query,
            start_at=args.start_at,
            artifact_dir=args.artifact_dir,
            retain_artifacts=args.retain_artifacts,
            status=args.status,
            actor=args.actor,
        )
    )
    store.close()
    return 0


def cmd_restore_drill_schedule_list(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.list_restore_drill_schedules(
            status=args.status,
            due_only=args.due_only,
            limit=args.limit,
        )
    )
    store.close()
    return 0


def cmd_restore_drill_schedule_run_due(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.run_due_restore_drill_schedules(
            limit=args.limit,
            actor=args.actor,
            include_not_due=args.include_not_due,
        )
    )
    store.close()
    return 0


def cmd_current_best(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.current_best_report(
            args.query or "",
            scope=args.scope,
            limit=args.limit,
        )
    )
    store.close()
    return 0


def cmd_memory_changes(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.memory_changes(
            keeper_job_id=args.keeper_job_id,
            thread_id=args.thread_id,
            scope=args.scope,
            limit=args.limit,
        )
    )
    store.close()
    return 0


def cmd_derived_invalidations(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.derived_invalidations(
            memory_id=args.memory_id,
            scope=args.scope,
            action=args.action,
            limit=args.limit,
        )
    )
    store.close()
    return 0


def cmd_derived_lineage(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.derived_lineage_report(
            memory_id=args.memory_id,
            scope=args.scope,
            action=args.action,
            limit=args.limit,
        )
    )
    store.close()
    return 0


def cmd_after_saved_turn(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    metadata = json.loads(args.metadata_json)
    print_json(
        store.after_saved_turn(
            thread_id=args.thread_id,
            scope=args.scope,
            user_id=args.user_id,
            agent_id=args.agent_id,
            model_id=args.model_id,
            user_text=args.user_text,
            assistant_text=args.assistant_text,
            turn_id=args.turn_id,
            auto_approve=args.approve,
            keeper_mode=args.keeper_mode,
            metadata=metadata,
        )
    )
    store.close()
    return 0


def cmd_shadow_turn(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    metadata = json.loads(args.metadata_json)
    print_json(
        store.shadow_turn(
            args.query,
            thread_id=args.thread_id,
            scope=args.scope,
            user_id=args.user_id,
            agent_id=args.agent_id,
            model_id=args.model_id,
            mode=args.mode,
            token_budget=args.token_budget,
            requested_lanes=parse_csv(args.requested_lanes),
            allowed_scopes=parse_csv(args.allowed_scopes),
            denied_scopes=parse_csv(args.denied_scopes),
            limit=args.limit,
            recent_messages=args.recent_messages,
            user_text=args.user_text,
            assistant_text=args.assistant_text,
            keeper_mode=args.keeper_mode,
            enable_brain_style=not args.disable_brain_style,
            metadata=metadata,
        )
    )
    store.close()
    return 0


def cmd_shadow_traces(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.list_shadow_traces(
            thread_id=args.thread_id,
            scope=args.scope,
            limit=args.limit,
        )
    )
    store.close()
    return 0


def cmd_shadow_eval(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.evaluate_shadow_trace(
            args.shadow_trace_id,
            expected=json.loads(args.expected_json),
            actor=args.actor,
            metadata=json.loads(args.metadata_json),
        )
    )
    store.close()
    return 0


def cmd_shadow_evals(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.list_shadow_evals(
            shadow_trace_id=args.shadow_trace_id,
            status=args.status,
            limit=args.limit,
        )
    )
    store.close()
    return 0


def cmd_outcome_record(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    result = store.record_outcome(
        project=args.project,
        loop_id=args.loop_id,
        outcome_status=args.status,
        score=args.score,
        hypothesis=args.hypothesis,
        action=args.action,
        result=args.result,
        cause=args.cause,
        lesson=args.lesson,
        next_recommendation=args.next_recommendation,
        scope=args.scope,
        actor=args.actor,
        auto_approve=args.approve,
        metadata=json.loads(args.metadata_json),
    )
    store.close()
    print_json(result)
    return 0


def cmd_outcome_list(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.list_outcomes(
            project=args.project,
            outcome_status=args.status,
            scope=args.scope,
            status=args.record_status,
            limit=args.limit,
        )
    )
    store.close()
    return 0


def cmd_outcome_pack(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print(store.outcome_pack(project=args.project, scope=args.scope, limit=args.limit))
    store.close()
    return 0


def cmd_outcome_compare(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.outcome_compare(
            project=args.project,
            scope=args.scope,
            limit=args.limit,
        )
    )
    store.close()
    return 0


def cmd_tree_pack(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print(
        store.memory_tree_pack(
            args.query,
            scope=args.scope,
            limit=args.limit,
            depth=args.depth,
            include_raw=not args.no_raw,
            raw_chars=args.raw_chars,
            actor=args.actor,
        )
    )
    store.close()
    return 0


def cmd_turn(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    result = store.record_turn(
        args.content,
        thread_id=args.thread_id,
        role=args.role,
        actor=args.actor,
        scope=args.scope,
        remember=args.remember,
        auto_approve=args.approve,
    )
    store.close()
    print_json(result)
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    summary_id = store.add_thread_summary(
        args.summary,
        thread_id=args.thread_id,
        scope=args.scope,
        summary_type=args.summary_type,
        source_memory_ids=args.source_memory_id or None,
    )
    store.close()
    print_json({"summary_id": summary_id, "status": "recorded"})
    return 0


def cmd_graph_items(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.list_memory_items(
            scope=args.scope,
            item_type=args.type,
            limit=args.limit,
        )
    )
    store.close()
    return 0


def cmd_graph_nodes(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.list_graph_nodes(
            scope=args.scope,
            node_type=args.type,
            limit=args.limit,
        )
    )
    store.close()
    return 0


def cmd_graph_edges(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(store.list_graph_edges(scope=args.scope, limit=args.limit))
    store.close()
    return 0


def cmd_graph_browser(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.graph_browser(
            scope=args.scope,
            node_type=args.type,
            query=args.query,
            limit=args.limit,
            evidence_limit=args.evidence_limit,
        )
    )
    store.close()
    return 0


def cmd_graph_keeper(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(store.list_keeper_runs(limit=args.limit))
    store.close()
    return 0


def cmd_graph_groups(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(store.list_graph_groups(scope=args.scope))
    store.close()
    return 0


def cmd_graph_analyses(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(store.list_semantic_analyses(scope=args.scope, limit=args.limit))
    store.close()
    return 0


def cmd_graph_optimize(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(store.optimize_graph(args.mode, scope=args.scope))
    store.close()
    return 0


def cmd_graph_optimization_runs(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(store.list_graph_optimization_runs(scope=args.scope, limit=args.limit))
    store.close()
    return 0


def cmd_graph_brain(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(store.digital_brain_state(scope=args.scope))
    store.close()
    return 0


def cmd_graph_brain_style(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(store.brain_style_append(scope=args.scope))
    store.close()
    return 0


def cmd_brain_style_certify(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(store.brain_style_certification_report(scope=args.scope))
    store.close()
    return 0


def cmd_graph_tree(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print(
        store.memory_tree_pack(
            args.query,
            scope=args.scope,
            limit=args.limit,
            depth=args.depth,
            include_raw=not args.no_raw,
            raw_chars=args.raw_chars,
        )
    )
    store.close()
    return 0


def cmd_profile_set_intro(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    note_id = store.upsert_profile_note(
        args.content,
        scope=args.scope,
        note_type="intro",
        title=args.title,
    )
    store.close()
    print_json({"profile_note_id": note_id, "status": "active"})
    return 0


def cmd_profile_add_rule(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    note_id = store.upsert_profile_note(
        args.content,
        scope=args.scope,
        note_type="rule",
        title=args.title,
    )
    store.close()
    print_json({"profile_note_id": note_id, "status": "active"})
    return 0


def cmd_profile_list(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(store.list_profile_notes(scope=args.scope, note_type=args.type))
    store.close()
    return 0


def cmd_profile_project(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    profile_id = store.upsert_project_profile(
        scope=args.scope,
        project=args.project,
        access=json.loads(args.access_json),
        env_snapshot=json.loads(args.env_json),
        saved_model_choices=json.loads(args.models_json),
        data_enrichment_snapshot=json.loads(args.data_json),
    )
    store.close()
    print_json({"profile_id": profile_id, "status": "active"})
    return 0


def cmd_usage_record(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    usage_id = store.record_llm_usage(
        provider=args.provider,
        model=args.model,
        scope=args.scope,
        thread_id=args.thread_id,
        prompt_tokens=args.prompt_tokens,
        completion_tokens=args.completion_tokens,
        cost=args.cost,
        currency=args.currency,
    )
    store.close()
    print_json({"usage_id": usage_id, "status": "recorded"})
    return 0


def cmd_usage_list(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.list_llm_usage(
            scope=args.scope,
            thread_id=args.thread_id,
            limit=args.limit,
        )
    )
    store.close()
    return 0


def cmd_export_profile(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.export_profile(
            scope=args.scope,
            project=args.project,
            actor=args.actor,
            redaction_profile=args.redaction_profile,
            approval_id=args.approval_id,
            retention_days=args.retention_days,
        )
    )
    store.close()
    return 0


def cmd_export_control(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.export_control_report(
            actor=args.actor,
            scope=args.scope,
            project=args.project,
            redaction_profile=args.redaction_profile,
            approval_id=args.approval_id,
            retention_days=args.retention_days,
        )
    )
    store.close()
    return 0


def cmd_export_custody(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.export_custody_report(
            actor=args.actor,
            scope=args.scope,
            project=args.project,
            redaction_profile=args.redaction_profile,
            approval_id=args.approval_id,
            retention_days=args.retention_days,
            artifact_ref=args.artifact_ref,
            passphrase_env=args.passphrase_env,
            offhost_required=not args.local_artifact_ok,
        )
    )
    store.close()
    return 0


def cmd_export_approval_request(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.request_export_approval(
            actor=args.actor,
            requested_by=args.requested_by,
            scope=args.scope,
            project=args.project,
            export_kind=args.export_kind,
            redaction_profile=args.redaction_profile,
            reason=args.reason,
            metadata=json.loads(args.metadata_json),
        )
    )
    store.close()
    return 0


def cmd_export_approval_list(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        {
            "approvals": store.list_export_approvals(
                status=args.status,
                actor=args.actor,
                scope=args.scope,
                limit=args.limit,
            )
        }
    )
    store.close()
    return 0


def cmd_export_approval_approve(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.approve_export_approval(
            args.approval_id,
            actor=args.actor,
            reason=args.reason,
        )
    )
    store.close()
    return 0


def cmd_export_approval_reject(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.reject_export_approval(
            args.approval_id,
            actor=args.actor,
            reason=args.reason,
        )
    )
    store.close()
    return 0


def cmd_export_retention_list(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        {
            "exports": store.list_export_records(
                status=args.status,
                actor=args.actor,
                scope=args.scope,
                expired_only=args.expired_only,
                limit=args.limit,
            )
        }
    )
    store.close()
    return 0


def cmd_export_retention_enforce(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(store.enforce_export_retention(actor=args.actor))
    store.close()
    return 0


def cmd_export_retention_purge(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.purge_export_record(
            args.export_id,
            actor=args.actor,
            reason=args.reason,
        )
    )
    store.close()
    return 0


def cmd_export_encrypted_profile(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    envelope = store.export_encrypted_profile(
        passphrase=read_passphrase(args),
        scope=args.scope,
        project=args.project,
        actor=args.actor,
        redaction_profile=args.redaction_profile,
        approval_id=args.approval_id,
        retention_days=args.retention_days,
        artifact_ref=args.out,
    )
    store.close()
    Path(args.out).write_text(
        json.dumps(envelope, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print_json(
        {
            "status": "encrypted_export_written",
            "out": args.out,
            "version": envelope["version"],
            "metadata": envelope["header"].get("metadata", {}),
        }
    )
    return 0


def cmd_import_encrypted_profile(args: argparse.Namespace) -> int:
    envelope = json.loads(Path(args.path).read_text(encoding="utf-8"))
    store = MemoryStore(args.db)
    store.init_db()
    print_json(store.import_encrypted_profile(envelope, passphrase=read_passphrase(args)))
    store.close()
    return 0


def cmd_import_profile(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    payload = json.loads(Path(args.path).read_text(encoding="utf-8"))
    print_json(store.import_profile(payload))
    store.close()
    return 0


def cmd_export_bundle(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    bundle = store.export_bundle(
        scope=args.scope,
        project=args.project,
        actor=args.actor,
        redaction_profile=args.redaction_profile,
        approval_id=args.approval_id,
        retention_days=args.retention_days,
        artifact_ref=args.out,
    )
    store.close()
    Path(args.out).write_text(
        json.dumps(bundle, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print_json(
        {
            "status": "bundle_written",
            "out": args.out,
            "version": bundle["version"],
            "manifest": bundle["manifest"],
        }
    )
    return 0


def cmd_verify_bundle(args: argparse.Namespace) -> int:
    bundle = json.loads(Path(args.path).read_text(encoding="utf-8"))
    store = MemoryStore(args.db)
    store.init_db()
    print_json(store.verify_bundle(bundle))
    store.close()
    return 0


def cmd_import_bundle(args: argparse.Namespace) -> int:
    bundle = json.loads(Path(args.path).read_text(encoding="utf-8"))
    store = MemoryStore(args.db)
    store.init_db()
    print_json(store.import_bundle(bundle))
    store.close()
    return 0


def cmd_vault_export(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.export_vault(
            args.out,
            actor=args.actor,
            scope=args.scope,
            redaction_profile=args.redaction_profile,
            approval_id=args.approval_id,
            retention_days=args.retention_days,
        )
    )
    store.close()
    return 0


def cmd_vault_import(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.import_vault(
            args.path,
            actor=args.actor,
            auto_approve=args.auto_approve,
        )
    )
    store.close()
    return 0


def cmd_correct(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    result = store.correct_memory(args.memory_id, args.text, actor=args.actor, reason=args.reason)
    store.close()
    print_json(result)
    return 0


def cmd_lifecycle_batch(args: argparse.Namespace) -> int:
    if bool(args.operations_json) == bool(args.operations_file):
        raise SystemExit("provide exactly one of --operations-json or --operations-file")
    raw = args.operations_json
    if args.operations_file:
        raw = Path(args.operations_file).read_text(encoding="utf-8")
    operations = json.loads(raw)
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.batch_memory_lifecycle(
            operations,
            actor=args.actor,
            reason=args.reason,
            dry_run=args.dry_run,
            stop_on_error=args.stop_on_error,
        )
    )
    store.close()
    return 0


def cmd_revisions(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(store.list_memory_revisions(args.memory_id, limit=args.limit))
    store.close()
    return 0


def cmd_rollback(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    result = store.rollback_memory(
        args.memory_id,
        revision_id=args.revision_id,
        actor=args.actor,
        reason=args.reason,
    )
    store.close()
    print_json(result)
    return 0


def cmd_supersede(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    result = store.supersede_memory(
        args.old_memory_id,
        args.new_memory_id,
        actor=args.actor,
        reason=args.reason,
    )
    store.close()
    print_json(result)
    return 0


def cmd_conflict_record(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    result = store.record_memory_conflict(
        args.memory_id,
        args.other_memory_id,
        relation=args.relation,
        winner_memory_id=args.winner_memory_id,
        actor=args.actor,
        reason=args.reason,
        metadata=json.loads(args.metadata_json),
    )
    store.close()
    print_json(result)
    return 0


def cmd_conflict_list(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.list_memory_conflicts(
            status=args.status,
            scope=args.scope,
            limit=args.limit,
        )
    )
    store.close()
    return 0


def cmd_conflict_detect(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(
        store.detect_memory_conflicts(
            scope=args.scope,
            kind=args.kind,
            limit=args.limit,
            min_overlap=args.min_overlap,
            min_jaccard=args.min_jaccard,
            record=args.record,
            actor=args.actor,
            reason=args.reason,
        )
    )
    store.close()
    return 0


def cmd_delete(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    store.delete_memory(args.memory_id, actor=args.actor, reason=args.reason)
    store.close()
    print_json({"memory_id": args.memory_id, "status": "deleted"})
    return 0


def cmd_distrust(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    store.distrust_memory(args.memory_id, actor=args.actor, reason=args.reason)
    store.close()
    print_json({"memory_id": args.memory_id, "status": "distrusted"})
    return 0


def cmd_expire(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    store.expire_memory(args.memory_id, actor=args.actor, reason=args.reason)
    store.close()
    print_json({"memory_id": args.memory_id, "status": "expired"})
    return 0


def cmd_slice_seed(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(seed_vertical_slice(store))
    store.close()
    return 0


def cmd_slice_run(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(run_vertical_slice(store))
    store.close()
    return 0


def cmd_slice_assert(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(assert_vertical_slice(store))
    store.close()
    return 0


def cmd_contract(args: argparse.Namespace) -> int:
    print_json(memory_contract())
    return 0


def cmd_contract_assert(args: argparse.Namespace) -> int:
    result = assert_contract_shape()
    print_json(result)
    return 0 if result["status"] == "pass" else 1


def cmd_acceptance_seed(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(seed_acceptance_fixture(store))
    store.close()
    return 0


def cmd_acceptance_run(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    result = run_acceptance_suite(store)
    store.close()
    print_json(result)
    return 0 if result["status"] == "pass" else 1


def cmd_acceptance_assert(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    result = assert_acceptance_suite(store)
    store.close()
    print_json(result)
    return 0


def cmd_conformance_spec(args: argparse.Namespace) -> int:
    print_json(conformance_spec())
    return 0


def cmd_conformance_spec_assert(args: argparse.Namespace) -> int:
    result = assert_conformance_spec_shape()
    print_json(result)
    return 0 if result["status"] == "pass" else 1


def cmd_conformance_seed(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(seed_conformance_fixture(store))
    store.close()
    return 0


def cmd_conformance_run(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    result = run_conformance_suite(store)
    store.close()
    print_json(result)
    return 0 if result["status"] == "pass" else 1


def cmd_conformance_assert(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    result = assert_conformance_suite(store)
    store.close()
    print_json(result)
    return 0


def cmd_conformance_certify(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    result = conformance_certification_report(
        store,
        adapter_name=args.adapter_name,
        adapter_version=args.adapter_version,
        seed_fixture=args.seed,
    )
    store.close()
    print_json(result)
    return 0 if result["status"] == "pass" else 1


def cmd_conformance_registry_entry(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    result = conformance_registry_entry(
        store,
        adapter_name=args.adapter_name,
        adapter_version=args.adapter_version,
        seed_fixture=args.seed,
        runtime=args.runtime,
        repository=args.repository,
        homepage=args.homepage,
        maintainer=args.maintainer,
        notes=args.notes,
    )
    store.close()
    print_json(result)
    return 0 if result["status"] == "pass" else 1


def cmd_keeper_eval(args: argparse.Namespace) -> int:
    if args.spec:
        print_json(keeper_eval_spec())
        return 0
    result = run_keeper_eval()
    print_json(result)
    return 0 if result.get("status") == "pass" else 1


def cmd_worker(args: argparse.Namespace) -> int:
    if args.daemon:
        def emit(report: dict[str, Any]) -> None:
            if not args.quiet:
                print(json.dumps(report, ensure_ascii=False, sort_keys=True), flush=True)

        result = run_keeper_worker_daemon(
            args.db,
            limit=args.limit,
            actor=args.actor,
            poll_interval=args.poll_interval,
            max_iterations=args.max_iterations if args.max_iterations > 0 else None,
            stop_when_idle=args.stop_when_idle,
            emit=emit,
        )
        print_json(result)
        return 0

    store = MemoryStore(args.db)
    store.init_db()
    result = store.process_keeper_jobs(limit=args.limit, actor=args.actor)
    store.close()
    print_json(result)
    return 0


def cmd_worker_status(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    result = store.worker_status_report(
        scope=args.scope,
        stale_after_seconds=args.stale_after_seconds,
        limit=args.limit,
    )
    store.close()
    print_json(result)
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    run_server(
        args.db,
        host=args.host,
        port=args.port,
        auth_token=args.auth_token,
        auth_token_env=args.auth_token_env,
    )
    return 0


def cmd_mcp(args: argparse.Namespace) -> int:
    run_mcp_stdio(args.db)
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    store.export_markdown(
        args.out,
        actor=args.actor,
        redaction_profile=args.redaction_profile,
        approval_id=args.approval_id,
        retention_days=args.retention_days,
    )
    store.close()
    print(f"exported markdown vault to {args.out}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-memory",
        description="Local-first auditable memory for AI agents.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init", help="Initialize a memory database")
    add_common_db(p)
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("remember", help="Record a memory event and candidate memory")
    add_common_db(p)
    p.add_argument("text")
    p.add_argument("--scope", default="professional", choices=["personal", "professional", "project", "agent", "session"])
    p.add_argument("--actor", default="user")
    p.add_argument("--source-type", default="manual")
    p.add_argument("--source-ref", default="")
    p.add_argument("--sensitivity", default="internal", choices=["public", "internal", "personal", "secret"])
    p.add_argument("--approve", action="store_true", help="Auto-approve safe trusted-source notes")
    p.set_defaults(func=cmd_remember)

    p = sub.add_parser("write-policy", help="Configure agent write authority")
    add_common_db(p)
    policy_sub = p.add_subparsers(dest="write_policy_command", required=True)

    wp = policy_sub.add_parser("set", help="Set an allow/deny write policy")
    wp.add_argument("--agent-id", default="*", help="Agent id or * wildcard")
    wp.add_argument("--scope", default="*", choices=["*", "personal", "professional", "project", "agent", "session"])
    wp.add_argument("--action", default="*", help="Action name or * wildcard")
    wp.add_argument("--decision", default="allow", choices=["allow", "deny"])
    wp.add_argument("--reason", default="")
    wp.add_argument("--metadata-json", default="{}")
    wp.add_argument("--actor", default="user")
    wp.set_defaults(func=cmd_write_policy_set)

    wp = policy_sub.add_parser("list", help="List configured write policies")
    wp.add_argument("--agent-id")
    wp.add_argument("--scope", choices=["*", "personal", "professional", "project", "agent", "session"])
    wp.add_argument("--action")
    wp.add_argument("--limit", type=int, default=100)
    wp.set_defaults(func=cmd_write_policy_list)

    p = sub.add_parser("read-policy", help="Configure agent read/injection authority")
    add_common_db(p)
    read_policy_sub = p.add_subparsers(dest="read_policy_command", required=True)

    rp = read_policy_sub.add_parser("set", help="Set an allow/deny read policy")
    rp.add_argument("--agent-id", default="*", help="Agent id or * wildcard")
    rp.add_argument("--scope", default="*", choices=["*", "personal", "professional", "project", "agent", "session"])
    rp.add_argument("--action", default="inject", help="Action name such as read, inject, export, or * wildcard")
    rp.add_argument("--decision", default="allow", choices=["allow", "deny"])
    rp.add_argument("--reason", default="")
    rp.add_argument("--metadata-json", default="{}")
    rp.add_argument("--actor", default="user")
    rp.set_defaults(func=cmd_read_policy_set)

    rp = read_policy_sub.add_parser("list", help="List configured read policies")
    rp.add_argument("--agent-id")
    rp.add_argument("--scope", choices=["*", "personal", "professional", "project", "agent", "session"])
    rp.add_argument("--action")
    rp.add_argument("--limit", type=int, default=100)
    rp.set_defaults(func=cmd_read_policy_list)

    p = sub.add_parser("capability", help="Report effective read/write memory capabilities for an agent")
    add_common_db(p)
    p.add_argument("--actor", default="agent")
    p.add_argument("--scope", default="professional", choices=["personal", "professional", "project", "agent", "session"])
    p.add_argument("--project", default="")
    p.add_argument("--read-actions", default="", help="Comma-separated read actions; default: read,inject,export")
    p.add_argument("--write-actions", default="", help="Comma-separated write actions; default: all write actions")
    p.set_defaults(func=cmd_capability)

    p = sub.add_parser("identity-delegation", help="Report hosted identity and explicit delegation posture")
    add_common_db(p)
    p.add_argument("--actor", default="agent")
    p.add_argument("--scope", default="professional", choices=["*", "personal", "professional", "project", "agent", "session"])
    p.add_argument("--project", default="")
    p.add_argument("--tenant-id", default="local")
    p.set_defaults(func=cmd_identity_delegation)

    p = sub.add_parser("review", help="Review candidate memories")
    add_common_db(p)
    review_sub = p.add_subparsers(dest="review_command", required=True)

    rp = review_sub.add_parser("list", help="List candidate memories")
    rp.add_argument("--status", default="pending", choices=["pending", "approved", "rejected", "quarantined", "all"])
    rp.set_defaults(func=cmd_review_list)

    rp = review_sub.add_parser("inbox", help="Show review candidates with source, risk, and operator handles")
    rp.add_argument("--status", default="open", choices=["open", "pending", "approved", "rejected", "quarantined", "all"])
    rp.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    rp.add_argument("--limit", type=int, default=50)
    rp.set_defaults(func=cmd_review_inbox)

    rp = review_sub.add_parser("batch", help="Approve or reject multiple review candidates")
    rp.add_argument("action", choices=["approve", "reject"])
    rp.add_argument("candidate_ids", nargs="+")
    rp.add_argument("--actor", default="reviewer")
    rp.add_argument("--reason", default="")
    rp.add_argument("--dry-run", action="store_true")
    rp.add_argument("--stop-on-error", action="store_true")
    rp.set_defaults(func=cmd_review_batch)

    rp = review_sub.add_parser("approve", help="Promote a candidate to active memory")
    rp.add_argument("candidate_id")
    rp.add_argument("--actor", default="user")
    rp.add_argument("--reason", default="")
    rp.set_defaults(func=cmd_review_approve)

    rp = review_sub.add_parser("reject", help="Reject a candidate memory")
    rp.add_argument("candidate_id")
    rp.add_argument("--actor", default="user")
    rp.add_argument("--reason", default="")
    rp.set_defaults(func=cmd_review_reject)

    p = sub.add_parser("notifications", help="Inspect and manage operator notifications")
    add_common_db(p)
    notifications_sub = p.add_subparsers(dest="notifications_command", required=True)

    np = notifications_sub.add_parser("list", help="List memory notifications")
    np.add_argument("--status", default="open", choices=["open", "acknowledged", "resolved", "all"])
    np.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    np.add_argument("--topic")
    np.add_argument("--severity", choices=["info", "warning", "high", "critical"])
    np.add_argument("--assigned-to")
    np.add_argument(
        "--sla-status",
        choices=["overdue", "due_soon", "on_track", "no_due_date", "invalid_due_date", "resolved"],
    )
    np.add_argument("--target-type")
    np.add_argument("--target-id")
    np.add_argument("--limit", type=int, default=50)
    np.set_defaults(func=cmd_notifications_list)

    np = notifications_sub.add_parser("escalations", help="List SLA-driven notification escalations")
    np.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    np.add_argument("--assigned-to")
    np.add_argument("--open-only", action="store_true")
    np.add_argument("--limit", type=int, default=50)
    np.set_defaults(func=cmd_notifications_escalations)

    np = notifications_sub.add_parser("transport", help="Build notification transport payloads")
    np.add_argument("--transport", default="webhook", choices=["webhook", "email", "push"])
    np.add_argument("--status", default="open", choices=["open", "acknowledged", "resolved", "all"])
    np.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    np.add_argument("--topic")
    np.add_argument("--severity", choices=["info", "warning", "high", "critical"])
    np.add_argument("--assigned-to")
    np.add_argument(
        "--sla-status",
        choices=["overdue", "due_soon", "on_track", "no_due_date", "invalid_due_date", "resolved"],
    )
    np.add_argument("--limit", type=int, default=50)
    np.set_defaults(func=cmd_notifications_transport)

    np = notifications_sub.add_parser("delivery-enqueue", help="Queue notification transport payloads for external senders")
    np.add_argument("--transport", default="webhook", choices=["webhook", "email", "push"])
    np.add_argument("--destination", default="")
    np.add_argument("--status", default="open", choices=["open", "acknowledged", "resolved", "all"])
    np.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    np.add_argument("--topic")
    np.add_argument("--severity", choices=["info", "warning", "high", "critical"])
    np.add_argument("--assigned-to")
    np.add_argument(
        "--sla-status",
        choices=["overdue", "due_soon", "on_track", "no_due_date", "invalid_due_date", "resolved"],
    )
    np.add_argument("--actor", default="operator")
    np.add_argument("--limit", type=int, default=50)
    np.add_argument("--no-dedupe", action="store_true")
    np.set_defaults(func=cmd_notifications_delivery_enqueue)

    np = notifications_sub.add_parser("delivery-list", help="List notification delivery outbox rows")
    np.add_argument("--status", default="queued", choices=["queued", "sending", "delivered", "failed", "all"])
    np.add_argument("--transport", choices=["webhook", "email", "push"])
    np.add_argument("--notification-id")
    np.add_argument("--destination")
    np.add_argument("--limit", type=int, default=50)
    np.set_defaults(func=cmd_notifications_delivery_list)

    np = notifications_sub.add_parser("delivery-mark", help="Mark a notification delivery row")
    np.add_argument("delivery_id")
    np.add_argument("--status", required=True, choices=["sending", "delivered", "failed"])
    np.add_argument("--actor", default="sender")
    np.add_argument("--error", default="")
    np.set_defaults(func=cmd_notifications_delivery_mark)

    np = notifications_sub.add_parser("assign", help="Assign a memory notification to an operator")
    np.add_argument("notification_id")
    np.add_argument("--assigned-to", required=True)
    np.add_argument("--actor", default="reviewer")
    np.add_argument("--due-at", default="")
    np.add_argument("--reason", default="")
    np.set_defaults(func=cmd_notifications_assign)

    np = notifications_sub.add_parser("ack", help="Acknowledge a memory notification")
    np.add_argument("notification_id")
    np.add_argument("--actor", default="reviewer")
    np.add_argument("--reason", default="")
    np.set_defaults(func=cmd_notifications_ack)

    np = notifications_sub.add_parser("resolve", help="Resolve a memory notification")
    np.add_argument("notification_id")
    np.add_argument("--actor", default="reviewer")
    np.add_argument("--reason", default="")
    np.set_defaults(func=cmd_notifications_resolve)

    p = sub.add_parser("search", help="Search active memories")
    add_common_db(p)
    p.add_argument("query")
    p.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    p.add_argument("--limit", type=int, default=5)
    p.add_argument("--actor", default="agent")
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("context-pack", help="Build a cited context pack for an agent")
    add_common_db(p)
    p.add_argument("query")
    p.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    p.add_argument("--limit", type=int, default=5)
    p.add_argument("--actor", default="agent")
    p.set_defaults(func=cmd_context_pack)

    p = sub.add_parser("build-context", help="Build a full agent context with memory tree supplement")
    add_common_db(p)
    p.add_argument("query")
    p.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    p.add_argument("--thread-id", default="default")
    p.add_argument("--limit", type=int, default=8)
    p.add_argument("--recent-messages", type=int, default=6)
    p.add_argument("--actor", default="agent")
    p.set_defaults(func=cmd_build_context)

    p = sub.add_parser("before-model-call", help="Build a provider-neutral memory prompt envelope")
    add_common_db(p)
    p.add_argument("query")
    p.add_argument("--thread-id", default="default")
    p.add_argument("--scope", default="professional", choices=["personal", "professional", "project", "agent", "session"])
    p.add_argument("--user-id", default="user_default")
    p.add_argument("--agent-id", default="agent")
    p.add_argument("--model-id", default="")
    p.add_argument("--mode", default="chat")
    p.add_argument("--token-budget", type=int, default=12000)
    p.add_argument("--requested-lanes", default="", help="Comma-separated memory lanes")
    p.add_argument("--allowed-scopes", default="", help="Comma-separated scopes allowed for retrieval")
    p.add_argument("--denied-scopes", default="", help="Comma-separated scopes denied for retrieval")
    p.add_argument("--limit", type=int, default=8)
    p.add_argument("--recent-messages", type=int, default=6)
    p.add_argument("--prompt-format", default="", choices=["", "openai", "anthropic", "google", "gemini", "local"])
    p.add_argument("--disable-brain-style", action="store_true", help="Omit graph-derived style hints")
    p.set_defaults(func=cmd_before_model_call)

    p = sub.add_parser("read-time-policy", help="Show the Router read-time decision policy")
    add_common_db(p)
    p.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    p.add_argument("--model-id", default="")
    p.add_argument("--token-budget", type=int, default=0)
    p.add_argument("--limit", type=int, default=0)
    p.set_defaults(func=cmd_read_time_policy)

    p = sub.add_parser("prompt-budget", help="Resolve the effective memory prompt budget for a model")
    add_common_db(p)
    p.add_argument("--model-id", default="", help="Main model id, such as gpt-4.1-mini or claude-sonnet")
    p.add_argument("--token-budget", type=int, default=0, help="Requested memory token budget")
    p.set_defaults(func=cmd_prompt_budget)

    p = sub.add_parser("prompt-format-certify", help="Certify provider prompt formatters")
    add_common_db(p)
    p.add_argument("--providers", default="", help="Comma-separated providers: openai, anthropic, gemini, local")
    p.add_argument("--model-id", default="", help="Optional model id for budget/profile metadata")
    p.set_defaults(func=cmd_prompt_format_certify)

    p = sub.add_parser("embedding-certify", help="Certify embedding/rerank contract")
    add_common_db(p)
    p.add_argument("--provider", default="local", help="Provider label for the certification report")
    p.add_argument("--dims", type=int, default=32)
    p.set_defaults(func=cmd_embedding_certify)

    p = sub.add_parser("router-runs", help="List Router runs and prompt-facing memory reads")
    add_common_db(p)
    p.add_argument("--thread-id")
    p.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    p.add_argument("--limit", type=int, default=50)
    p.set_defaults(func=cmd_router_runs)

    p = sub.add_parser("router-explain", help="Explain why a Router run selected memory")
    add_common_db(p)
    p.add_argument("router_run_id")
    p.set_defaults(func=cmd_router_explain)

    p = sub.add_parser("memory-explain", help="Explain why one memory exists")
    add_common_db(p)
    p.add_argument("memory_id")
    p.set_defaults(func=cmd_memory_explain)

    p = sub.add_parser("router-feedback", help="Record or list Router memory usefulness feedback")
    add_common_db(p)
    feedback_sub = p.add_subparsers(dest="router_feedback_command", required=True)

    fp = feedback_sub.add_parser("record", help="Record whether selected memory helped")
    fp.add_argument("router_run_id")
    fp.add_argument("--memory-id", default="")
    fp.add_argument("--branch-id", default="")
    fp.add_argument(
        "--rating",
        default="neutral",
        choices=["helpful", "neutral", "ignored", "missing", "harmful"],
    )
    fp.add_argument("--score", type=float)
    fp.add_argument("--actor", default="reviewer")
    fp.add_argument("--reason", default="")
    fp.add_argument("--metadata-json", default="{}")
    fp.set_defaults(func=cmd_router_feedback_record)

    fp = feedback_sub.add_parser("list", help="List Router feedback")
    fp.add_argument("--router-run-id")
    fp.add_argument("--memory-id")
    fp.add_argument("--rating", choices=["helpful", "neutral", "ignored", "missing", "harmful"])
    fp.add_argument("--limit", type=int, default=50)
    fp.set_defaults(func=cmd_router_feedback_list)

    p = sub.add_parser("memory-quality", help="Summarize Router feedback quality signals")
    add_common_db(p)
    p.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    p.add_argument("--limit", type=int, default=10)
    p.set_defaults(func=cmd_memory_quality)

    p = sub.add_parser("observability", help="Summarize Router, Keeper, and usage telemetry")
    add_common_db(p)
    p.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    p.add_argument("--thread-id")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--router-latency-slo-ms", type=float, default=750.0)
    p.add_argument("--keeper-latency-slo-ms", type=float, default=2500.0)
    p.set_defaults(func=cmd_observability)

    p = sub.add_parser("dashboard", help="Aggregate local memory operations health")
    add_common_db(p)
    p.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    p.add_argument("--thread-id")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--stale-after-seconds", type=int, default=300)
    p.add_argument("--summary-only", action="store_true", help="Omit nested component reports")
    p.set_defaults(func=cmd_dashboard)

    p = sub.add_parser("billing-reconcile", help="Reconcile recorded LLM usage costs")
    add_common_db(p)
    p.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    p.add_argument("--thread-id")
    p.add_argument("--provider")
    p.add_argument("--currency")
    p.add_argument("--since", help="Inclusive created_at lower bound, ISO timestamp recommended")
    p.add_argument("--until", help="Inclusive created_at upper bound, ISO timestamp recommended")
    p.add_argument("--expected-cost", type=float)
    p.add_argument("--expected-currency", default="USD")
    p.add_argument("--tolerance", type=float, default=0.01)
    p.add_argument("--max-cost-per-1k", type=float)
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(func=cmd_billing_reconcile)

    p = sub.add_parser("billing-invoice", help="Import and inspect provider invoice line items")
    add_common_db(p)
    invoice_sub = p.add_subparsers(dest="billing_invoice_command", required=True)

    ip = invoice_sub.add_parser("import", help="Import a provider invoice JSON file")
    ip.add_argument("--file", required=True, help="JSON invoice file with line_items")
    ip.add_argument("--invoice-id", default="", help="Fallback invoice id if omitted in the file")
    ip.add_argument("--provider", default="", help="Fallback provider if omitted in the file")
    ip.add_argument("--period-start", default="", help="Fallback invoice period start")
    ip.add_argument("--period-end", default="", help="Fallback invoice period end")
    ip.add_argument("--currency", default="USD", help="Fallback invoice currency")
    ip.add_argument("--actor", default="operator")
    ip.add_argument("--source-ref", default="")
    ip.add_argument("--overwrite", action="store_true")
    ip.set_defaults(func=cmd_billing_invoice_import)

    ip = invoice_sub.add_parser("list", help="List imported provider invoice line items")
    ip.add_argument("--invoice-id", default="")
    ip.add_argument("--provider", default="")
    ip.add_argument("--scope", choices=["", "all", "personal", "professional", "project", "agent", "session"], default="")
    ip.add_argument("--thread-id", default="")
    ip.add_argument("--currency", default="")
    ip.add_argument("--since", default="")
    ip.add_argument("--until", default="")
    ip.add_argument("--status", choices=["active", "replaced", "all"], default="active")
    ip.add_argument("--limit", type=int, default=50)
    ip.set_defaults(func=cmd_billing_invoice_list)

    p = sub.add_parser("migration-status", help="Check local schema and migration compatibility")
    add_common_db(p)
    p.add_argument("--skip-integrity-check", action="store_true")
    p.set_defaults(func=cmd_migration_status)

    p = sub.add_parser("kernel-status", help="Report kernel API, contract, schema, and compatibility versions")
    add_common_db(p)
    p.add_argument("--skip-integrity-check", action="store_true")
    p.set_defaults(func=cmd_kernel_status)

    p = sub.add_parser("audit-integrity", help="Verify local audit-log tamper-evidence hash chain")
    add_common_db(p)
    p.add_argument("--limit", type=int, default=20, help="Maximum audit integrity failures to return")
    p.set_defaults(func=cmd_audit_integrity)

    p = sub.add_parser("migration-changelog", help="Summarize schema migrations and recent recovery events")
    add_common_db(p)
    p.add_argument("--limit", type=int, default=20, help="Maximum recent recovery audit events")
    p.set_defaults(func=cmd_migration_changelog)

    p = sub.add_parser("backup", help="Create a SQLite backup of the memory database")
    add_common_db(p)
    p.add_argument("--out", required=True, help="Backup database path to create")
    p.add_argument("--actor", default="operator")
    p.add_argument("--overwrite", action="store_true")
    p.set_defaults(func=cmd_backup)

    p = sub.add_parser("restore", help="Restore a SQLite backup into a target database path")
    p.add_argument("--backup", required=True, help="Backup database path to restore from")
    p.add_argument("--target-db", required=True, help="Target database path to create")
    p.add_argument("--actor", default="operator")
    p.add_argument("--overwrite", action="store_true")
    p.set_defaults(func=cmd_restore)

    p = sub.add_parser("restore-drill", help="Run a backup/restore drill and verify the restored database")
    add_common_db(p)
    p.add_argument("--backup-path", default="", help="Optional backup artifact path to keep")
    p.add_argument("--target-db", default="", help="Optional restored database path to keep")
    p.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    p.add_argument("--probe-query", default="", help="Optional query that must be found after restore")
    p.add_argument("--actor", default="operator")
    p.add_argument("--overwrite", action="store_true")
    p.set_defaults(func=cmd_restore_drill)

    p = sub.add_parser("restore-drill-schedule", help="Manage local restore-drill schedules")
    add_common_db(p)
    schedule_sub = p.add_subparsers(dest="restore_drill_schedule_command", required=True)

    sp = schedule_sub.add_parser("set", help="Create or update a restore-drill schedule")
    sp.add_argument("--name", required=True)
    sp.add_argument("--interval-hours", type=int, default=24)
    sp.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    sp.add_argument("--probe-query", default="")
    sp.add_argument("--start-at", default="", help="ISO timestamp for the next due time")
    sp.add_argument("--artifact-dir", default="", help="Directory for retained drill artifacts")
    sp.add_argument("--retain-artifacts", action="store_true")
    sp.add_argument("--status", choices=["active", "paused"], default="active")
    sp.add_argument("--actor", default="operator")
    sp.set_defaults(func=cmd_restore_drill_schedule_set)

    sp = schedule_sub.add_parser("list", help="List restore-drill schedules")
    sp.add_argument("--status", choices=["active", "paused", "all"], default="active")
    sp.add_argument("--due-only", action="store_true")
    sp.add_argument("--limit", type=int, default=50)
    sp.set_defaults(func=cmd_restore_drill_schedule_list)

    sp = schedule_sub.add_parser("run-due", help="Run due restore-drill schedules")
    sp.add_argument("--limit", type=int, default=5)
    sp.add_argument("--actor", default="scheduler")
    sp.add_argument("--include-not-due", action="store_true")
    sp.set_defaults(func=cmd_restore_drill_schedule_run_due)

    p = sub.add_parser("current-best", help="Resolve current-best memory for a query or scope")
    add_common_db(p)
    p.add_argument("query", nargs="?", default="")
    p.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    p.add_argument("--limit", type=int, default=8)
    p.set_defaults(func=cmd_current_best)

    p = sub.add_parser("memory-changes", help="Inspect Keeper changes after saved turns")
    add_common_db(p)
    p.add_argument("--keeper-job-id", default="", help="Show one Keeper job change report")
    p.add_argument("--thread-id", default="", help="List recent Keeper changes for a thread")
    p.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(func=cmd_memory_changes)

    p = sub.add_parser("derived-invalidations", help="Inspect derived-memory invalidation records")
    add_common_db(p)
    p.add_argument("--memory-id", default="")
    p.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    p.add_argument("--action", default="", help="Lifecycle action such as correct, delete, distrust, expire, supersede")
    p.add_argument("--limit", type=int, default=50)
    p.set_defaults(func=cmd_derived_invalidations)

    p = sub.add_parser("derived-lineage", help="Explain derived-memory dependency lineage")
    add_common_db(p)
    p.add_argument("--memory-id", default="")
    p.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    p.add_argument("--action", default="", help="Lifecycle action such as correct, delete, distrust, expire, supersede")
    p.add_argument("--limit", type=int, default=50)
    p.set_defaults(func=cmd_derived_lineage)

    p = sub.add_parser("after-saved-turn", help="Run the conservative Keeper path after an exchange")
    add_common_db(p)
    p.add_argument("--thread-id", default="default")
    p.add_argument("--scope", default="professional", choices=["personal", "professional", "project", "agent", "session"])
    p.add_argument("--user-id", default="user_default")
    p.add_argument("--agent-id", default="agent")
    p.add_argument("--model-id", default="")
    p.add_argument("--user-text", default="")
    p.add_argument("--assistant-text", default="")
    p.add_argument("--turn-id", default="")
    p.add_argument("--approve", action="store_true", help="Auto-approve safe Keeper candidates")
    p.add_argument("--keeper-mode", default="sync", choices=["sync", "queued"], help="Run Keeper now or queue it")
    p.add_argument("--metadata-json", default="{}")
    p.set_defaults(func=cmd_after_saved_turn)

    p = sub.add_parser("shadow-turn", help="Run a propose-only Router/Keeper trace for shadow rollout")
    add_common_db(p)
    p.add_argument("query")
    p.add_argument("--thread-id", default="default")
    p.add_argument("--scope", default="professional", choices=["personal", "professional", "project", "agent", "session"])
    p.add_argument("--user-id", default="user_default")
    p.add_argument("--agent-id", default="agent")
    p.add_argument("--model-id", default="")
    p.add_argument("--mode", default="shadow")
    p.add_argument("--token-budget", type=int, default=12000)
    p.add_argument("--requested-lanes", default="", help="Comma-separated memory lanes")
    p.add_argument("--allowed-scopes", default="", help="Comma-separated scopes allowed for retrieval")
    p.add_argument("--denied-scopes", default="", help="Comma-separated scopes denied for retrieval")
    p.add_argument("--limit", type=int, default=8)
    p.add_argument("--recent-messages", type=int, default=6)
    p.add_argument("--user-text", default="")
    p.add_argument("--assistant-text", default="")
    p.add_argument("--keeper-mode", default="sync", choices=["sync", "queued"], help="Run Keeper now or queue it")
    p.add_argument("--disable-brain-style", action="store_true", help="Omit graph-derived style hints")
    p.add_argument("--metadata-json", default="{}")
    p.set_defaults(func=cmd_shadow_turn)

    p = sub.add_parser("shadow-traces", help="List recorded shadow-mode traces")
    add_common_db(p)
    p.add_argument("--thread-id")
    p.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    p.add_argument("--limit", type=int, default=50)
    p.set_defaults(func=cmd_shadow_traces)

    p = sub.add_parser("shadow-eval", help="Evaluate a shadow trace against expected Router/Keeper behavior")
    add_common_db(p)
    p.add_argument("shadow_trace_id")
    p.add_argument("--expected-json", default="{}")
    p.add_argument("--actor", default="reviewer")
    p.add_argument("--metadata-json", default="{}")
    p.set_defaults(func=cmd_shadow_eval)

    p = sub.add_parser("shadow-evals", help="List stored shadow trace evaluations")
    add_common_db(p)
    p.add_argument("--shadow-trace-id")
    p.add_argument("--status", choices=["pass", "fail"])
    p.add_argument("--limit", type=int, default=50)
    p.set_defaults(func=cmd_shadow_evals)

    p = sub.add_parser("outcome", help="Record and retrieve first-class loop outcomes")
    add_common_db(p)
    outcome_sub = p.add_subparsers(dest="outcome_command", required=True)

    op = outcome_sub.add_parser("record", help="Record a structured attempt/outcome")
    op.add_argument("--project", required=True)
    op.add_argument("--loop-id", default="")
    op.add_argument("--status", default="unknown", choices=["success", "failure", "mixed", "unknown"])
    op.add_argument("--score", type=float, default=0.0)
    op.add_argument("--hypothesis", default="")
    op.add_argument("--action", default="")
    op.add_argument("--result", default="")
    op.add_argument("--cause", default="")
    op.add_argument("--lesson", default="")
    op.add_argument("--next-recommendation", default="")
    op.add_argument("--scope", default="professional", choices=["personal", "professional", "project", "agent", "session"])
    op.add_argument("--actor", default="user")
    op.add_argument("--approve", action="store_true", help="Auto-approve the generated outcome memory")
    op.add_argument("--metadata-json", default="{}")
    op.set_defaults(func=cmd_outcome_record)

    op = outcome_sub.add_parser("list", help="List outcome records")
    op.add_argument("--project")
    op.add_argument("--status", choices=["success", "failure", "mixed", "unknown"])
    op.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    op.add_argument("--record-status", choices=["pending", "active", "quarantined", "rejected"])
    op.add_argument("--limit", type=int, default=50)
    op.set_defaults(func=cmd_outcome_list)

    op = outcome_sub.add_parser("pack", help="Build an outcome memory pack for planning")
    op.add_argument("--project", required=True)
    op.add_argument("--scope", default="professional", choices=["personal", "professional", "project", "agent", "session"])
    op.add_argument("--limit", type=int, default=8)
    op.set_defaults(func=cmd_outcome_pack)

    op = outcome_sub.add_parser("compare", help="Compare success/failure outcomes and extract lessons")
    op.add_argument("--project", required=True)
    op.add_argument("--scope", default="professional", choices=["personal", "professional", "project", "agent", "session"])
    op.add_argument("--limit", type=int, default=50)
    op.set_defaults(func=cmd_outcome_compare)

    p = sub.add_parser("tree-pack", help="Build a branch-oriented memory tree pack for an agent")
    add_common_db(p)
    p.add_argument("query")
    p.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    p.add_argument("--limit", type=int, default=8)
    p.add_argument("--depth", type=int, default=1, help="Graph neighbor depth, 0-3")
    p.add_argument("--raw-chars", type=int, default=1600, help="Max raw event excerpt characters")
    p.add_argument("--no-raw", action="store_true", help="Omit raw provenance excerpts")
    p.add_argument("--actor", default="agent")
    p.set_defaults(func=cmd_tree_pack)

    p = sub.add_parser("turn", help="Record a conversation turn and optional memory candidate")
    add_common_db(p)
    p.add_argument("content")
    p.add_argument("--thread-id", default="default")
    p.add_argument("--role", default="user", choices=["user", "assistant", "system", "tool"])
    p.add_argument("--actor", default="user")
    p.add_argument("--scope", default="professional", choices=["personal", "professional", "project", "agent", "session"])
    p.add_argument("--remember", action="store_true", help="Also ingest the turn as a memory event")
    p.add_argument("--approve", action="store_true", help="Auto-approve safe trusted-source memory")
    p.set_defaults(func=cmd_turn)

    p = sub.add_parser("summary", help="Record a rolling thread summary")
    add_common_db(p)
    p.add_argument("summary")
    p.add_argument("--thread-id", default="default")
    p.add_argument("--scope", default="professional", choices=["personal", "professional", "project", "agent", "session"])
    p.add_argument("--summary-type", default="rolling", choices=["rolling", "session", "project", "manual"])
    p.add_argument("--source-memory-id", action="append", default=[], help="Memory id used as summary source; repeatable")
    p.set_defaults(func=cmd_summary)

    p = sub.add_parser("graph", help="Inspect the persistent memory graph tree")
    add_common_db(p)
    graph_sub = p.add_subparsers(dest="graph_command", required=True)

    gp = graph_sub.add_parser("items", help="List compact memory items")
    gp.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    gp.add_argument("--type")
    gp.add_argument("--limit", type=int, default=50)
    gp.set_defaults(func=cmd_graph_items)

    gp = graph_sub.add_parser("nodes", help="List memory graph nodes")
    gp.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    gp.add_argument("--type")
    gp.add_argument("--limit", type=int, default=50)
    gp.set_defaults(func=cmd_graph_nodes)

    gp = graph_sub.add_parser("edges", help="List memory graph edges")
    gp.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    gp.add_argument("--limit", type=int, default=50)
    gp.set_defaults(func=cmd_graph_edges)

    gp = graph_sub.add_parser("browser", help="Build graph browser data with source previews")
    gp.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    gp.add_argument("--type")
    gp.add_argument("--query", default="")
    gp.add_argument("--limit", type=int, default=50)
    gp.add_argument("--evidence-limit", type=int, default=3)
    gp.set_defaults(func=cmd_graph_browser)

    gp = graph_sub.add_parser("keeper-runs", help="List Keeper extraction runs")
    gp.add_argument("--limit", type=int, default=50)
    gp.set_defaults(func=cmd_graph_keeper)

    gp = graph_sub.add_parser("groups", help="List graph groups")
    gp.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    gp.set_defaults(func=cmd_graph_groups)

    gp = graph_sub.add_parser("analyses", help="List Light Model semantic analyses")
    gp.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    gp.add_argument("--limit", type=int, default=50)
    gp.set_defaults(func=cmd_graph_analyses)

    gp = graph_sub.add_parser("optimize", help="Run a graph optimization pass")
    gp.add_argument("--scope", default="professional", choices=["personal", "professional", "project", "agent", "session"])
    gp.add_argument(
        "--mode",
        default="record_linkage",
        choices=[
            "record_linkage",
            "consolidate_duplicates",
            "knowledge_consistency",
            "decay_stale",
            "llm_check",
            "interests_reconnect",
            "hemisphere_markup",
            "brain_calibration",
        ],
    )
    gp.set_defaults(func=cmd_graph_optimize)

    gp = graph_sub.add_parser("optimization-runs", help="List graph optimization runs")
    gp.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    gp.add_argument("--limit", type=int, default=50)
    gp.set_defaults(func=cmd_graph_optimization_runs)

    gp = graph_sub.add_parser("brain", help="Show digital brain calibration state")
    gp.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    gp.set_defaults(func=cmd_graph_brain)

    gp = graph_sub.add_parser("brain-style", help="Show guarded Digital Brain style append")
    gp.add_argument("--scope", default="professional", choices=["personal", "professional", "project", "agent", "session"])
    gp.set_defaults(func=cmd_graph_brain_style)

    p = sub.add_parser("brain-style-certify", help="Certify guarded graph-derived style behavior")
    add_common_db(p)
    p.add_argument("--scope", default="professional", choices=["personal", "professional", "project", "agent", "session"])
    p.set_defaults(func=cmd_brain_style_certify)

    gp = graph_sub.add_parser("tree", help="Build a Memory Tree Pack from graph nodes")
    gp.add_argument("query")
    gp.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    gp.add_argument("--limit", type=int, default=8)
    gp.add_argument("--depth", type=int, default=1)
    gp.add_argument("--raw-chars", type=int, default=1600)
    gp.add_argument("--no-raw", action="store_true")
    gp.add_argument("--actor", default="agent")
    gp.set_defaults(func=cmd_graph_tree)

    p = sub.add_parser("profile", help="Manage intro, rules, and project profile metadata")
    add_common_db(p)
    profile_sub = p.add_subparsers(dest="profile_command", required=True)

    pp = profile_sub.add_parser("set-intro", help="Set the profile intro")
    pp.add_argument("content")
    pp.add_argument("--scope", default="professional", choices=["personal", "professional", "project", "agent", "session"])
    pp.add_argument("--title", default="My intro")
    pp.set_defaults(func=cmd_profile_set_intro)

    pp = profile_sub.add_parser("add-rule", help="Add a profile rule")
    pp.add_argument("content")
    pp.add_argument("--scope", default="professional", choices=["personal", "professional", "project", "agent", "session"])
    pp.add_argument("--title", default="My rule")
    pp.set_defaults(func=cmd_profile_add_rule)

    pp = profile_sub.add_parser("list", help="List profile notes")
    pp.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    pp.add_argument("--type", choices=["intro", "rule"])
    pp.set_defaults(func=cmd_profile_list)

    pp = profile_sub.add_parser("project", help="Upsert project profile metadata")
    pp.add_argument("--scope", default="professional", choices=["personal", "professional", "project", "agent", "session"])
    pp.add_argument("--project", default="")
    pp.add_argument("--access-json", default="{}")
    pp.add_argument("--env-json", default="{}")
    pp.add_argument("--models-json", default="{}")
    pp.add_argument("--data-json", default="{}")
    pp.set_defaults(func=cmd_profile_project)

    p = sub.add_parser("usage", help="Record or list LLM usage stats")
    add_common_db(p)
    usage_sub = p.add_subparsers(dest="usage_command", required=True)

    up = usage_sub.add_parser("record", help="Record one LLM usage event")
    up.add_argument("--provider", default="openai")
    up.add_argument("--model", required=True)
    up.add_argument("--scope", default="professional", choices=["personal", "professional", "project", "agent", "session"])
    up.add_argument("--thread-id", default="")
    up.add_argument("--prompt-tokens", type=int, default=0)
    up.add_argument("--completion-tokens", type=int, default=0)
    up.add_argument("--cost", type=float, default=0.0)
    up.add_argument("--currency", default="USD")
    up.set_defaults(func=cmd_usage_record)

    up = usage_sub.add_parser("list", help="List LLM usage events")
    up.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    up.add_argument("--thread-id")
    up.add_argument("--limit", type=int, default=50)
    up.set_defaults(func=cmd_usage_list)

    p = sub.add_parser("export-profile", help="Export project profile with memory tree and usage stats")
    add_common_db(p)
    p.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    p.add_argument("--project", default="")
    p.add_argument("--actor", default="user")
    p.add_argument("--redaction-profile", default="full", choices=["full", "safe", "metadata"])
    p.add_argument("--approval-id", default="")
    p.add_argument("--retention-days", type=int)
    p.set_defaults(func=cmd_export_profile)

    p = sub.add_parser("export-control", help="Preview export policy and aggregate memory counts")
    add_common_db(p)
    p.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    p.add_argument("--project", default="")
    p.add_argument("--actor", default="user")
    p.add_argument("--redaction-profile", default="full", choices=["full", "safe", "metadata"])
    p.add_argument("--approval-id", default="")
    p.add_argument("--retention-days", type=int)
    p.set_defaults(func=cmd_export_control)

    p = sub.add_parser("export-custody", help="Preview encrypted export key and artifact custody")
    add_common_db(p)
    p.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    p.add_argument("--project", default="")
    p.add_argument("--actor", default="user")
    p.add_argument("--redaction-profile", default="safe", choices=["full", "safe", "metadata"])
    p.add_argument("--approval-id", default="")
    p.add_argument("--retention-days", type=int)
    p.add_argument("--artifact-ref", default="")
    p.add_argument("--passphrase-env", default="AGENT_MEMORY_EXPORT_PASSPHRASE")
    p.add_argument("--local-artifact-ok", action="store_true")
    p.set_defaults(func=cmd_export_custody)

    p = sub.add_parser("export-approval", help="Request or decide sensitive export approval")
    add_common_db(p)
    approval_sub = p.add_subparsers(dest="export_approval_command", required=True)

    ap = approval_sub.add_parser("request", help="Request approval for a sensitive full export")
    ap.add_argument("--actor", default="user", help="Actor that will perform the export")
    ap.add_argument("--requested-by", default="", help="Operator requesting approval")
    ap.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    ap.add_argument("--project", default="")
    ap.add_argument("--export-kind", default="profile", choices=["profile", "markdown"])
    ap.add_argument("--redaction-profile", default="full", choices=["full", "safe", "metadata"])
    ap.add_argument("--reason", default="")
    ap.add_argument("--metadata-json", default="{}")
    ap.set_defaults(func=cmd_export_approval_request)

    ap = approval_sub.add_parser("list", help="List export approval requests")
    ap.add_argument("--status", default="pending", choices=["pending", "approved", "rejected", "used", "not_required", "all"])
    ap.add_argument("--actor")
    ap.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    ap.add_argument("--limit", type=int, default=50)
    ap.set_defaults(func=cmd_export_approval_list)

    ap = approval_sub.add_parser("approve", help="Approve a sensitive export request")
    ap.add_argument("approval_id")
    ap.add_argument("--actor", default="reviewer")
    ap.add_argument("--reason", default="")
    ap.set_defaults(func=cmd_export_approval_approve)

    ap = approval_sub.add_parser("reject", help="Reject a sensitive export request")
    ap.add_argument("approval_id")
    ap.add_argument("--actor", default="reviewer")
    ap.add_argument("--reason", default="")
    ap.set_defaults(func=cmd_export_approval_reject)

    p = sub.add_parser("export-retention", help="Inspect and enforce export retention ledger")
    add_common_db(p)
    retention_sub = p.add_subparsers(dest="export_retention_command", required=True)

    rp = retention_sub.add_parser("list", help="List recorded exports")
    rp.add_argument("--status", default="active", choices=["active", "expired", "purged", "all"])
    rp.add_argument("--actor")
    rp.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    rp.add_argument("--expired-only", action="store_true")
    rp.add_argument("--limit", type=int, default=50)
    rp.set_defaults(func=cmd_export_retention_list)

    rp = retention_sub.add_parser("enforce", help="Mark export records expired after expires_at")
    rp.add_argument("--actor", default="system")
    rp.set_defaults(func=cmd_export_retention_enforce)

    rp = retention_sub.add_parser("purge", help="Mark an export record purged after artifact cleanup")
    rp.add_argument("export_id")
    rp.add_argument("--actor", default="reviewer")
    rp.add_argument("--reason", default="")
    rp.set_defaults(func=cmd_export_retention_purge)

    p = sub.add_parser("export-encrypted-profile", help="Write an encrypted project profile export")
    add_common_db(p)
    p.add_argument("--out", required=True)
    p.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    p.add_argument("--project", default="")
    p.add_argument("--actor", default="user")
    p.add_argument("--redaction-profile", default="full", choices=["full", "safe", "metadata"])
    p.add_argument("--approval-id", default="")
    p.add_argument("--retention-days", type=int)
    p.add_argument("--passphrase-env", default="AGENT_MEMORY_EXPORT_PASSPHRASE")
    p.add_argument("--passphrase-file", default="")
    p.set_defaults(func=cmd_export_encrypted_profile)

    p = sub.add_parser("import-profile", help="Import project profile JSON")
    add_common_db(p)
    p.add_argument("path")
    p.set_defaults(func=cmd_import_profile)

    p = sub.add_parser("export-bundle", help="Write a portable .amk profile bundle")
    add_common_db(p)
    p.add_argument("--out", required=True)
    p.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    p.add_argument("--project", default="")
    p.add_argument("--actor", default="user")
    p.add_argument("--redaction-profile", default="full", choices=["full", "safe", "metadata"])
    p.add_argument("--approval-id", default="")
    p.add_argument("--retention-days", type=int)
    p.set_defaults(func=cmd_export_bundle)

    p = sub.add_parser("verify-bundle", help="Verify a portable .amk bundle manifest")
    add_common_db(p)
    p.add_argument("path")
    p.set_defaults(func=cmd_verify_bundle)

    p = sub.add_parser("import-bundle", help="Import a verified portable .amk bundle")
    add_common_db(p)
    p.add_argument("path")
    p.set_defaults(func=cmd_import_bundle)

    p = sub.add_parser("vault", help="Export or import a machine-readable markdown memory vault")
    add_common_db(p)
    vault_sub = p.add_subparsers(dest="vault_command", required=True)
    vp = vault_sub.add_parser("export", help="Export active memory as a file-based vault")
    vp.add_argument("--out", default="agent-memory-vault")
    vp.add_argument("--actor", default="user")
    vp.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    vp.add_argument("--redaction-profile", default="full", choices=["full", "safe", "metadata"])
    vp.add_argument("--approval-id", default="")
    vp.add_argument("--retention-days", type=int)
    vp.set_defaults(func=cmd_vault_export)
    vp = vault_sub.add_parser("import", help="Import a file-based vault through review lifecycle")
    vp.add_argument("path")
    vp.add_argument("--actor", default="vault-import")
    vp.add_argument("--auto-approve", action="store_true")
    vp.set_defaults(func=cmd_vault_import)

    p = sub.add_parser("import-encrypted-profile", help="Import an encrypted project profile export")
    add_common_db(p)
    p.add_argument("path")
    p.add_argument("--passphrase-env", default="AGENT_MEMORY_EXPORT_PASSPHRASE")
    p.add_argument("--passphrase-file", default="")
    p.set_defaults(func=cmd_import_encrypted_profile)

    p = sub.add_parser("correct", help="Correct active memory text")
    add_common_db(p)
    p.add_argument("memory_id")
    p.add_argument("text")
    p.add_argument("--actor", default="user")
    p.add_argument("--reason", default="")
    p.set_defaults(func=cmd_correct)

    p = sub.add_parser("lifecycle-batch", help="Batch correct/delete/distrust/expire active memories")
    add_common_db(p)
    p.add_argument("--operations-json", default="")
    p.add_argument("--operations-file", default="")
    p.add_argument("--actor", default="reviewer")
    p.add_argument("--reason", default="")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--stop-on-error", action="store_true")
    p.set_defaults(func=cmd_lifecycle_batch)

    p = sub.add_parser("revisions", help="List correction and rollback history for memory")
    add_common_db(p)
    p.add_argument("memory_id")
    p.add_argument("--limit", type=int, default=50)
    p.set_defaults(func=cmd_revisions)

    p = sub.add_parser("rollback", help="Rollback memory text to a prior revision")
    add_common_db(p)
    p.add_argument("memory_id")
    p.add_argument("--revision-id", default="", help="Revision to restore; defaults to latest")
    p.add_argument("--actor", default="user")
    p.add_argument("--reason", default="")
    p.set_defaults(func=cmd_rollback)

    p = sub.add_parser("supersede", help="Mark old memory as superseded by newer memory")
    add_common_db(p)
    p.add_argument("old_memory_id")
    p.add_argument("new_memory_id")
    p.add_argument("--actor", default="user")
    p.add_argument("--reason", default="")
    p.set_defaults(func=cmd_supersede)

    p = sub.add_parser("conflict", help="Record or inspect memory conflicts")
    add_common_db(p)
    conflict_sub = p.add_subparsers(dest="conflict_command", required=True)

    cp = conflict_sub.add_parser("record", help="Record a conflict between two memories")
    cp.add_argument("memory_id")
    cp.add_argument("other_memory_id")
    cp.add_argument(
        "--relation",
        default="conflicts_with",
        choices=["conflicts_with", "contradicted_by", "supersedes", "context_bound"],
    )
    cp.add_argument("--winner-memory-id", default="")
    cp.add_argument("--actor", default="user")
    cp.add_argument("--reason", default="")
    cp.add_argument("--metadata-json", default="{}")
    cp.set_defaults(func=cmd_conflict_record)

    cp = conflict_sub.add_parser("list", help="List memory conflicts")
    cp.add_argument("--status", choices=["open", "resolved"])
    cp.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    cp.add_argument("--limit", type=int, default=50)
    cp.set_defaults(func=cmd_conflict_list)

    cp = conflict_sub.add_parser("detect", help="Detect likely active-memory conflicts")
    cp.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    cp.add_argument("--kind", default="")
    cp.add_argument("--limit", type=int, default=50)
    cp.add_argument("--min-overlap", type=float, default=0.5)
    cp.add_argument("--min-jaccard", type=float, default=0.35)
    cp.add_argument("--record", action="store_true", help="Record detected pairs as open conflicts")
    cp.add_argument("--actor", default="system")
    cp.add_argument("--reason", default="")
    cp.set_defaults(func=cmd_conflict_detect)

    p = sub.add_parser("delete", help="Soft-delete active memory")
    add_common_db(p)
    p.add_argument("memory_id")
    p.add_argument("--actor", default="user")
    p.add_argument("--reason", default="")
    p.set_defaults(func=cmd_delete)

    p = sub.add_parser("distrust", help="Keep memory for audit but suppress retrieval")
    add_common_db(p)
    p.add_argument("memory_id")
    p.add_argument("--actor", default="user")
    p.add_argument("--reason", default="")
    p.set_defaults(func=cmd_distrust)

    p = sub.add_parser("expire", help="Expire active memory and suppress retrieval")
    add_common_db(p)
    p.add_argument("memory_id")
    p.add_argument("--actor", default="system")
    p.add_argument("--reason", default="")
    p.set_defaults(func=cmd_expire)

    p = sub.add_parser("slice", help="Run the deterministic full-memory vertical slice")
    slice_sub = p.add_subparsers(dest="slice_command", required=True)

    sp = slice_sub.add_parser("seed", help="Seed the deterministic vertical slice fixture")
    add_common_db(sp)
    sp.set_defaults(func=cmd_slice_seed)

    sp = slice_sub.add_parser("run", help="Run Router and Keeper over the slice fixture")
    add_common_db(sp)
    sp.set_defaults(func=cmd_slice_run)

    sp = slice_sub.add_parser("assert", help="Assert the slice fixture satisfies runtime gates")
    add_common_db(sp)
    sp.set_defaults(func=cmd_slice_assert)

    p = sub.add_parser("contract", help="Show or validate the formal memory contract")
    contract_sub = p.add_subparsers(dest="contract_command")
    p.set_defaults(func=cmd_contract)

    cp = contract_sub.add_parser("assert", help="Validate the public memory contract shape")
    cp.set_defaults(func=cmd_contract_assert)

    p = sub.add_parser("acceptance", help="Run the full-memory acceptance harness")
    acceptance_sub = p.add_subparsers(dest="acceptance_command", required=True)

    ap = acceptance_sub.add_parser("seed", help="Seed the full-memory acceptance fixture")
    add_common_db(ap)
    ap.set_defaults(func=cmd_acceptance_seed)

    ap = acceptance_sub.add_parser("run", help="Run the acceptance suite and return pass/fail JSON")
    add_common_db(ap)
    ap.set_defaults(func=cmd_acceptance_run)

    ap = acceptance_sub.add_parser("assert", help="Run acceptance and fail the command on any failed gate")
    add_common_db(ap)
    ap.set_defaults(func=cmd_acceptance_assert)

    p = sub.add_parser("conformance", help="Run the public memory behavior conformance suite")
    conformance_sub = p.add_subparsers(dest="conformance_command", required=True)

    cp = conformance_sub.add_parser("spec", help="Print the versioned conformance scenarios")
    cp.set_defaults(func=cmd_conformance_spec)

    cp = conformance_sub.add_parser("spec-assert", help="Validate the conformance spec shape")
    cp.set_defaults(func=cmd_conformance_spec_assert)

    cp = conformance_sub.add_parser("seed", help="Seed the public conformance fixture")
    add_common_db(cp)
    cp.set_defaults(func=cmd_conformance_seed)

    cp = conformance_sub.add_parser("run", help="Run conformance scenarios and return pass/fail JSON")
    add_common_db(cp)
    cp.set_defaults(func=cmd_conformance_run)

    cp = conformance_sub.add_parser("assert", help="Run conformance and fail the command on any failed scenario")
    add_common_db(cp)
    cp.set_defaults(func=cmd_conformance_assert)

    cp = conformance_sub.add_parser("certify", help="Run conformance and emit an adapter badge report")
    add_common_db(cp)
    cp.add_argument("--adapter-name", default="local-runtime")
    cp.add_argument("--adapter-version", default="")
    cp.add_argument("--seed", action="store_true", help="Seed the public conformance fixture before certifying")
    cp.set_defaults(func=cmd_conformance_certify)

    cp = conformance_sub.add_parser("registry-entry", help="Emit a compact public adapter registry entry")
    add_common_db(cp)
    cp.add_argument("--adapter-name", default="local-runtime")
    cp.add_argument("--adapter-version", default="")
    cp.add_argument("--runtime", default="")
    cp.add_argument("--repository", default="")
    cp.add_argument("--homepage", default="")
    cp.add_argument("--maintainer", default="")
    cp.add_argument("--notes", default="")
    cp.add_argument("--seed", action="store_true", help="Seed the public conformance fixture before generating the entry")
    cp.set_defaults(func=cmd_conformance_registry_entry)

    p = sub.add_parser("keeper-eval", help="Run offline Keeper extraction evals")
    p.add_argument("--spec", action="store_true")
    p.set_defaults(func=cmd_keeper_eval)

    p = sub.add_parser("worker", help="Process queued Keeper jobs")
    add_common_db(p)
    p.add_argument("--once", action="store_true", help="Process one batch and exit")
    p.add_argument("--daemon", action="store_true", help="Poll queued Keeper jobs until stopped")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--actor", default="worker")
    p.add_argument("--poll-interval", type=float, default=5.0)
    p.add_argument("--max-iterations", type=int, default=0, help="Testing/supervisor limit; 0 means unlimited")
    p.add_argument("--stop-when-idle", action="store_true", help="Exit daemon mode after an idle poll")
    p.add_argument("--quiet", action="store_true", help="Suppress per-iteration daemon JSON logs")
    p.set_defaults(func=cmd_worker)

    p = sub.add_parser("worker-status", help="Report queued Keeper worker supervision health")
    add_common_db(p)
    p.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    p.add_argument("--stale-after-seconds", type=int, default=300)
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(func=cmd_worker_status)

    p = sub.add_parser("serve", help="Run the stdlib HTTP API service")
    add_common_db(p)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--auth-token", default="")
    p.add_argument("--auth-token-env", default="AGENT_MEMORY_API_TOKEN")
    p.set_defaults(func=cmd_serve)

    p = sub.add_parser("mcp", help="Run the stdio MCP server")
    add_common_db(p)
    p.set_defaults(func=cmd_mcp)

    p = sub.add_parser("export", help="Export active memories to a markdown vault")
    add_common_db(p)
    p.add_argument("--out", default="memory-vault")
    p.add_argument("--actor", default="user")
    p.add_argument("--redaction-profile", default="full", choices=["full", "safe", "metadata"])
    p.add_argument("--approval-id", default="")
    p.add_argument("--retention-days", type=int)
    p.set_defaults(func=cmd_export)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except Exception as exc:
        print(f"agent-memory: error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
