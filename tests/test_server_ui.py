from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agent_memory_kernel import MemoryStore
from agent_memory_kernel.extractors.base import ExtractedMemory
from agent_memory_kernel.server import render_graph_ui, render_review_ui


class UIExtractor:
    def extract(self, text: str, *, scope: str = "professional") -> list[ExtractedMemory]:
        label = "conflict-site" if "conflict-site" in text else "ui-site"
        return [
            ExtractedMemory(
                text=text,
                kind="decision",
                scope=scope,
                confidence="high",
                nodes=[{"type": "project", "label": label}],
                edges=[
                    {
                        "source": label,
                        "target": "summary-first loop",
                        "type": "uses",
                        "label": "uses",
                    }
                ],
                metadata={"extractor": "ui-test"},
            )
        ]


class ServerUITests(unittest.TestCase):
    def test_review_ui_renders_conflict_warnings_and_actions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "memory.db", extractor=UIExtractor())
            store.init_db()
            active_memory_id = store.remember(
                "Decision: conflict-site owner is Alice.",
                scope="professional",
                actor="seo-agent",
                source_type="manual",
                auto_approve=True,
            )["candidates"][0]["memory_id"]
            pending_candidate_id = store.remember(
                "Decision: conflict-site owner is Bob.",
                scope="professional",
                actor="seo-agent",
                source_type="manual",
            )["candidates"][0]["candidate_id"]

            html = render_review_ui(store, status="open", scope="professional", limit=10)

            self.assertIn("Review Inbox", html)
            self.assertIn(pending_candidate_id, html)
            self.assertIn(active_memory_id, html)
            self.assertIn("Possible Conflicts", html)
            self.assertIn('data-action="approve"', html)
            self.assertIn("/review/approve", html)
            store.close()

    def test_graph_ui_renders_nodes_edges_and_source_previews(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "memory.db", extractor=UIExtractor())
            store.init_db()
            store.remember(
                "Decision: ui-site uses summary-first loop.",
                scope="professional",
                actor="seo-agent",
                source_type="manual",
                auto_approve=True,
            )

            html = render_graph_ui(store, scope="professional", query="ui-site", limit=10)

            self.assertIn("Graph Browser", html)
            self.assertIn("ui-site", html)
            self.assertIn("summary-first loop", html)
            self.assertIn("Sources", html)
            store.close()


if __name__ == "__main__":
    unittest.main()
