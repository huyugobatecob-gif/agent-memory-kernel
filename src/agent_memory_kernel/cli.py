"""Command line interface."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .store import MemoryStore


DEFAULT_DB = ".memory/memory.db"


def add_common_db(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--db", default=DEFAULT_DB, help=f"SQLite database path (default: {DEFAULT_DB})")


def print_json(data: object) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True))


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
