from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agent_memory_kernel.extractors.base import Extractor
from agent_memory_kernel.mcp_server import list_mcp_tools
from agent_memory_kernel.server import handle_api_request
from agent_memory_kernel.store import MemoryStore


class FailingExtractor(Extractor):
    def extract(self, text: str, *, scope: str = "professional"):
        raise RuntimeError("keeper model down")


class OperationalFailureTests(unittest.TestCase):
    def test_before_model_call_returns_no_memory_envelope_when_retrieval_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "memory.db")
            store.init_db()

            def boom(*args, **kwargs):
                raise RuntimeError("router unavailable")

            store.retrieve_tree = boom  # type: ignore[method-assign]
            result = store.before_model_call(
                "Plan the next SEO loop.",
                thread_id="seo-demo",
                scope="professional",
                agent_id="planner",
            )
            metadata = result["prompt_envelope"]["metadata"]
            self.assertFalse(metadata["memory_allowed"])
            self.assertEqual(metadata["operational_failure"]["code"], "memory_unavailable")
            self.assertEqual(result["selected_branch_ids"], [])
            self.assertTrue(any("memory unavailable" in warning for warning in result["warnings"]))
            self.assertIn(
                "No relevant memory branches",
                result["prompt_envelope"]["messages"][1]["content"],
            )

            with self.assertRaises(RuntimeError):
                store.before_model_call(
                    "Plan the next SEO loop.",
                    scope="professional",
                    fallback_on_error=False,
                )
            store.close()

    def test_after_saved_turn_marks_keeper_failed_when_extractor_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "memory.db", extractor=FailingExtractor())
            store.init_db()

            result = store.after_saved_turn(
                thread_id="seo-demo",
                scope="professional",
                user_text="Decision: demo-site should reuse the successful loop.",
                assistant_text="I will reuse it.",
                agent_id="planner",
            )

            self.assertEqual(result["status"], "failed")
            self.assertEqual(result["candidate_ids"], [])
            self.assertEqual(result["event_id"], "")
            self.assertGreaterEqual(len(result["saved_turn_ids"]), 2)
            self.assertTrue(any("keeper failed" in warning for warning in result["warnings"]))

            changes = store.memory_changes(keeper_job_id=result["keeper_job_id"])
            self.assertEqual(changes["keeper_job"]["status"], "failed")
            self.assertGreaterEqual(len(changes["saved_turns"]), 2)
            self.assertEqual(changes["candidates"], [])
            self.assertEqual(
                changes["keeper_job"]["metadata"]["operational_failure"]["code"],
                "keeper_failed",
            )
            store.close()

    def test_operational_status_endpoint_and_mcp_tool_are_available(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "memory.db")
            store.init_db()

            status = store.operational_status()
            self.assertEqual(status["version"], "operational-failure-v0.1")
            self.assertEqual(status["status"], "pass")
            self.assertEqual(status["mode"], "normal")

            endpoint = handle_api_request(
                store,
                "/operational/status",
                {"max_db_bytes": 1, "integrity_check": True},
            )
            self.assertEqual(endpoint["status"], "warn")
            self.assertEqual(endpoint["mode"], "degraded")

            names = {tool["name"] for tool in list_mcp_tools()}
            self.assertIn("memory_operational_status", names)
            store.close()


if __name__ == "__main__":
    unittest.main()
