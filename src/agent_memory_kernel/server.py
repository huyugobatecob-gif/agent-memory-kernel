"""Small stdlib HTTP API for Agent Memory Kernel."""

from __future__ import annotations

import argparse
from html import escape
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

from .acceptance import assert_acceptance_suite, run_acceptance_suite, seed_acceptance_fixture
from .conformance import (
    assert_conformance_spec_shape,
    assert_conformance_suite,
    conformance_spec,
    run_conformance_suite,
    seed_conformance_fixture,
)
from .contract import assert_contract_shape, memory_contract
from .orchestrator import MemoryOrchestrator
from .slice import assert_vertical_slice, run_vertical_slice, seed_vertical_slice
from .store import MemoryStore


def _payload_passphrase(payload: dict[str, Any]) -> str:
    direct = str(payload.get("passphrase", "") or "")
    if direct:
        return direct
    env_name = str(payload.get("passphrase_env", "") or "AGENT_MEMORY_EXPORT_PASSPHRASE")
    value = os.environ.get(env_name, "")
    if not value:
        raise ValueError(f"passphrase not found in environment variable: {env_name}")
    return value


def handle_api_request(store: MemoryStore, path: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Dispatch one API request against an initialized store."""
    path = _normalize_path(path)
    if path == "/health":
        return {"status": "ok"}
    if path in {"/operational/status", "/operational-status"}:
        return store.operational_status(
            max_db_bytes=int(payload.get("max_db_bytes", 512 * 1024 * 1024) or 0),
            integrity_check=bool(payload.get("integrity_check", True)),
        )
    if path == "/contract":
        return memory_contract()
    if path == "/contract/assert":
        return assert_contract_shape()
    if path == "/conformance/spec":
        return conformance_spec()
    if path == "/conformance/spec/assert":
        return assert_conformance_spec_shape()
    orchestrator = MemoryOrchestrator(store)
    if path in {"/before-turn", "/orchestrator/before-turn"}:
        query = str(payload.pop("query", ""))
        return orchestrator.before_turn(query, **payload)
    if path in {"/build-prompt-context", "/orchestrator/build-prompt-context"}:
        query = str(payload.pop("query", ""))
        return orchestrator.build_prompt_context(query, **payload)
    if path in {"/retrieve-context", "/orchestrator/retrieve-context"}:
        query = str(payload.pop("query", ""))
        return orchestrator.retrieve_context(query, **payload)
    if path in {"/record-turn", "/orchestrator/record-turn"}:
        content = str(payload.pop("content", ""))
        return orchestrator.record_turn(content, **payload)
    if path in {"/keeper-analyze-turn", "/orchestrator/keeper-analyze-turn"}:
        payload = _normalize_after_turn_payload(payload)
        return orchestrator.keeper_analyze_turn(**payload)
    if path in {"/after-turn", "/orchestrator/after-turn"}:
        payload = _normalize_after_turn_payload(payload)
        return orchestrator.after_turn(**payload)
    if path in {"/ingest-graph", "/orchestrator/ingest-graph"}:
        updates = payload.pop("updates", [])
        return orchestrator.ingest_graph(updates, **payload)
    if path == "/before-model-call":
        return store.before_model_call(**payload)
    if path == "/read-time-policy":
        return store.read_time_policy(
            scope=payload.get("scope"),
            token_budget=int(payload.get("token_budget", 0) or 0),
            limit=int(payload.get("limit", 0) or 0),
        )
    if path == "/router-runs":
        return {
            "runs": store.list_router_runs(
                thread_id=payload.get("thread_id"),
                scope=payload.get("scope"),
                limit=int(payload.get("limit", 50) or 50),
            )
        }
    if path == "/router-explain":
        return store.explain_router_run(str(payload.get("router_run_id", "")))
    if path == "/router-feedback/record":
        router_run_id = str(payload.pop("router_run_id"))
        return store.record_router_feedback(router_run_id, **payload)
    if path == "/router-feedback/list":
        return {
            "feedback": store.list_router_feedback(
                router_run_id=payload.get("router_run_id"),
                memory_id=payload.get("memory_id"),
                rating=payload.get("rating"),
                limit=int(payload.get("limit", 50) or 50),
            )
        }
    if path == "/memory-quality":
        return store.memory_quality_report(
            scope=payload.get("scope"),
            limit=int(payload.get("limit", 10) or 10),
        )
    if path in {"/observability", "/memory-observability"}:
        return store.memory_observability_report(
            scope=payload.get("scope"),
            thread_id=payload.get("thread_id"),
            limit=int(payload.get("limit", 20) or 20),
        )
    if path in {"/migration/status", "/migration-status"}:
        return store.migration_status(
            integrity_check=bool(payload.get("integrity_check", True)),
        )
    if path == "/backup":
        return store.backup_database(
            payload.get("out_path") or payload.get("path"),
            actor=str(payload.get("actor", "api")),
            overwrite=bool(payload.get("overwrite", False)),
        )
    if path == "/restore":
        return MemoryStore.restore_database(
            payload.get("backup_path"),
            payload.get("target_path"),
            actor=str(payload.get("actor", "api")),
            overwrite=bool(payload.get("overwrite", False)),
        )
    if path == "/current-best":
        return store.current_best_report(
            str(payload.get("query", "")),
            scope=payload.get("scope"),
            limit=int(payload.get("limit", 8) or 8),
        )
    if path == "/memory-changes":
        return store.memory_changes(
            keeper_job_id=str(payload.get("keeper_job_id", "")),
            thread_id=payload.get("thread_id"),
            scope=payload.get("scope"),
            limit=int(payload.get("limit", 20) or 20),
        )
    if path in {"/notifications/list", "/notifications"}:
        return store.list_notifications(
            status=str(payload.get("status", "open")),
            scope=payload.get("scope"),
            topic=payload.get("topic"),
            severity=payload.get("severity"),
            assigned_to=payload.get("assigned_to"),
            sla_status=payload.get("sla_status"),
            target_type=payload.get("target_type"),
            target_id=payload.get("target_id"),
            limit=int(payload.get("limit", 50) or 50),
        )
    if path == "/notifications/escalations":
        return store.notification_escalations(
            scope=payload.get("scope"),
            assigned_to=payload.get("assigned_to"),
            include_acknowledged=bool(payload.get("include_acknowledged", True)),
            limit=int(payload.get("limit", 50) or 50),
        )
    if path == "/notifications/assign":
        return store.assign_notification(
            str(payload.get("notification_id", "")),
            assigned_to=str(payload.get("assigned_to", "")),
            actor=str(payload.get("actor", "reviewer")),
            due_at=str(payload.get("due_at", "")),
            reason=str(payload.get("reason", "")),
        )
    if path == "/notifications/ack":
        return store.ack_notification(
            str(payload.get("notification_id", "")),
            actor=str(payload.get("actor", "reviewer")),
            reason=str(payload.get("reason", "")),
        )
    if path == "/notifications/resolve":
        return store.resolve_notification(
            str(payload.get("notification_id", "")),
            actor=str(payload.get("actor", "reviewer")),
            reason=str(payload.get("reason", "")),
        )
    if path == "/derived-invalidations":
        return store.derived_invalidations(
            memory_id=str(payload.get("memory_id", "")),
            scope=payload.get("scope"),
            action=str(payload.get("action", "")),
            limit=int(payload.get("limit", 50) or 50),
        )
    if path == "/after-saved-turn":
        payload = _normalize_after_turn_payload(payload)
        return store.after_saved_turn(**payload)
    if path == "/shadow-turn":
        query = str(payload.pop("query", ""))
        return store.shadow_turn(query, **payload)
    if path == "/shadow-traces":
        return {
            "traces": store.list_shadow_traces(
                thread_id=payload.get("thread_id"),
                scope=payload.get("scope"),
                limit=int(payload.get("limit", 50) or 50),
            )
        }
    if path == "/shadow-eval":
        shadow_trace_id = str(payload.pop("shadow_trace_id"))
        return store.evaluate_shadow_trace(shadow_trace_id, **payload)
    if path == "/shadow-evals":
        return {
            "evals": store.list_shadow_evals(
                shadow_trace_id=payload.get("shadow_trace_id"),
                status=payload.get("status"),
                limit=int(payload.get("limit", 50) or 50),
            )
        }
    if path == "/outcome/record":
        return store.record_outcome(**payload)
    if path == "/outcome/list":
        return {
            "outcomes": store.list_outcomes(
                project=payload.get("project"),
                outcome_status=payload.get("outcome_status"),
                scope=payload.get("scope"),
                status=payload.get("status"),
                limit=int(payload.get("limit", 50) or 50),
            )
        }
    if path == "/outcome/pack":
        project = str(payload.pop("project"))
        return {"pack": store.outcome_pack(project=project, **payload)}
    if path == "/remember":
        text = str(payload.pop("text"))
        return store.remember(text, **payload)
    if path == "/graph/items":
        return {
            "items": store.list_memory_items(
                scope=payload.get("scope"),
                item_type=payload.get("item_type") or payload.get("type"),
                limit=int(payload.get("limit", 50) or 50),
            )
        }
    if path == "/graph/nodes":
        return {
            "nodes": store.list_graph_nodes(
                scope=payload.get("scope"),
                node_type=payload.get("node_type") or payload.get("type"),
                limit=int(payload.get("limit", 50) or 50),
            )
        }
    if path == "/graph/edges":
        return {
            "edges": store.list_graph_edges(
                scope=payload.get("scope"),
                limit=int(payload.get("limit", 50) or 50),
            )
        }
    if path == "/graph/browser":
        return store.graph_browser(
            scope=payload.get("scope"),
            node_type=payload.get("node_type") or payload.get("type"),
            query=str(payload.get("query", "")),
            limit=int(payload.get("limit", 50) or 50),
            evidence_limit=int(payload.get("evidence_limit", 3) or 3),
        )
    if path == "/write-policy/set":
        return store.set_write_policy(**payload)
    if path == "/write-policy/list":
        return {
            "policies": store.list_write_policies(
                agent_id=payload.get("agent_id"),
                scope=payload.get("scope"),
                action=payload.get("action"),
                limit=int(payload.get("limit", 100) or 100),
            )
        }
    if path == "/read-policy/set":
        return store.set_read_policy(**payload)
    if path == "/read-policy/list":
        return {
            "policies": store.list_read_policies(
                agent_id=payload.get("agent_id"),
                scope=payload.get("scope"),
                action=payload.get("action"),
                limit=int(payload.get("limit", 100) or 100),
            )
        }
    if path == "/capability/check":
        return store.capability_report(
            actor=str(payload.get("actor", "agent")),
            scope=str(payload.get("scope", "professional")),
            project=str(payload.get("project", "")),
            read_actions=payload.get("read_actions"),
            write_actions=payload.get("write_actions"),
        )
    if path == "/export/control":
        return store.export_control_report(
            actor=str(payload.get("actor", "user")),
            scope=payload.get("scope"),
            project=str(payload.get("project", "")),
            redaction_profile=str(payload.get("redaction_profile", "full")),
            approval_id=str(payload.get("approval_id", "")),
            retention_days=payload.get("retention_days"),
        )
    if path == "/export/approval/request":
        return store.request_export_approval(
            actor=str(payload.get("actor", "user")),
            requested_by=str(payload.get("requested_by", "")),
            scope=payload.get("scope"),
            project=str(payload.get("project", "")),
            export_kind=str(payload.get("export_kind", "profile")),
            redaction_profile=str(payload.get("redaction_profile", "full")),
            reason=str(payload.get("reason", "")),
            metadata=payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {},
        )
    if path == "/export/approval/list":
        return {
            "approvals": store.list_export_approvals(
                status=payload.get("status"),
                actor=payload.get("actor"),
                scope=payload.get("scope"),
                limit=int(payload.get("limit", 50) or 50),
            )
        }
    if path == "/export/approval/approve":
        return store.approve_export_approval(
            str(payload.get("approval_id", "")),
            actor=str(payload.get("actor", "reviewer")),
            reason=str(payload.get("reason", "")),
        )
    if path == "/export/approval/reject":
        return store.reject_export_approval(
            str(payload.get("approval_id", "")),
            actor=str(payload.get("actor", "reviewer")),
            reason=str(payload.get("reason", "")),
        )
    if path == "/export/retention/list":
        return {
            "exports": store.list_export_records(
                status=payload.get("status"),
                actor=payload.get("actor"),
                scope=payload.get("scope"),
                expired_only=bool(payload.get("expired_only", False)),
                limit=int(payload.get("limit", 50) or 50),
            )
        }
    if path == "/export/retention/enforce":
        return store.enforce_export_retention(actor=str(payload.get("actor", "system")))
    if path == "/export/retention/purge":
        return store.purge_export_record(
            str(payload.get("export_id", "")),
            actor=str(payload.get("actor", "reviewer")),
            reason=str(payload.get("reason", "")),
        )
    if path == "/search":
        query = str(payload.pop("query"))
        return {"results": store.search(query, **payload)}
    if path == "/context-pack":
        query = str(payload.pop("query"))
        return {"context": store.context_pack(query, **payload)}
    if path == "/tree-pack":
        query = str(payload.pop("query"))
        return {"tree": store.memory_tree_pack(query, **payload)}
    if path == "/brain/style":
        return store.brain_style_append(scope=str(payload.get("scope", "professional")))
    if path == "/export/profile":
        return store.export_profile(
            scope=payload.get("scope"),
            project=str(payload.get("project", "")),
            actor=str(payload.get("actor", "user")),
            redaction_profile=str(payload.get("redaction_profile", "full")),
            approval_id=str(payload.get("approval_id", "")),
            retention_days=payload.get("retention_days"),
            artifact_ref=str(payload.get("artifact_ref", "")),
        )
    if path == "/export/encrypted-profile":
        return store.export_encrypted_profile(
            passphrase=_payload_passphrase(payload),
            scope=payload.get("scope"),
            project=str(payload.get("project", "")),
            actor=str(payload.get("actor", "user")),
            redaction_profile=str(payload.get("redaction_profile", "full")),
            approval_id=str(payload.get("approval_id", "")),
            retention_days=payload.get("retention_days"),
            artifact_ref=str(payload.get("artifact_ref", "")),
        )
    if path == "/import/encrypted-profile":
        envelope = payload.get("envelope")
        if not isinstance(envelope, dict):
            raise ValueError("envelope must be provided as an object")
        return store.import_encrypted_profile(
            envelope,
            passphrase=_payload_passphrase(payload),
        )
    if path == "/review/inbox":
        return store.review_inbox(
            status=str(payload.get("status", "open")),
            scope=payload.get("scope"),
            limit=int(payload.get("limit", 50)),
        )
    if path == "/review/list":
        return {"candidates": store.list_candidates(str(payload.get("status", "pending")))}
    if path == "/review/batch":
        raw_ids = payload.pop("candidate_ids", [])
        if isinstance(raw_ids, str):
            candidate_ids = [item.strip() for item in raw_ids.split(",") if item.strip()]
        else:
            candidate_ids = [str(item) for item in raw_ids]
        return store.review_batch(
            action=str(payload.pop("action")),
            candidate_ids=candidate_ids,
            actor=str(payload.pop("actor", "reviewer")),
            reason=str(payload.pop("reason", "")),
            dry_run=bool(payload.pop("dry_run", False)),
            stop_on_error=bool(payload.pop("stop_on_error", False)),
        )
    if path == "/review/approve":
        candidate_id = str(payload.pop("candidate_id"))
        return {"memory_id": store.approve_candidate(candidate_id, **payload), "status": "active"}
    if path == "/review/reject":
        candidate_id = str(payload.pop("candidate_id"))
        store.reject_candidate(candidate_id, **payload)
        return {"candidate_id": candidate_id, "status": "rejected"}
    if path == "/memory/correct":
        memory_id = str(payload.pop("memory_id"))
        text = str(payload.pop("text"))
        store.correct_memory(memory_id, text, **payload)
        return {"memory_id": memory_id, "status": "corrected"}
    if path == "/memory/lifecycle-batch":
        return store.batch_memory_lifecycle(
            payload.get("operations", []),
            actor=str(payload.get("actor", "api")),
            reason=str(payload.get("reason", "")),
            dry_run=bool(payload.get("dry_run", False)),
            stop_on_error=bool(payload.get("stop_on_error", False)),
        )
    if path == "/memory/delete":
        memory_id = str(payload.pop("memory_id"))
        store.delete_memory(memory_id, **payload)
        return {"memory_id": memory_id, "status": "deleted"}
    if path == "/memory/distrust":
        memory_id = str(payload.pop("memory_id"))
        store.distrust_memory(memory_id, **payload)
        return {"memory_id": memory_id, "status": "distrusted"}
    if path == "/memory/expire":
        memory_id = str(payload.pop("memory_id"))
        store.expire_memory(memory_id, **payload)
        return {"memory_id": memory_id, "status": "expired"}
    if path == "/memory/revisions":
        memory_id = str(payload.pop("memory_id"))
        return {
            "revisions": store.list_memory_revisions(
                memory_id,
                limit=int(payload.get("limit", 50) or 50),
            )
        }
    if path == "/memory/rollback":
        memory_id = str(payload.pop("memory_id"))
        return store.rollback_memory(memory_id, **payload)
    if path == "/supersede":
        old_memory_id = str(payload.pop("old_memory_id"))
        new_memory_id = str(payload.pop("new_memory_id"))
        return store.supersede_memory(old_memory_id, new_memory_id, **payload)
    if path == "/conflict/record":
        memory_id = str(payload.pop("memory_id"))
        other_memory_id = str(payload.pop("other_memory_id"))
        return store.record_memory_conflict(memory_id, other_memory_id, **payload)
    if path == "/conflict/list":
        return {
            "conflicts": store.list_memory_conflicts(
                status=payload.get("status"),
                scope=payload.get("scope"),
                limit=int(payload.get("limit", 50) or 50),
            )
        }
    if path == "/conflict/detect":
        return store.detect_memory_conflicts(
            scope=payload.get("scope"),
            kind=payload.get("kind"),
            limit=int(payload.get("limit", 50) or 50),
            min_overlap=float(payload.get("min_overlap", 0.5) or 0.5),
            min_jaccard=float(payload.get("min_jaccard", 0.35) or 0.35),
            record=bool(payload.get("record", False)),
            actor=str(payload.get("actor", "system")),
            reason=str(payload.get("reason", "")),
        )
    if path == "/slice/seed":
        return seed_vertical_slice(store)
    if path == "/slice/run":
        return run_vertical_slice(store)
    if path == "/slice/assert":
        return assert_vertical_slice(store)
    if path == "/acceptance/seed":
        return seed_acceptance_fixture(store)
    if path == "/acceptance/run":
        return run_acceptance_suite(store)
    if path == "/acceptance/assert":
        return assert_acceptance_suite(store)
    if path == "/conformance/seed":
        return seed_conformance_fixture(store)
    if path == "/conformance/run":
        return run_conformance_suite(store)
    if path == "/conformance/assert":
        return assert_conformance_suite(store)
    if path == "/worker/run":
        return store.process_keeper_jobs(
            limit=int(payload.get("limit", 10) or 10),
            actor=str(payload.get("actor", "worker")),
        )
    raise KeyError(f"unknown endpoint: {path}")


def _normalize_after_turn_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(payload)
    if "user_message" in normalized and "user_text" not in normalized:
        normalized["user_text"] = normalized.pop("user_message")
    if "assistant_message" in normalized and "assistant_text" not in normalized:
        normalized["assistant_text"] = normalized.pop("assistant_message")

    metadata = dict(normalized.get("metadata") or {})
    for key in ("write_policy", "source_ref"):
        if key in normalized:
            metadata[key] = normalized.pop(key)
    if metadata:
        normalized["metadata"] = metadata
    return normalized


def render_review_ui(
    store: MemoryStore,
    *,
    status: str = "open",
    scope: str | None = None,
    limit: int = 50,
) -> str:
    safe_limit = max(1, min(int(limit or 50), 200))
    inbox = store.review_inbox(status=status, scope=scope or None, limit=safe_limit)
    summary = inbox.get("summary", {})
    summary_html = "".join(
        f"<span class=\"pill\"><strong>{_h(key)}</strong> {_h(value)}</span>"
        for key, value in sorted(summary.items())
    )
    items_html = "".join(_review_item_html(item) for item in inbox.get("items", []))
    if not items_html:
        items_html = "<p class=\"empty\">No candidates found.</p>"
    body = f"""
    <section class="toolbar">
      <form method="get" action="/ui/review" class="filters">
        <label>Status {_select("status", ["open", "pending", "quarantined", "approved", "rejected", "all"], str(inbox.get("status_filter", status)))}</label>
        <label>Scope <input name="scope" value="{_h(scope or "")}" placeholder="all"></label>
        <label>Limit <input name="limit" type="number" min="1" max="200" value="{_h(safe_limit)}"></label>
        <button type="submit">Apply</button>
      </form>
      <div class="summary">{summary_html or '<span class="pill">0 items</span>'}</div>
    </section>
    <section class="bulkbar">
      <div class="actions">
        <button data-batch-action="approve" data-dry-run="true">Preview Approve</button>
        <button data-batch-action="approve">Approve Selected</button>
        <button data-batch-action="reject" data-dry-run="true" class="danger">Preview Reject</button>
        <button data-batch-action="reject" class="danger">Reject Selected</button>
      </div>
    </section>
    <main class="stack" id="review-items">{items_html}</main>
    <div class="toast" id="toast" role="status" aria-live="polite"></div>
    """
    return _html_shell("Review Inbox", body, script=_REVIEW_UI_SCRIPT)


def render_graph_ui(
    store: MemoryStore,
    *,
    scope: str | None = None,
    node_type: str | None = None,
    query: str = "",
    limit: int = 50,
    evidence_limit: int = 3,
) -> str:
    graph = store.graph_browser(
        scope=scope or None,
        node_type=node_type or None,
        query=query,
        limit=limit,
        evidence_limit=evidence_limit,
    )
    nodes_html = "".join(_graph_node_html(node) for node in graph.get("nodes", []))
    edges_html = "".join(_graph_edge_html(edge) for edge in graph.get("edges", []))
    if not nodes_html:
        nodes_html = "<p class=\"empty\">No graph nodes found.</p>"
    if not edges_html:
        edges_html = "<p class=\"empty\">No graph edges found.</p>"
    counts = graph.get("counts", {})
    body = f"""
    <section class="toolbar">
      <form method="get" action="/ui/graph" class="filters">
        <label>Scope <input name="scope" value="{_h(scope or "")}" placeholder="all"></label>
        <label>Type <input name="node_type" value="{_h(node_type or "")}" placeholder="all"></label>
        <label>Query <input name="query" value="{_h(query)}"></label>
        <label>Limit <input name="limit" type="number" min="1" max="200" value="{_h(limit)}"></label>
        <button type="submit">Apply</button>
      </form>
      <div class="summary">
        <span class="pill"><strong>nodes</strong> {_h(counts.get("nodes", 0))}</span>
        <span class="pill"><strong>edges</strong> {_h(counts.get("edges", 0))}</span>
      </div>
    </section>
    <main class="columns">
      <section>
        <h2>Nodes</h2>
        <div class="stack">{nodes_html}</div>
      </section>
      <section>
        <h2>Edges</h2>
        <div class="stack">{edges_html}</div>
      </section>
    </main>
    """
    return _html_shell("Graph Browser", body)


def render_conflicts_ui(
    store: MemoryStore,
    *,
    scope: str | None = None,
    kind: str | None = None,
    status: str = "open",
    limit: int = 50,
) -> str:
    safe_limit = max(1, min(int(limit or 50), 200))
    detection = store.detect_memory_conflicts(
        scope=scope or None,
        kind=kind or None,
        limit=safe_limit,
    )
    status_filter = (status or "open").strip().lower()
    if status_filter not in {"open", "resolved", "all"}:
        status_filter = "open"
    conflicts = store.list_memory_conflicts(
        status=None if status_filter == "all" else status_filter,
        scope=scope or None,
        limit=safe_limit,
    )
    body = f"""
    <section class="toolbar">
      <form method="get" action="/ui/conflicts" class="filters">
        <label>Scope <input name="scope" value="{_h(scope or "")}" placeholder="all"></label>
        <label>Kind <input name="kind" value="{_h(kind or "")}" placeholder="all"></label>
        <label>Status {_select("status", ["open", "resolved", "all"], status_filter)}</label>
        <label>Limit <input name="limit" type="number" min="1" max="200" value="{_h(safe_limit)}"></label>
        <button type="submit">Apply</button>
      </form>
      <div class="summary">
        <span class="pill"><strong>detected</strong> {_h(detection.get("count", 0))}</span>
        <span class="pill"><strong>records</strong> {_h(len(conflicts))}</span>
      </div>
    </section>
    <section class="bulkbar">
      <div class="actions">
        <button data-conflict-record data-scope="{_h(scope or "")}" data-kind="{_h(kind or "")}" data-limit="{_h(safe_limit)}">Record Detected</button>
      </div>
    </section>
    <main class="columns">
      <section>
        <h2>Detected</h2>
        {_conflict_detection_table(detection.get("detections", []))}
      </section>
      <section>
        <h2>Recorded</h2>
        {_conflict_record_table(conflicts)}
      </section>
    </main>
    <div class="toast" id="toast" role="status" aria-live="polite"></div>
    """
    return _html_shell("Conflicts", body, script=_CONFLICT_UI_SCRIPT)


def _review_item_html(item: dict[str, Any]) -> str:
    candidate = item.get("candidate", {})
    source_event = item.get("source_event", {})
    review = item.get("review", {})
    candidate_id = str(candidate.get("candidate_id", ""))
    status = str(candidate.get("status", ""))
    risk_flags = review.get("risk_flags", [])
    conflict_warnings = review.get("conflict_warnings", [])
    selection = ""
    actions = ""
    if status in {"pending", "quarantined"}:
        selection = (
            f"<label class=\"checkline\"><input type=\"checkbox\" "
            f"class=\"candidate-check\" value=\"{_h(candidate_id)}\"> Select</label>"
        )
        actions = f"""
        <div class="actions">
          <button data-action="approve" data-candidate-id="{_h(candidate_id)}">Approve</button>
          <button data-action="reject" data-candidate-id="{_h(candidate_id)}" class="danger">Reject</button>
        </div>
        """
    active_memories = _active_memory_html(item.get("active_memories", []))
    graph_preview = item.get("graph_preview", {})
    return f"""
    <article class="card" data-candidate="{_h(candidate_id)}">
      <header>
        <div>
          <h2>{_h(candidate.get("kind", "memory"))}</h2>
          <p class="muted"><code>{_h(candidate_id)}</code></p>
          {selection}
        </div>
        <div class="meta">
          <span>{_h(status)}</span>
          <span>{_h(candidate.get("scope", ""))}</span>
          <span>{_h(candidate.get("confidence", ""))}</span>
          <span>{_h(candidate.get("source_trust", ""))}</span>
        </div>
      </header>
      <p class="text">{_h(candidate.get("proposed_text", ""))}</p>
      <dl class="grid">
        <div><dt>Recommended</dt><dd>{_h(review.get("recommended_action", ""))}</dd></div>
        <div><dt>Source</dt><dd>{_h(source_event.get("source_type", ""))} {_h(source_event.get("source_ref", ""))}</dd></div>
        <div><dt>Graph</dt><dd>{_h(graph_preview.get("node_count", 0))} nodes, {_h(graph_preview.get("edge_count", 0))} edges, {_h(graph_preview.get("fact_count", 0))} facts</dd></div>
      </dl>
      {_flag_list("Risk Flags", risk_flags)}
      {_conflict_warning_html(conflict_warnings)}
      <details>
        <summary>Source excerpt</summary>
        <p class="text">{_h(source_event.get("content_excerpt", ""))}</p>
      </details>
      {active_memories}
      {actions}
    </article>
    """


def _active_memory_html(memories: list[dict[str, Any]]) -> str:
    if not memories:
        return ""
    rows = []
    for memory in memories:
        memory_id = str(memory.get("memory_id", ""))
        text = str(memory.get("text", ""))
        rows.append(
            f"""
            <section class="memory-row" data-memory-id="{_h(memory_id)}">
              <div>
                <p class="muted"><code>{_h(memory_id)}</code></p>
                <p class="text">{_h(text)}</p>
              </div>
              <label>Correction
                <textarea data-correction-text="{_h(memory_id)}">{_h(text)}</textarea>
              </label>
              <div class="actions">
                <button data-lifecycle-action="correct" data-memory-id="{_h(memory_id)}" data-dry-run="true">Preview Correction</button>
                <button data-lifecycle-action="correct" data-memory-id="{_h(memory_id)}">Apply Correction</button>
              </div>
            </section>
            """
        )
    return f"<section><h3>Active Memories</h3><div class=\"memory-list\">{''.join(rows)}</div></section>"


def _graph_node_html(node: dict[str, Any]) -> str:
    label = str(node.get("label", ""))
    scope = str(node.get("scope", ""))
    node_type = str(node.get("node_type", ""))
    type_href = _ui_href("/ui/graph", scope=scope, node_type=node_type)
    focus_href = _ui_href("/ui/graph", scope=scope, query=label)
    return f"""
    <article class="card">
      <header>
        <div>
          <h2>{_h(label)}</h2>
          <p class="muted"><code>{_h(node.get("graph_node_id", ""))}</code></p>
        </div>
        <div class="meta">
          <span>{_h(node_type)}</span>
          <span>{_h(scope)}</span>
          <span>{_h(node.get("confidence", ""))}</span>
        </div>
      </header>
      <div class="linkbar">
        <a href="{_h(type_href)}">Type</a>
        <a href="{_h(focus_href)}">Focus</a>
      </div>
      <p class="text">{_h(node.get("summary", "") or node.get("blob", ""))}</p>
      {_graph_source_preview_html(node.get("source_previews", []))}
    </article>
    """


def _graph_edge_html(edge: dict[str, Any]) -> str:
    source_label = str(edge.get("source_label", ""))
    target_label = str(edge.get("target_label", ""))
    source_href = _ui_href("/ui/graph", query=source_label)
    target_href = _ui_href("/ui/graph", query=target_label)
    return f"""
    <article class="card">
      <header>
        <div>
          <h2>{_h(source_label)} -> {_h(target_label)}</h2>
          <p class="muted"><code>{_h(edge.get("graph_edge_id", ""))}</code></p>
        </div>
        <div class="meta">
          <span>{_h(edge.get("edge_type", ""))}</span>
          <span>weight {_h(edge.get("weight", ""))}</span>
        </div>
      </header>
      <div class="linkbar">
        <a href="{_h(source_href)}">Source</a>
        <a href="{_h(target_href)}">Target</a>
      </div>
      <p class="text">{_h(edge.get("label", ""))}</p>
      {_graph_source_preview_html(edge.get("source_previews", []))}
    </article>
    """


def _graph_source_preview_html(previews: list[dict[str, Any]]) -> str:
    if not previews:
        return ""
    items = []
    for preview in previews:
        source = " ".join(
            part
            for part in [
                str(preview.get("source_type", "") or ""),
                str(preview.get("source_ref", "") or ""),
            ]
            if part
        )
        items.append(
            f"""
            <li>
              <p class="text">{_h(preview.get("quote", ""))}</p>
              <p class="muted">
                <code>{_h(preview.get("memory_id", ""))}</code>
                <code>{_h(preview.get("event_id", ""))}</code>
                {_h(source)}
              </p>
            </li>
            """
        )
    return _list_block("Sources", "".join(items))


def _flag_list(title: str, flags: list[dict[str, Any]]) -> str:
    if not flags:
        return ""
    items = "".join(
        f"<li><strong>{_h(flag.get('flag', ''))}</strong> <span>{_h(flag.get('severity', ''))}</span> {_h(flag.get('detail', ''))}</li>"
        for flag in flags
    )
    return _list_block(title, items)


def _conflict_warning_html(warnings: list[dict[str, Any]]) -> str:
    if not warnings:
        return ""
    rows = "".join(
        f"""
        <tr>
          <td><code>{_h(warning.get("memory_id", ""))}</code></td>
          <td>{_h(warning.get("memory_text_excerpt", ""))}</td>
          <td>{_h(", ".join(str(token) for token in warning.get("overlap_tokens", [])))}</td>
        </tr>
        """
        for warning in warnings
    )
    return f"""
    <section class="table-wrap">
      <h3>Possible Conflicts</h3>
      <table>
        <thead><tr><th>Memory</th><th>Active text</th><th>Overlap</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </section>
    """


def _conflict_detection_table(detections: list[dict[str, Any]]) -> str:
    if not detections:
        return "<p class=\"empty\">No likely conflicts found.</p>"
    rows = "".join(
        f"""
        <tr>
          <td><code>{_h(item.get("memory_id", ""))}</code><br><code>{_h(item.get("other_memory_id", ""))}</code></td>
          <td>{_h(item.get("memory_text_excerpt", ""))}<hr>{_h(item.get("other_memory_text_excerpt", ""))}</td>
          <td>{_h(", ".join(str(token) for token in item.get("overlap_tokens", [])))}</td>
        </tr>
        """
        for item in detections
    )
    return f"""
    <section class="table-wrap">
      <table>
        <thead><tr><th>Memories</th><th>Texts</th><th>Overlap</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </section>
    """


def _conflict_record_table(conflicts: list[dict[str, Any]]) -> str:
    if not conflicts:
        return "<p class=\"empty\">No conflict records found.</p>"
    rows = "".join(
        f"""
        <tr>
          <td><code>{_h(item.get("conflict_id", ""))}</code><br>{_h(item.get("status", ""))}</td>
          <td>{_h(item.get("relation", ""))}<br><code>{_h(item.get("winner_memory_id", ""))}</code></td>
          <td>{_h(item.get("memory_text", ""))}<hr>{_h(item.get("other_memory_text", ""))}</td>
        </tr>
        """
        for item in conflicts
    )
    return f"""
    <section class="table-wrap">
      <table>
        <thead><tr><th>Conflict</th><th>Relation</th><th>Texts</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </section>
    """


def _list_block(title: str, items_html: str) -> str:
    if not items_html:
        return ""
    return f"<section><h3>{_h(title)}</h3><ul>{items_html}</ul></section>"


def _select(name: str, options: list[str], selected: str) -> str:
    option_html = "".join(
        f"<option value=\"{_h(option)}\"{' selected' if option == selected else ''}>{_h(option)}</option>"
        for option in options
    )
    return f"<select name=\"{_h(name)}\">{option_html}</select>"


def _ui_href(path: str, **params: Any) -> str:
    clean_params = {
        key: str(value)
        for key, value in params.items()
        if value is not None and str(value).strip() and str(value) != "all"
    }
    query = urlencode(clean_params)
    return f"{path}?{query}" if query else path


def _html_shell(title: str, body: str, *, script: str = "") -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{_h(title)} - Agent Memory Kernel</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f7f4;
      --panel: #ffffff;
      --ink: #1f2933;
      --muted: #64707d;
      --line: #d9ded6;
      --accent: #0f766e;
      --danger: #b42318;
      --warn: #9a6700;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font: 14px/1.45 ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    nav {{
      display: flex;
      gap: 12px;
      align-items: center;
      padding: 14px 24px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
      position: sticky;
      top: 0;
      z-index: 1;
    }}
    nav strong {{ margin-right: auto; }}
    nav a {{ color: var(--ink); text-decoration: none; }}
    nav a:hover {{ color: var(--accent); }}
    a {{ color: var(--accent); }}
    .page {{ max-width: 1280px; margin: 0 auto; padding: 24px; }}
    .toolbar {{
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 16px;
      align-items: center;
      margin-bottom: 18px;
    }}
    .bulkbar {{
      display: flex;
      justify-content: flex-end;
      margin: -6px 0 18px;
    }}
    .filters {{ display: flex; flex-wrap: wrap; gap: 10px; align-items: end; }}
    label {{ display: grid; gap: 4px; color: var(--muted); font-size: 12px; }}
    .checkline {{
      display: inline-flex;
      grid-auto-flow: column;
      align-items: center;
      gap: 6px;
      margin-top: 8px;
      color: var(--ink);
    }}
    input, select, button, textarea {{
      min-height: 34px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      color: var(--ink);
      padding: 6px 9px;
      font: inherit;
    }}
    textarea {{ width: 100%; min-height: 96px; resize: vertical; }}
    button {{ cursor: pointer; background: var(--ink); color: #fff; border-color: var(--ink); }}
    button:hover {{ background: var(--accent); border-color: var(--accent); }}
    button.danger {{ background: var(--danger); border-color: var(--danger); }}
    .summary, .meta, .actions {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }}
    .linkbar {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0 0; }}
    .linkbar a {{
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 3px 8px;
      text-decoration: none;
      background: #fff;
    }}
    .pill, .meta span {{
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 4px 8px;
      background: #fff;
      color: var(--muted);
      white-space: nowrap;
    }}
    .stack {{ display: grid; gap: 14px; }}
    .columns {{ display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 18px; }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
    }}
    header {{ display: flex; justify-content: space-between; gap: 16px; align-items: start; }}
    h1 {{ margin: 0; font-size: 20px; }}
    h2 {{ margin: 0; font-size: 16px; line-height: 1.3; }}
    h3 {{ margin: 14px 0 8px; font-size: 13px; color: var(--muted); text-transform: uppercase; }}
    .muted {{ color: var(--muted); margin: 4px 0 0; }}
    .text {{ white-space: pre-wrap; overflow-wrap: anywhere; }}
    .grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; margin: 14px 0; }}
    dt {{ color: var(--muted); font-size: 12px; }}
    dd {{ margin: 2px 0 0; overflow-wrap: anywhere; }}
    ul {{ margin: 0; padding-left: 18px; }}
    li {{ margin: 4px 0; overflow-wrap: anywhere; }}
    .memory-list {{ display: grid; gap: 10px; }}
    .memory-row {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(260px, .8fr);
      gap: 12px;
      padding: 12px 0;
      border-top: 1px solid var(--line);
    }}
    .memory-row .actions {{ grid-column: 1 / -1; justify-content: flex-end; }}
    details {{ border-top: 1px solid var(--line); padding-top: 10px; margin-top: 12px; }}
    summary {{ cursor: pointer; color: var(--accent); }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ border-top: 1px solid var(--line); padding: 8px; text-align: left; vertical-align: top; }}
    code {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 12px; }}
    .empty {{ color: var(--muted); }}
    .toast {{ position: fixed; right: 18px; bottom: 18px; max-width: 420px; }}
    .toast:not(:empty) {{
      background: var(--ink);
      color: #fff;
      border-radius: 8px;
      padding: 10px 12px;
      box-shadow: 0 10px 30px rgba(0,0,0,.16);
    }}
    @media (max-width: 760px) {{
      .page {{ padding: 16px; }}
      .toolbar, .columns, .grid, .memory-row {{ grid-template-columns: 1fr; }}
      .bulkbar {{ justify-content: stretch; }}
      header {{ display: grid; }}
    }}
  </style>
</head>
<body>
  <nav>
    <strong>Agent Memory Kernel</strong>
    <a href="/ui/review">Review</a>
    <a href="/ui/graph">Graph</a>
    <a href="/ui/conflicts">Conflicts</a>
    <a href="/health">Health</a>
  </nav>
  <div class="page">
    <h1>{_h(title)}</h1>
    {body}
  </div>
  {script}
</body>
</html>"""


_REVIEW_UI_SCRIPT = """
<script>
const toast = document.getElementById("toast");
function showToast(message) {
  if (!toast) return;
  toast.textContent = message;
  window.setTimeout(() => { toast.textContent = ""; }, 4000);
}
async function postJson(path, payload) {
  const response = await fetch(path, {
    method: "POST",
    headers: {"content-type": "application/json"},
    body: JSON.stringify(payload)
  });
  const data = await response.json();
  if (!response.ok || data.error) throw new Error(data.detail || data.error || "request failed");
  return data;
}
document.addEventListener("click", async (event) => {
  const batchButton = event.target.closest("button[data-batch-action]");
  if (batchButton) {
    const action = batchButton.dataset.batchAction;
    const dryRun = batchButton.dataset.dryRun === "true";
    const candidateIds = Array.from(document.querySelectorAll(".candidate-check:checked"))
      .map((item) => item.value)
      .filter(Boolean);
    if (!candidateIds.length) {
      showToast("No candidates selected");
      return;
    }
    batchButton.disabled = true;
    try {
      const data = await postJson("/review/batch", {
        action,
        candidate_ids: candidateIds,
        actor: "browser-reviewer",
        reason: (dryRun ? "preview " : "") + action + " via browser review UI",
        dry_run: dryRun
      });
      showToast(JSON.stringify(data.summary || data));
      if (!dryRun) window.setTimeout(() => window.location.reload(), 450);
    } catch (error) {
      showToast(error.message);
      batchButton.disabled = false;
    }
    return;
  }

  const lifecycleButton = event.target.closest("button[data-lifecycle-action]");
  if (lifecycleButton) {
    const action = lifecycleButton.dataset.lifecycleAction;
    const memoryId = lifecycleButton.dataset.memoryId;
    const dryRun = lifecycleButton.dataset.dryRun === "true";
    const textInput = document.querySelector(`[data-correction-text="${memoryId}"]`);
    const text = textInput ? textInput.value.trim() : "";
    if (action === "correct" && !text) {
      showToast("Correction text is empty");
      return;
    }
    lifecycleButton.disabled = true;
    try {
      const operation = action === "correct"
        ? {action, memory_id: memoryId, text}
        : {action, memory_id: memoryId};
      const data = await postJson("/memory/lifecycle-batch", {
        operations: [operation],
        actor: "browser-reviewer",
        reason: (dryRun ? "preview " : "") + action + " via browser review UI",
        dry_run: dryRun
      });
      showToast(JSON.stringify(data.summary || data.results || data));
      if (!dryRun) window.setTimeout(() => window.location.reload(), 450);
    } catch (error) {
      showToast(error.message);
      lifecycleButton.disabled = false;
    }
    return;
  }

  const button = event.target.closest("button[data-action]");
  if (!button) return;
  const action = button.dataset.action;
  const candidateId = button.dataset.candidateId;
  const endpoint = action === "approve" ? "/review/approve" : "/review/reject";
  button.disabled = true;
  try {
    await postJson(endpoint, {
      candidate_id: candidateId,
      actor: "browser-reviewer",
      reason: action + " via browser review UI"
    });
    showToast(action + " completed");
    window.setTimeout(() => window.location.reload(), 350);
  } catch (error) {
    showToast(error.message);
    button.disabled = false;
  }
});
</script>
"""


_CONFLICT_UI_SCRIPT = """
<script>
const toast = document.getElementById("toast");
function showToast(message) {
  if (!toast) return;
  toast.textContent = message;
  window.setTimeout(() => { toast.textContent = ""; }, 4000);
}
async function postJson(path, payload) {
  const response = await fetch(path, {
    method: "POST",
    headers: {"content-type": "application/json"},
    body: JSON.stringify(payload)
  });
  const data = await response.json();
  if (!response.ok || data.error) throw new Error(data.detail || data.error || "request failed");
  return data;
}
document.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-conflict-record]");
  if (!button) return;
  button.disabled = true;
  try {
    const data = await postJson("/conflict/detect", {
      scope: button.dataset.scope || "",
      kind: button.dataset.kind || "",
      limit: Number(button.dataset.limit || 50),
      record: true,
      actor: "browser-reviewer",
      reason: "record via conflict UI"
    });
    showToast(JSON.stringify({recorded: data.count}));
    window.setTimeout(() => window.location.reload(), 450);
  } catch (error) {
    showToast(error.message);
    button.disabled = false;
  }
});
</script>
"""


def _h(value: Any) -> str:
    return escape(str(value if value is not None else ""), quote=True)


def run_server(db_path: str | Path, *, host: str = "127.0.0.1", port: int = 8765) -> None:
    """Run the blocking HTTP service."""
    handler = make_handler(db_path)
    server = ThreadingHTTPServer((host, int(port)), handler)
    print(f"agent-memory api listening on http://{host}:{int(port)}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def make_handler(db_path: str | Path) -> type[BaseHTTPRequestHandler]:
    db_path = str(db_path)

    class MemoryAPIHandler(BaseHTTPRequestHandler):
        server_version = "AgentMemoryKernel/0.1"

        def do_GET(self) -> None:  # noqa: N802 - stdlib handler name
            parsed = urlparse(self.path)
            path = _normalize_path(parsed.path)
            params = {key: values[-1] for key, values in parse_qs(parsed.query).items()}
            if path == "/health":
                self._send_json(200, {"status": "ok"})
                return
            if path in {"/", "/ui", "/ui/review"}:
                try:
                    store = MemoryStore(db_path)
                    store.init_db()
                    try:
                        body = render_review_ui(
                            store,
                            status=str(params.get("status", "open")),
                            scope=params.get("scope") or None,
                            limit=int(params.get("limit", 50) or 50),
                        )
                    finally:
                        store.close()
                    self._send_html(200, body)
                except Exception as exc:  # pragma: no cover - defensive HTTP boundary
                    self._send_json(400, {"error": "bad_request", "detail": str(exc)})
                return
            if path == "/ui/graph":
                try:
                    store = MemoryStore(db_path)
                    store.init_db()
                    try:
                        body = render_graph_ui(
                            store,
                            scope=params.get("scope") or None,
                            node_type=params.get("node_type") or None,
                            query=str(params.get("query", "")),
                            limit=int(params.get("limit", 50) or 50),
                            evidence_limit=int(params.get("evidence_limit", 3) or 3),
                        )
                    finally:
                        store.close()
                    self._send_html(200, body)
                except Exception as exc:  # pragma: no cover - defensive HTTP boundary
                    self._send_json(400, {"error": "bad_request", "detail": str(exc)})
                return
            if path == "/ui/conflicts":
                try:
                    store = MemoryStore(db_path)
                    store.init_db()
                    try:
                        body = render_conflicts_ui(
                            store,
                            scope=params.get("scope") or None,
                            kind=params.get("kind") or None,
                            status=str(params.get("status", "open")),
                            limit=int(params.get("limit", 50) or 50),
                        )
                    finally:
                        store.close()
                    self._send_html(200, body)
                except Exception as exc:  # pragma: no cover - defensive HTTP boundary
                    self._send_json(400, {"error": "bad_request", "detail": str(exc)})
                return
            self._send_json(404, {"error": "not_found"})

        def do_POST(self) -> None:  # noqa: N802 - stdlib handler name
            try:
                payload = self._read_json()
                store = MemoryStore(db_path)
                store.init_db()
                try:
                    result = handle_api_request(store, self.path, payload)
                finally:
                    store.close()
                self._send_json(200, result)
            except KeyError as exc:
                self._send_json(404, {"error": "not_found", "detail": str(exc)})
            except Exception as exc:  # pragma: no cover - defensive HTTP boundary
                self._send_json(400, {"error": "bad_request", "detail": str(exc)})

        def log_message(self, format: str, *args: Any) -> None:
            return

        def _read_json(self) -> dict[str, Any]:
            length = int(self.headers.get("content-length", "0") or "0")
            if length <= 0:
                return {}
            data = self.rfile.read(length)
            return json.loads(data.decode("utf-8"))

        def _send_json(self, status: int, payload: dict[str, Any]) -> None:
            body = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
            self.send_response(status)
            self.send_header("content-type", "application/json; charset=utf-8")
            self.send_header("content-length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_html(self, status: int, body: str) -> None:
            encoded = body.encode("utf-8")
            self.send_response(status)
            self.send_header("content-type", "text/html; charset=utf-8")
            self.send_header("content-length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

    return MemoryAPIHandler


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="agent-memory-api")
    parser.add_argument("--db", default=".memory/memory.db")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(argv)
    run_server(args.db, host=args.host, port=args.port)
    return 0


def _normalize_path(path: str) -> str:
    path = (path or "/").split("?", 1)[0].rstrip("/")
    return path or "/"


if __name__ == "__main__":
    raise SystemExit(main())
