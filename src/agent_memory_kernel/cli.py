"""Command line interface."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .server import run_server
from .slice import assert_vertical_slice, run_vertical_slice, seed_vertical_slice
from .store import MemoryStore


DEFAULT_DB = ".memory/memory.db"


def add_common_db(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--db", default=DEFAULT_DB, help=f"SQLite database path (default: {DEFAULT_DB})")


def print_json(data: object) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True))


def parse_csv(value: str) -> list[str] | None:
    items = [item.strip() for item in (value or "").split(",") if item.strip()]
    return items or None


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


def cmd_review_list(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(store.list_candidates(args.status))
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


def cmd_search(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print_json(store.search(args.query, scope=args.scope, limit=args.limit))
    store.close()
    return 0


def cmd_context_pack(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    print(store.context_pack(args.query, scope=args.scope, limit=args.limit))
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
    print_json(store.export_profile(scope=args.scope, project=args.project))
    store.close()
    return 0


def cmd_import_profile(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    payload = json.loads(Path(args.path).read_text(encoding="utf-8"))
    print_json(store.import_profile(payload))
    store.close()
    return 0


def cmd_correct(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    store.correct_memory(args.memory_id, args.text, actor=args.actor)
    store.close()
    print_json({"memory_id": args.memory_id, "status": "corrected"})
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


def cmd_worker(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    result = store.process_keeper_jobs(limit=args.limit, actor=args.actor)
    store.close()
    print_json(result)
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    run_server(args.db, host=args.host, port=args.port)
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    store = MemoryStore(args.db)
    store.init_db()
    store.export_markdown(args.out)
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

    p = sub.add_parser("review", help="Review candidate memories")
    add_common_db(p)
    review_sub = p.add_subparsers(dest="review_command", required=True)

    rp = review_sub.add_parser("list", help="List candidate memories")
    rp.add_argument("--status", default="pending", choices=["pending", "approved", "rejected", "quarantined", "all"])
    rp.set_defaults(func=cmd_review_list)

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

    p = sub.add_parser("search", help="Search active memories")
    add_common_db(p)
    p.add_argument("query")
    p.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    p.add_argument("--limit", type=int, default=5)
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("context-pack", help="Build a cited context pack for an agent")
    add_common_db(p)
    p.add_argument("query")
    p.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    p.add_argument("--limit", type=int, default=5)
    p.set_defaults(func=cmd_context_pack)

    p = sub.add_parser("build-context", help="Build a full agent context with memory tree supplement")
    add_common_db(p)
    p.add_argument("query")
    p.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    p.add_argument("--thread-id", default="default")
    p.add_argument("--limit", type=int, default=8)
    p.add_argument("--recent-messages", type=int, default=6)
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
    p.set_defaults(func=cmd_before_model_call)

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

    p = sub.add_parser("tree-pack", help="Build a branch-oriented memory tree pack for an agent")
    add_common_db(p)
    p.add_argument("query")
    p.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    p.add_argument("--limit", type=int, default=8)
    p.add_argument("--depth", type=int, default=1, help="Graph neighbor depth, 0-3")
    p.add_argument("--raw-chars", type=int, default=1600, help="Max raw event excerpt characters")
    p.add_argument("--no-raw", action="store_true", help="Omit raw provenance excerpts")
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
            "knowledge_consistency",
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

    gp = graph_sub.add_parser("tree", help="Build a Memory Tree Pack from graph nodes")
    gp.add_argument("query")
    gp.add_argument("--scope", choices=["personal", "professional", "project", "agent", "session"])
    gp.add_argument("--limit", type=int, default=8)
    gp.add_argument("--depth", type=int, default=1)
    gp.add_argument("--raw-chars", type=int, default=1600)
    gp.add_argument("--no-raw", action="store_true")
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
    p.set_defaults(func=cmd_export_profile)

    p = sub.add_parser("import-profile", help="Import project profile JSON")
    add_common_db(p)
    p.add_argument("path")
    p.set_defaults(func=cmd_import_profile)

    p = sub.add_parser("correct", help="Correct active memory text")
    add_common_db(p)
    p.add_argument("memory_id")
    p.add_argument("text")
    p.add_argument("--actor", default="user")
    p.set_defaults(func=cmd_correct)

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

    p = sub.add_parser("worker", help="Process queued Keeper jobs")
    add_common_db(p)
    p.add_argument("--once", action="store_true", help="Process one batch and exit")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--actor", default="worker")
    p.set_defaults(func=cmd_worker)

    p = sub.add_parser("serve", help="Run the stdlib HTTP API service")
    add_common_db(p)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8765)
    p.set_defaults(func=cmd_serve)

    p = sub.add_parser("export", help="Export active memories to a markdown vault")
    add_common_db(p)
    p.add_argument("--out", default="memory-vault")
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
