from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agent_memory_kernel import MemoryStore
from agent_memory_kernel.extractors.base import ExtractedMemory
from agent_memory_kernel.server import render_conflicts_ui, render_graph_ui, render_review_ui


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
            self.assertIn('class="candidate-check"', html)
            self.assertIn('data-batch-action="approve"', html)
            self.assertIn("/review/approve", html)
            self.assertIn("/review/batch", html)

            approved_html = render_review_ui(
                store,
                status="approved",
                scope="professional",
                limit=10,
            )
            self.assertIn(active_memory_id, approved_html)
            self.assertIn('data-lifecycle-action="correct"', approved_html)
            self.assertIn("/memory/lifecycle-batch", approved_html)
            store.close()

    def test_graph_ui_renders_nodes_edges_and_source_previews(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "memory.db", extractor=UIExtractor())
            store.init_db()
            memory_id = store.remember(
                "Decision: ui-site uses summary-first loop.",
                scope="professional",
                actor="seo-agent",
                source_type="manual",
                auto_approve=True,
            )["candidates"][0]["memory_id"]

            html = render_graph_ui(store, scope="professional", query="ui-site", limit=10)

            self.assertIn("Graph Browser", html)
            self.assertIn("ui-site", html)
            self.assertIn("summary-first loop", html)
            self.assertIn("Sources", html)
            self.assertIn(memory_id, html)
            self.assertIn("/ui/graph?scope=professional&amp;node_type=project", html)
            self.assertIn("/ui/graph?scope=professional&amp;query=ui-site", html)
            store.close()

    def test_conflicts_ui_renders_detection_and_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "memory.db", extractor=UIExtractor())
            store.init_db()
            first = store.remember(
                "Decision: conflict-site owner is Alice.",
                scope="professional",
                actor="seo-agent",
                source_type="manual",
                auto_approve=True,
            )["candidates"][0]["memory_id"]
            second = store.remember(
                "Decision: conflict-site owner is Bob.",
                scope="professional",
                actor="seo-agent",
                source_type="manual",
                auto_approve=True,
            )["candidates"][0]["memory_id"]

            html = render_conflicts_ui(store, scope="professional", kind="decision", limit=10)

            self.assertIn("Conflicts", html)
            self.assertIn(first, html)
            self.assertIn(second, html)
            self.assertIn('data-conflict-record', html)
            self.assertIn("/conflict/detect", html)
            store.record_memory_conflict(first, second, actor="reviewer")
            recorded_html = render_conflicts_ui(store, scope="professional", kind="decision", limit=10)
            self.assertIn("Recorded", recorded_html)
            self.assertIn("conflicts_with", recorded_html)
            store.close()


if __name__ == "__main__":
    unittest.main()
