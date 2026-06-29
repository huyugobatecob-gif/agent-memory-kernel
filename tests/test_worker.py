from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from agent_memory_kernel.cli import build_parser
from agent_memory_kernel.extractors.base import Extractor
from agent_memory_kernel.mcp_server import list_mcp_tools
from agent_memory_kernel.server import handle_api_request
from agent_memory_kernel.store import MemoryStore
from agent_memory_kernel.worker import run_keeper_worker_daemon


class FailingExtractor(Extractor):
    def extract(self, text: str, *, scope: str = "professional"):
        raise RuntimeError("queued keeper model down")


class WorkerDaemonTests(unittest.TestCase):
    def test_daemon_worker_processes_queue_and_stops_when_idle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "memory.db"
            store = MemoryStore(db)
            store.init_db()
            queued = store.after_saved_turn(
                thread_id="daemon-thread",
                scope="professional",
                user_text="Decision: daemon-site uses background Keeper workers.",
                assistant_text="I will queue that memory.",
                agent_id="daemon-agent",
                keeper_mode="queued",
            )
            store.close()

            sleeps: list[float] = []
            result = run_keeper_worker_daemon(
                db,
                limit=1,
                actor="daemon-worker",
                poll_interval=0.25,
                max_iterations=3,
                stop_when_idle=True,
                sleep_func=sleeps.append,
            )

            self.assertEqual(result["mode"], "daemon")
            self.assertEqual(result["stopped_reason"], "idle")
            self.assertEqual(result["iterations"], 2)
            self.assertEqual(result["processed_total"], 1)
            self.assertEqual(sleeps, [0.25])
            self.assertEqual(result["reports"][0]["jobs"][0]["keeper_job_id"], queued["keeper_job_id"])

            verify = MemoryStore(db)
            verify.init_db()
            changes = verify.memory_changes(keeper_job_id=queued["keeper_job_id"])
            self.assertEqual(changes["keeper_job"]["status"], "completed")
            self.assertTrue(changes["keeper_job"]["candidate_ids"])
            verify.close()

    def test_worker_status_reports_queued_and_stale_jobs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "memory.db"
            store = MemoryStore(db)
            store.init_db()
            queued = store.after_saved_turn(
                thread_id="status-thread",
                scope="professional",
                user_text="Decision: status-site queues Keeper work.",
                assistant_text="I will leave this queued for worker status.",
                agent_id="status-agent",
                keeper_mode="queued",
            )

            report = store.worker_status_report(scope="professional", stale_after_seconds=0)

            self.assertEqual(report["version"], "worker-supervision-v0.1")
            self.assertEqual(report["status"], "warn")
            self.assertEqual(report["counts"]["queued"], 1)
            self.assertEqual(report["stale_jobs"][0]["keeper_job_id"], queued["keeper_job_id"])
            self.assertIn("run_once", report["recommended_commands"])

            endpoint = handle_api_request(
                store,
                "/worker/status",
                {"scope": "professional", "stale_after_seconds": 0},
            )
            self.assertEqual(endpoint["stale_jobs"][0]["keeper_job_id"], queued["keeper_job_id"])
            names = {tool["name"] for tool in list_mcp_tools()}
            self.assertIn("memory_worker_status", names)
            store.close()

    def test_queued_keeper_failure_marks_job_failed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "memory.db"
            store = MemoryStore(db, extractor=FailingExtractor())
            store.init_db()
            queued = store.after_saved_turn(
                thread_id="failed-worker-thread",
                scope="professional",
                user_text="Decision: failed-worker-site should still save turns.",
                assistant_text="I will queue that memory.",
                agent_id="daemon-agent",
                keeper_mode="queued",
            )

            processed = store.process_keeper_jobs(limit=1, actor="daemon-worker")

            self.assertEqual(processed["processed"], 1)
            self.assertEqual(processed["jobs"][0]["status"], "failed")
            self.assertTrue(any("keeper failed" in warning for warning in processed["jobs"][0]["warnings"]))
            changes = store.memory_changes(keeper_job_id=queued["keeper_job_id"])
            self.assertEqual(changes["keeper_job"]["status"], "failed")
            self.assertEqual(changes["keeper_job"]["metadata"]["operational_failure"]["code"], "keeper_failed")
            self.assertGreaterEqual(len(changes["saved_turns"]), 2)
            self.assertEqual(changes["candidates"], [])
            store.close()

    def test_worker_cli_daemon_can_run_bounded_and_quiet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = str(Path(tmp) / "memory.db")
            parser = build_parser()
            args = parser.parse_args(
                [
                    "worker",
                    "--db",
                    db,
                    "--daemon",
                    "--max-iterations",
                    "1",
                    "--poll-interval",
                    "0",
                    "--quiet",
                ]
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = args.func(args)

            self.assertEqual(code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["mode"], "daemon")
            self.assertEqual(payload["stopped_reason"], "max_iterations")
            self.assertEqual(payload["iterations"], 1)


if __name__ == "__main__":
    unittest.main()
