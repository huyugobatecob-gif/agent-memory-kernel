from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agent_memory_kernel import MemoryStore
from agent_memory_kernel.acceptance import (
    assert_acceptance_suite,
    run_acceptance_suite,
    seed_acceptance_fixture,
)
from agent_memory_kernel.contract import assert_contract_shape, memory_contract
from agent_memory_kernel.server import handle_api_request


class ContractAcceptanceTests(unittest.TestCase):
    def test_memory_contract_shape_is_stable(self) -> None:
        contract = memory_contract()
        result = assert_contract_shape(contract)

        self.assertEqual(result["status"], "pass")
        self.assertIn("personal", contract["lanes"])
        self.assertIn("professional", contract["lanes"])
        self.assertIn("project", contract["extension_lanes"])
        self.assertIn("before_model_call runs before a non-incognito main model call", str(contract))
        self.assertIn("revise_or_forget", contract["closed_loop"])

    def test_acceptance_suite_passes_seeded_full_memory_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "memory.db")
            store.init_db()

            seeded = seed_acceptance_fixture(store)
            self.assertEqual(seeded["status"], "seeded")

            result = run_acceptance_suite(store)
            self.assertEqual(result["status"], "pass")
            check_names = {item["name"] for item in result["checks"] if item["passed"]}
            self.assertIn("memory_context_beats_no_memory_baseline", check_names)
            self.assertIn("personal_lane_absent_from_professional_prompt", check_names)
            self.assertIn("rolled_back_text_retrieved", check_names)
            self.assertIn("write_policy_blocks_unauthorized_approval", check_names)

            asserted = assert_acceptance_suite(store)
            self.assertEqual(asserted["status"], "pass")
            store.close()

    def test_http_contract_and_acceptance_endpoints(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "memory.db")
            store.init_db()

            contract = handle_api_request(store, "/contract", {})
            self.assertIn("acceptance_gates", contract)
            contract_assert = handle_api_request(store, "/contract/assert", {})
            self.assertEqual(contract_assert["status"], "pass")

            seeded = handle_api_request(store, "/acceptance/seed", {})
            self.assertEqual(seeded["status"], "seeded")
            result = handle_api_request(store, "/acceptance/assert", {})
            self.assertEqual(result["status"], "pass")
            store.close()
