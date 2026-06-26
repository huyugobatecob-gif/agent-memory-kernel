"""SQLite-backed memory store."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .extractors.rules import RuleBasedExtractor
from .policy import admission_policy, normalize_confidence, normalize_scope


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:16]}"


class MemoryStore:
    """Local-first auditable memory store.

    Events are append-only. Active memories are promoted from candidates through
    review or explicit trusted auto-approval.
    """

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path).expanduser()
        if self.db_path.parent:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")

    def close(self) -> None:
        self.conn.close()

    def init_db(self) -> None:
        schema_path = Path(__file__).with_name("schema.sql")
        self.conn.executescript(schema_path.read_text(encoding="utf-8"))
        self._ensure_column(
            "candidate_memories",
            "extraction_json",
            "TEXT NOT NULL DEFAULT '{}'",
        )
        self._audit("init", "database", str(self.db_path), details={"version": "0.1.0"})
        self.conn.commit()

    def remember(
        self,
        text: str,
        *,
        scope: str = "professional",
        actor: str = "user",
        source_type: str = "manual",
        source_ref: str = "",
        sensitivity: str = "internal",
        auto_approve: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Append an event and create candidate memories from it."""
        scope = normalize_scope(scope)
        text = (text or "").strip()
        if not text:
            raise ValueError("text must not be empty")

        ts = now_iso()
        event_id = new_id("evt")
        self.conn.execute(
            """
            INSERT INTO events
              (event_id, created_at, actor, scope, source_type, source_ref, content, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                ts,
                actor,
                scope,
                source_type,
                source_ref,
                text,
                json.dumps(metadata or {}, sort_keys=True),
            ),
        )
        self._audit("record", "event", event_id, actor=actor, details={"scope": scope})

        extractor = RuleBasedExtractor()
        candidates: list[dict[str, Any]] = []
        for extracted in extractor.extract(text, scope=scope):
            policy = admission_policy(
                extracted.text,
                source_type=source_type,
                sensitivity=sensitivity,
                auto_approve=auto_approve,
            )
            candidate_id = new_id("cand")
            confidence = normalize_confidence(extracted.confidence)
            self.conn.execute(
                """
                INSERT INTO candidate_memories
                  (candidate_id, event_id, created_at, proposed_text, kind, scope,
                   confidence, sensitivity, source_trust, status, reason, extraction_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    candidate_id,
                    event_id,
                    ts,
                    extracted.text,
                    extracted.kind,
                    scope,
                    confidence,
                    policy.sensitivity,
                    policy.source_trust,
                    policy.status,
                    policy.reason,
                    json.dumps(
                        {
                            "nodes": extracted.nodes,
                            "edges": extracted.edges,
                        },
                        sort_keys=True,
                    ),
                ),
            )
            self._audit(
                "candidate_created",
                "candidate",
                candidate_id,
                actor=actor,
                details={
                    "status": policy.status,
                    "reason": policy.reason,
                    "source_trust": policy.source_trust,
                },
            )
            if policy.status == "approved":
                memory_id = self._activate_candidate(candidate_id, actor=actor)
            else:
                memory_id = None
            candidates.append(
                {
                    "candidate_id": candidate_id,
                    "status": policy.status,
                    "reason": policy.reason,
                    "memory_id": memory_id,
                }
            )

        self.conn.commit()
        return {"event_id": event_id, "candidates": candidates}

    def list_candidates(self, status: str = "pending") -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT candidate_id, event_id, created_at, proposed_text, kind, scope,
                   confidence, sensitivity, source_trust, status, reason
            FROM candidate_memories
            WHERE (? = 'all' OR status = ?)
            ORDER BY created_at ASC
            """,
            (status, status),
        ).fetchall()
        return [dict(row) for row in rows]

    def approve_candidate(self, candidate_id: str, *, actor: str = "user", reason: str = "") -> str:
        memory_id = self._activate_candidate(candidate_id, actor=actor)
        self.conn.execute(
            """
            INSERT INTO review_actions
              (review_id, created_at, candidate_id, action, actor, reason)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (new_id("rev"), now_iso(), candidate_id, "approve", actor, reason),
        )
        self.conn.commit()
        return memory_id

    def reject_candidate(self, candidate_id: str, *, actor: str = "user", reason: str = "") -> None:
        row = self._candidate(candidate_id)
        if row is None:
            raise KeyError(f"candidate not found: {candidate_id}")
        existing = self.conn.execute(
            "SELECT memory_id FROM memories WHERE candidate_id = ? AND status = 'active'",
            (candidate_id,),
        ).fetchone()
        if existing:
            raise ValueError("active memories must be deleted instead of rejecting their candidate")
        self.conn.execute(
            "UPDATE candidate_memories SET status = ?, reason = ? WHERE candidate_id = ?",
            ("rejected", reason or "rejected by reviewer", candidate_id),
        )
        self.conn.execute(
            """
            INSERT INTO review_actions
              (review_id, created_at, candidate_id, action, actor, reason)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (new_id("rev"), now_iso(), candidate_id, "reject", actor, reason),
        )
        self._audit("reject", "candidate", candidate_id, actor=actor, details={"reason": reason})
        self.conn.commit()

    def search(self, query: str, *, scope: str | None = None, limit: int = 5) -> list[dict[str, Any]]:
        query = (query or "").strip()
        if not query:
            return []
        scope = normalize_scope(scope) if scope else None

        try:
            rows = self.conn.execute(
                """
                SELECT m.memory_id, m.text, m.kind, m.scope, m.confidence,
                       m.sensitivity, m.source_trust, m.status, m.updated_at,
                       e.event_id, e.source_type, e.source_ref
                FROM memories_fts f
                JOIN memories m ON m.rowid = f.rowid
                LEFT JOIN sources s ON s.memory_id = m.memory_id
                LEFT JOIN events e ON e.event_id = s.event_id
                WHERE memories_fts MATCH ?
                  AND m.status = 'active'
                  AND (? IS NULL OR m.scope = ?)
                ORDER BY rank
                LIMIT ?
                """,
                (query, scope, scope, limit),
            ).fetchall()
        except sqlite3.Error:
            like = f"%{query}%"
            rows = self.conn.execute(
                """
                SELECT m.memory_id, m.text, m.kind, m.scope, m.confidence,
                       m.sensitivity, m.source_trust, m.status, m.updated_at,
                       e.event_id, e.source_type, e.source_ref
                FROM memories m
                LEFT JOIN sources s ON s.memory_id = m.memory_id
                LEFT JOIN events e ON e.event_id = s.event_id
                WHERE m.status = 'active'
                  AND m.text LIKE ?
                  AND (? IS NULL OR m.scope = ?)
                ORDER BY m.updated_at DESC
                LIMIT ?
                """,
                (like, scope, scope, limit),
            ).fetchall()

        return [dict(row) for row in rows]

    def context_pack(self, query: str, *, scope: str | None = None, limit: int = 5) -> str:
        results = self.search(query, scope=scope, limit=limit)
        if not results:
            return "## Agent Memory Context\nNo active memories matched this request."

        lines = ["## Agent Memory Context", "", "Selected memories:"]
        for item in results:
            source = item.get("source_ref") or item.get("event_id") or "unknown source"
            lines.append(
                "- "
                f"[{item['scope']}:{item['kind']}:{item['confidence']}] "
                f"{item['text']} "
                f"(source={source}; trust={item['source_trust']}; "
                f"why_selected=query match; why_trusted={self._trust_explanation(item)})"
            )
        return "\n".join(lines)

    def correct_memory(self, memory_id: str, text: str, *, actor: str = "user") -> None:
        text = (text or "").strip()
        if not text:
            raise ValueError("text must not be empty")
        row = self.conn.execute(
            "SELECT memory_id FROM memories WHERE memory_id = ?", (memory_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"memory not found: {memory_id}")
        self.conn.execute(
            "UPDATE memories SET text = ?, updated_at = ? WHERE memory_id = ?",
            (text, now_iso(), memory_id),
        )
        self._audit("correct", "memory", memory_id, actor=actor)
        self.conn.commit()

    def delete_memory(self, memory_id: str, *, actor: str = "user", reason: str = "") -> None:
        row = self.conn.execute(
            "SELECT memory_id FROM memories WHERE memory_id = ?", (memory_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"memory not found: {memory_id}")
        self.conn.execute(
            "UPDATE memories SET status = 'deleted', updated_at = ? WHERE memory_id = ?",
            (now_iso(), memory_id),
        )
        self._audit("delete", "memory", memory_id, actor=actor, details={"reason": reason})
        self.conn.commit()

    def export_markdown(self, out_dir: str | Path) -> None:
        out_path = Path(out_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        rows = self.conn.execute(
            """
            SELECT memory_id, text, kind, scope, confidence, source_trust, updated_at
            FROM memories
            WHERE status = 'active'
            ORDER BY scope, updated_at DESC
            """
        ).fetchall()

        by_scope: dict[str, list[sqlite3.Row]] = {}
        for row in rows:
            by_scope.setdefault(row["scope"], []).append(row)

        for scope in ["personal", "professional", "project", "agent", "session"]:
            items = by_scope.get(scope, [])
            lines = [
                f"# {scope.title()} Memory",
                "",
                "Exported from Agent Memory Kernel.",
                "",
            ]
            for item in items:
                lines.append(
                    f"- `{item['kind']}` `{item['confidence']}` `{item['source_trust']}` "
                    f"{item['text']} <!-- {item['memory_id']} -->"
                )
            (out_path / f"{scope}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

        review_items = [
            item
            for item in self.list_candidates("all")
            if item["status"] in {"pending", "quarantined"}
        ]
        pending_lines = ["# Pending Memory Review", ""]
        for item in review_items:
            pending_lines.append(
                f"- `{item['candidate_id']}` `{item['status']}` `{item['scope']}` `{item['kind']}` "
                f"{item['proposed_text']}"
            )
        (out_path / "pending-review.md").write_text(
            "\n".join(pending_lines) + "\n", encoding="utf-8"
        )

    def _activate_candidate(self, candidate_id: str, *, actor: str = "user") -> str:
        existing = self.conn.execute(
            "SELECT memory_id FROM memories WHERE candidate_id = ?", (candidate_id,)
        ).fetchone()
        if existing:
            return str(existing["memory_id"])

        candidate = self._candidate(candidate_id)
        if candidate is None:
            raise KeyError(f"candidate not found: {candidate_id}")
        if candidate["status"] == "quarantined":
            raise ValueError("quarantined candidates cannot be approved without correction")
        if candidate["status"] == "rejected":
            raise ValueError("rejected candidates cannot be approved without correction")

        ts = now_iso()
        memory_id = new_id("mem")
        self.conn.execute(
            """
            INSERT INTO memories
              (memory_id, candidate_id, created_at, updated_at, text, kind, scope,
               confidence, sensitivity, source_trust, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
            """,
            (
                memory_id,
                candidate_id,
                ts,
                ts,
                candidate["proposed_text"],
                candidate["kind"],
                candidate["scope"],
                candidate["confidence"],
                candidate["sensitivity"],
                candidate["source_trust"],
            ),
        )
        self.conn.execute(
            "UPDATE candidate_memories SET status = 'approved' WHERE candidate_id = ?",
            (candidate_id,),
        )

        event = self.conn.execute(
            "SELECT event_id, source_type, source_ref FROM events WHERE event_id = ?",
            (candidate["event_id"],),
        ).fetchone()
        if event:
            self.conn.execute(
                """
                INSERT INTO sources (source_id, memory_id, event_id, source_type, source_ref)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    new_id("src"),
                    memory_id,
                    event["event_id"],
                    event["source_type"],
                    event["source_ref"],
                ),
            )

        self._create_graph_nodes(memory_id, candidate)
        self._audit("approve", "candidate", candidate_id, actor=actor, details={"memory_id": memory_id})
        return memory_id

    def _create_graph_nodes(self, memory_id: str, candidate: sqlite3.Row) -> None:
        try:
            extraction = json.loads(candidate["extraction_json"] or "{}")
        except json.JSONDecodeError:
            extraction = {}

        anchor_node_id = new_id("node")
        self.conn.execute(
            """
            INSERT INTO nodes (node_id, memory_id, node_type, label, scope)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                anchor_node_id,
                memory_id,
                "memory",
                candidate["kind"],
                candidate["scope"],
            ),
        )

        for item in extraction.get("nodes", []):
            label = str(item.get("label", "")).strip()
            if not label:
                continue
            node_id = new_id("node")
            self.conn.execute(
                """
                INSERT INTO nodes (node_id, memory_id, node_type, label, scope)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    node_id,
                    memory_id,
                    str(item.get("type", "memory")).strip() or "memory",
                    label,
                    candidate["scope"],
                ),
            )
            self.conn.execute(
                """
                INSERT INTO edges (edge_id, source_node_id, target_node_id, edge_type, memory_id)
                VALUES (?, ?, ?, ?, ?)
                """,
                (new_id("edge"), anchor_node_id, node_id, "relates_to", memory_id),
            )

    def _candidate(self, candidate_id: str) -> sqlite3.Row | None:
        return self.conn.execute(
            "SELECT * FROM candidate_memories WHERE candidate_id = ?", (candidate_id,)
        ).fetchone()

    def _audit(
        self,
        action: str,
        target_type: str,
        target_id: str,
        *,
        actor: str = "system",
        details: dict[str, Any] | None = None,
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO audit_log
              (audit_id, created_at, action, target_type, target_id, actor, details_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                new_id("aud"),
                now_iso(),
                action,
                target_type,
                target_id,
                actor,
                json.dumps(details or {}, sort_keys=True),
            ),
        )

    def _ensure_column(self, table: str, column: str, declaration: str) -> None:
        columns = {
            row["name"]
            for row in self.conn.execute(f"PRAGMA table_info({table})").fetchall()
        }
        if column not in columns:
            self.conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {declaration}")

    @staticmethod
    def _trust_explanation(item: dict[str, Any]) -> str:
        trust = item.get("source_trust")
        confidence = item.get("confidence")
        if trust in {"trusted", "user", "system"}:
            return f"{trust} source with {confidence} confidence"
        return f"{trust} source; verify before high-stakes use"
