from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agent_memory_kernel import MemoryStore


class MemoryStoreTests(unittest.TestCase):
    def test_full_lifecycle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "memory.db")
            store.init_db()

            result = store.remember(
                "Rule: professional project memories must keep provenance.",
                scope="professional",
            )
            candidate_id = result["candidates"][0]["candidate_id"]

            self.assertEqual(result["candidates"][0]["status"], "pending")
            self.assertEqual(store.search("provenance"), [])

            memory_id = store.approve_candidate(candidate_id, reason="useful project rule")
            results = store.search("provenance")

            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["memory_id"], memory_id)
            self.assertEqual(results[0]["scope"], "professional")
            self.assertIn("provenance", store.context_pack("provenance"))

            store.close()

    def test_auto_approve_trusted_manual_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "memory.db")
            store.init_db()

            result = store.remember(
                "I prefer concise technical updates.",
                scope="personal",
                auto_approve=True,
            )

            self.assertEqual(result["candidates"][0]["status"], "approved")
            self.assertEqual(len(store.search("concise", scope="personal")), 1)
            store.close()

    def test_secret_like_content_is_quarantined(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "memory.db")
            store.init_db()

            result = store.remember(
                "password: super-secret-value",
                scope="professional",
                auto_approve=True,
            )
            candidate = result["candidates"][0]

            self.assertEqual(candidate["status"], "quarantined")
            self.assertEqual(store.search("super-secret-value"), [])
            with self.assertRaises(ValueError):
                store.approve_candidate(candidate["candidate_id"])
            store.close()

    def test_correct_delete_and_export(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "memory.db"
            export_dir = Path(tmp) / "vault"
            store = MemoryStore(db_path)
            store.init_db()

            result = store.remember(
                "Decision: use SQLite as the local memory store.",
                auto_approve=True,
            )
            memory_id = result["candidates"][0]["memory_id"]

            store.correct_memory(memory_id, "Decision: use SQLite for the local-first memory store.")
            self.assertIn("local-first", store.context_pack("SQLite"))

            store.export_markdown(export_dir)
            self.assertTrue((export_dir / "professional.md").exists())
            self.assertTrue((export_dir / "personal.md").exists())
            self.assertIn("local-first", (export_dir / "professional.md").read_text())

            store.delete_memory(memory_id, reason="test cleanup")
            self.assertEqual(store.search("SQLite"), [])
            store.close()

    def test_approved_memory_creates_graph_nodes_and_edges(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "memory.db")
            store.init_db()

            result = store.remember(
                "Rule: project demo-site should track failed SEO attempts.",
                auto_approve=True,
            )
            memory_id = result["candidates"][0]["memory_id"]

            node_count = store.conn.execute(
                "SELECT COUNT(*) AS count FROM nodes WHERE memory_id = ?",
                (memory_id,),
            ).fetchone()["count"]
            edge_count = store.conn.execute(
                "SELECT COUNT(*) AS count FROM edges WHERE memory_id = ?",
                (memory_id,),
            ).fetchone()["count"]

            self.assertGreaterEqual(node_count, 2)
            self.assertGreaterEqual(edge_count, 1)
            store.close()


if __name__ == "__main__":
    unittest.main()
