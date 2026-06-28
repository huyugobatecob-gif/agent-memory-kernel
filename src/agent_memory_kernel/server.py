"""Small stdlib HTTP API for Agent Memory Kernel."""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

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
            if _normalize_path(self.path) == "/health":
                self._send_json(200, {"status": "ok"})
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
