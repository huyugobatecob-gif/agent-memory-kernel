from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agent_memory_kernel import MemoryOrchestrator, MemoryStore
from agent_memory_kernel.server import handle_api_request


class MemoryOrchestratorTests(unittest.TestCase):
    def test_orchestrator_runs_before_and_after_turn_lifecycle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "memory.db")
            store.init_db()
            store.remember(
                "Rule: project demo-site should use successful SEO refresh loops before inventing new plans.",
                scope="professional",
                actor="user",
                source_type="manual",
                auto_approve=True,
            )
            orchestrator = MemoryOrchestrator(store)

            before = orchestrator.before_turn(
                "Plan the next demo-site SEO refresh loop.",
                thread_id="seo-demo",
                scope="professional",
                agent_id="planner",
            )
            self.assertEqual(before["phase"], "before_turn")
            self.assertEqual(before["status"], "ready")
            self.assertIn("prompt_envelope", before)
            self.assertTrue(before["selected_branch_ids"])
            self.assertIn(
                "MEMORY_TREE_SUPPLEMENT",
                "\n".join(message["content"] for message in before["prompt_envelope"]["messages"]),
            )

            prompt = orchestrator.build_prompt_context(
                "Plan the next demo-site SEO refresh loop.",
                thread_id="seo-demo",
                scope="professional",
                agent_id="planner",
            )
            self.assertEqual(prompt["phase"], "build_prompt_context")
            self.assertIn("router_run_id", prompt)
            self.assertIn("messages", prompt["prompt_envelope"])

            after = orchestrator.after_turn(
                thread_id="seo-demo",
                scope="professional",
                user_id="user_default",
                agent_id="planner",
                user_text="Decision: demo-site will reuse the refresh loop pattern.",
                assistant_text="Acknowledged and will use the prior loop memory.",
            )
            self.assertEqual(after["phase"], "after_turn")
            self.assertEqual(after["mode"], "sync")
            self.assertGreaterEqual(len(after["saved_turn_ids"]), 2)
            self.assertIn("keeper_job_id", after)

            changes = store.memory_changes(keeper_job_id=after["keeper_job_id"])
            self.assertEqual(changes["keeper_job"]["keeper_job_id"], after["keeper_job_id"])
            self.assertGreaterEqual(len(changes["saved_turns"]), 2)
            store.close()

    def test_orchestrator_retrieve_record_and_ingest_graph(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "memory.db")
            store.init_db()
            orchestrator = MemoryOrchestrator(store)

            turn = orchestrator.record_turn(
                "Project demo-site uses WordPress.",
                thread_id="seo-demo",
                role="user",
                actor="user",
                scope="professional",
            )
            self.assertEqual(turn["phase"], "record_turn")
            self.assertEqual(turn["status"], "recorded")
            self.assertTrue(turn["turn_id"].startswith("turn_"))

            ingest = orchestrator.ingest_graph(
                [
                    {
                        "kind": "decision",
                        "label": "demo-site CMS",
                        "summary": "Project demo-site canonical CMS is WordPress.",
                        "evidence": "User stated the CMS during setup.",
                    }
                ],
                scope="professional",
                actor="keeper",
                source_ref=turn["turn_id"],
            )
            self.assertEqual(ingest["phase"], "ingest_graph")
            self.assertEqual(ingest["status"], "ingested")
            self.assertEqual(ingest["update_count"], 1)
            self.assertTrue(ingest["candidate_ids"])

            candidate_id = ingest["candidate_ids"][0]
            memory_id = store.approve_candidate(candidate_id, actor="reviewer")
            retrieved = orchestrator.retrieve_context(
                "Which CMS does demo-site use?",
                scope="professional",
                actor="planner",
            )
            self.assertEqual(retrieved["phase"], "retrieve_context")
            self.assertEqual(retrieved["status"], "ready")
            self.assertIn(memory_id, retrieved["memory_tree_supplement"])
            self.assertTrue(retrieved["tree"]["branches"])
            store.close()

    def test_http_orchestrator_endpoints(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "memory.db")
            store.init_db()
            store.remember(
                "Pattern: demo-site successful SEO loops refresh intent and internal links together.",
                scope="professional",
                actor="user",
                source_type="manual",
                auto_approve=True,
            )

            before = handle_api_request(
                store,
                "/before-turn",
                {
                    "query": "Plan demo-site SEO loop",
                    "scope": "professional",
                    "thread_id": "seo-demo",
                    "agent_id": "planner",
                },
            )
            self.assertEqual(before["phase"], "before_turn")
            self.assertIn("prompt_envelope", before)

            after = handle_api_request(
                store,
                "/after-turn",
                {
                    "thread_id": "seo-demo",
                    "scope": "professional",
                    "user_message": "Decision: keep internal link refresh in the next loop.",
                    "assistant_message": "I will keep that in the plan.",
                    "agent_id": "planner",
                },
            )
            self.assertEqual(after["phase"], "after_turn")
            self.assertIn("keeper_job_id", after)

            ingest = handle_api_request(
                store,
                "/ingest-graph",
                {
                    "updates": [{"text": "Gotcha: demo-site thin pages need intent checks first."}],
                    "scope": "professional",
                    "actor": "keeper",
                },
            )
            self.assertEqual(ingest["phase"], "ingest_graph")
            self.assertTrue(ingest["candidate_ids"])
            store.close()


if __name__ == "__main__":
    unittest.main()
