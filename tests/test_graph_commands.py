from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from agent_memory_kernel import MemoryStore
from agent_memory_kernel.graph_commands import (
    GRAPH_COMMAND_VERSION,
    graph_commands_to_extraction,
    normalize_graph_commands,
)


class GraphCommandTests(unittest.TestCase):
    def test_normalizes_keeper_graph_commands(self) -> None:
        commands = normalize_graph_commands(
            [
                {
                    "command": "create_node",
                    "node_type": "project",
                    "label": "demo-site",
                    "summary": "SEO client project",
                    "evidence": "User mentioned demo-site.",
                },
                {
                    "command": "create_edge",
                    "source": {"type": "project", "label": "demo-site"},
                    "target": {"type": "tool", "label": "WordPress"},
                    "edge_type": "uses",
                },
            ],
            default_scope="professional",
        )
        extraction = graph_commands_to_extraction(commands)

        self.assertEqual(commands[0]["version"], GRAPH_COMMAND_VERSION)
        self.assertEqual(commands[0]["command_type"], "upsert_node")
        self.assertEqual(commands[1]["command_type"], "upsert_edge")
        self.assertEqual(extraction["version"], GRAPH_COMMAND_VERSION)
        self.assertIn({"type": "project", "label": "demo-site", "summary": "SEO client project"}, extraction["nodes"])
        self.assertIn({"source": "demo-site", "target": "WordPress", "type": "uses"}, extraction["edges"])

    def test_pending_graph_commands_are_reviewable_without_graph_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "memory.db")
            store.init_db()

            result = store.apply_graph_commands(
                [
                    {
                        "command": "upsert_node",
                        "node_type": "project",
                        "label": "demo-site",
                        "summary": "SEO project",
                    }
                ],
                scope="professional",
                actor="keeper",
                auto_approve=False,
            )

            self.assertEqual(result["version"], GRAPH_COMMAND_VERSION)
            self.assertEqual(result["candidates"][0]["status"], "pending")
            self.assertEqual(store.list_graph_nodes(scope="professional"), [])
            proposed = store.conn.execute(
                "SELECT status, command_type FROM graph_commands"
            ).fetchall()
            self.assertEqual([(row["status"], row["command_type"]) for row in proposed], [("proposed", "upsert_node")])
            store.close()

    def test_approved_graph_commands_apply_nodes_edges_and_evidence_idempotently(self) -> None:
        commands = [
            {
                "command": "upsert_edge",
                "source": {"type": "project", "label": "demo-site"},
                "target": {"type": "tool", "label": "WordPress"},
                "edge_type": "uses",
                "evidence": "User said demo-site uses WordPress.",
            }
        ]
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "memory.db")
            store.init_db()

            first = store.apply_graph_commands(
                commands,
                scope="professional",
                actor="keeper",
                source_type="system",
                auto_approve=True,
            )
            second = store.apply_graph_commands(
                commands,
                scope="professional",
                actor="keeper",
                source_type="system",
                auto_approve=True,
            )

            self.assertEqual(first["candidates"][0]["status"], "approved")
            self.assertTrue(first["candidates"][0]["memory_id"])
            self.assertTrue(second["candidates"][0]["memory_id"])

            project_nodes = store.list_graph_nodes(scope="professional", node_type="project")
            tool_nodes = store.list_graph_nodes(scope="professional", node_type="tool")
            edges = store.list_graph_edges(scope="professional")
            self.assertEqual([node["label"] for node in project_nodes].count("demo-site"), 1)
            self.assertEqual([node["label"] for node in tool_nodes].count("WordPress"), 1)
            direct_edges = [
                edge
                for edge in edges
                if edge["edge_type"] == "uses"
                and edge["source_type"] == "project"
                and edge["source_label"] == "demo-site"
                and edge["target_type"] == "tool"
                and edge["target_label"] == "WordPress"
            ]
            self.assertEqual(len(direct_edges), 1)

            node_evidence_count = store.conn.execute(
                """
                SELECT COUNT(*) AS count
                FROM node_evidence ne
                JOIN memory_graph_nodes gn ON gn.graph_node_id = ne.graph_node_id
                WHERE gn.label IN ('demo-site', 'WordPress')
                """
            ).fetchone()["count"]
            edge_evidence_count = store.conn.execute(
                """
                SELECT COUNT(*) AS count
                FROM edge_evidence ee
                JOIN memory_graph_edges ge ON ge.graph_edge_id = ee.graph_edge_id
                WHERE ge.edge_type = 'uses'
                """
            ).fetchone()["count"]
            self.assertGreaterEqual(node_evidence_count, 2)
            self.assertGreaterEqual(edge_evidence_count, 1)

            applied = store.conn.execute(
                "SELECT command_type, status, payload_json FROM graph_commands WHERE status = 'applied'"
            ).fetchall()
            self.assertTrue(any(row["command_type"] == "upsert_edge" for row in applied))
            self.assertTrue(any(json.loads(row["payload_json"]).get("source") == "graph_command" for row in applied))
            store.close()

    def test_mark_conflict_command_records_open_conflict_on_approval(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "memory.db")
            store.init_db()
            old = store.remember(
                "Decision: demo-site owner is Alice.",
                scope="professional",
                actor="user",
                source_type="manual",
                auto_approve=True,
            )["candidates"][0]["memory_id"]
            new = store.remember(
                "Decision: demo-site owner is Bob.",
                scope="professional",
                actor="user",
                source_type="manual",
                auto_approve=True,
            )["candidates"][0]["memory_id"]

            result = store.apply_graph_commands(
                [
                    {
                        "command": "mark_conflict",
                        "memory_id": old,
                        "other_memory_id": new,
                        "reason": "new owner contradicts old owner",
                    }
                ],
                scope="professional",
                actor="keeper",
                source_type="system",
                auto_approve=True,
            )
            conflicts = store.list_memory_conflicts(status="open", scope="professional")

            self.assertEqual(result["candidates"][0]["status"], "approved")
            self.assertTrue(any(item["memory_id"] == old and item["other_memory_id"] == new for item in conflicts))
            store.close()


if __name__ == "__main__":
    unittest.main()
