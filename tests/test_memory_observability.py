from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from agent_memory_kernel.cli import build_parser
from agent_memory_kernel.mcp_server import list_mcp_tools
from agent_memory_kernel.server import handle_api_request
from agent_memory_kernel.store import MemoryStore


class MemoryObservabilityTests(unittest.TestCase):
    def test_memory_observability_report_aggregates_router_keeper_and_usage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "memory.db"
            store = MemoryStore(db)
            store.init_db()
            store.remember(
                "Rule: project obs-site should inspect memory observability before rollout.",
                scope="professional",
                actor="user",
                source_type="manual",
                auto_approve=True,
            )
            before = store.before_model_call(
                "Plan obs-site rollout with memory observability.",
                thread_id="obs-thread",
                scope="professional",
                agent_id="planner",
                model_id="main-model",
            )
            after = store.after_saved_turn(
                thread_id="obs-thread",
                scope="professional",
                user_text="Decision: obs-site rollout tracks Router and Keeper telemetry.",
                assistant_text="I will include telemetry checks.",
                agent_id="planner",
                model_id="main-model",
            )
            store.record_llm_usage(
                provider="openai",
                model="cheap-memory-model",
                scope="professional",
                thread_id="obs-thread",
                prompt_tokens=120,
                completion_tokens=30,
                cost=0.0125,
            )

            report = store.memory_observability_report(
                scope="professional",
                thread_id="obs-thread",
            )

            self.assertEqual(report["version"], "memory-observability-v0.1")
            self.assertEqual(report["router"]["run_count"], 1)
            self.assertEqual(report["router"]["latest_runs"][0]["router_run_id"], before["router_run_id"])
            self.assertTrue(report["router"]["latest_runs"][0]["selected_branch_ids"])
            self.assertGreater(report["router"]["latest_runs"][0]["token_estimate"], 0)
            self.assertEqual(report["keeper"]["job_count"], 1)
            self.assertEqual(report["keeper"]["status_counts"]["completed"], 1)
            self.assertEqual(report["keeper"]["latest_jobs"][0]["keeper_job_id"], after["keeper_job_id"])
            self.assertEqual(report["usage"]["call_count"], 1)
            self.assertEqual(report["usage"]["total_tokens"], 150)
            self.assertEqual(report["usage"]["by_model"]["openai:cheap-memory-model"]["cost"], 0.0125)
            self.assertEqual(report["usage"]["by_currency"]["USD"]["cost"], 0.0125)

            endpoint = handle_api_request(
                store,
                "/observability",
                {"scope": "professional", "thread_id": "obs-thread"},
            )
            self.assertEqual(endpoint["usage"]["total_tokens"], 150)

            names = {tool["name"] for tool in list_mcp_tools()}
            self.assertIn("memory_observability", names)
            store.close()

    def test_observability_cli_outputs_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = str(Path(tmp) / "memory.db")
            store = MemoryStore(db)
            store.init_db()
            store.record_llm_usage(
                provider="openai",
                model="keeper-mini",
                scope="professional",
                thread_id="cli-thread",
                prompt_tokens=10,
                completion_tokens=5,
                cost=0.001,
            )
            store.close()

            parser = build_parser()
            args = parser.parse_args(
                [
                    "observability",
                    "--db",
                    db,
                    "--scope",
                    "professional",
                    "--thread-id",
                    "cli-thread",
                ]
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = args.func(args)

            self.assertEqual(code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["version"], "memory-observability-v0.1")
            self.assertEqual(payload["usage"]["total_tokens"], 15)


if __name__ == "__main__":
    unittest.main()
