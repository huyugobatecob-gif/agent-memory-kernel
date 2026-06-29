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
from agent_memory_kernel.conformance import (
    assert_conformance_spec_shape,
    assert_conformance_suite,
    conformance_certification_report,
    conformance_registry_entry,
    conformance_spec,
    run_conformance_suite,
    seed_conformance_fixture,
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

    def test_conformance_suite_passes_public_memory_scenarios(self) -> None:
        spec = conformance_spec()
        spec_result = assert_conformance_spec_shape(spec)

        self.assertEqual(spec_result["status"], "pass")
        scenario_ids = {item["id"] for item in spec["scenarios"]}
        self.assertIn("prompt_envelope_contains_selected_content_only", scenario_ids)
        self.assertIn("stored_read_policy_denies_injection", scenario_ids)
        self.assertIn("personal_lane_absent_from_derived_surfaces", scenario_ids)
        self.assertIn("personal_lane_absent_from_graph_surfaces", scenario_ids)
        self.assertIn("resolved_conflict_suppresses_loser", scenario_ids)
        self.assertIn("derived_invalidation_is_auditable", scenario_ids)
        self.assertIn("distrusted_memory_absent_from_summaries_and_derived", scenario_ids)
        self.assertIn("keeper_write_is_reviewable", scenario_ids)
        self.assertIn("keeper_retry_is_idempotent", scenario_ids)
        self.assertIn("keeper_change_is_inspectable", scenario_ids)
        self.assertIn("capability_report_blocks_denied_actions", scenario_ids)
        self.assertIn("golden_trace_outcome_pack_uses_success_and_failure", scenario_ids)
        self.assertIn("golden_trace_graph_browser_shows_source_previews", scenario_ids)
        self.assertIn("golden_trace_deterministic_ranking_snapshot", scenario_ids)
        self.assertIn("golden_trace_prompt_budget_trims_context_pack", scenario_ids)
        self.assertIn("golden_trace_large_history_prompt_is_bounded", scenario_ids)
        self.assertIn("golden_trace_safe_export_redacts_memory_content", scenario_ids)
        self.assertIn("golden_trace_export_preserves_lifecycle_tombstones", scenario_ids)
        self.assertIn("golden_trace_import_restores_lifecycle_tombstones", scenario_ids)
        self.assertIn("golden_trace_import_preserves_policy_metadata", scenario_ids)
        self.assertIn("golden_trace_portable_bundle_manifest_roundtrip", scenario_ids)
        self.assertIn("migration_status_is_compatible", scenario_ids)
        self.assertIn("secret_like_memory_is_quarantined", scenario_ids)
        self.assertIn("tool_prompt_injection_is_quarantined", scenario_ids)
        self.assertIn("untrusted_tool_claim_stays_reviewable", scenario_ids)
        self.assertIn("assistant_guess_stays_reviewable", scenario_ids)
        self.assertIn("personal_full_export_requires_approval", scenario_ids)
        self.assertIn("personal_safe_export_redacts_content", scenario_ids)
        self.assertTrue(spec["golden_traces"])

        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "memory.db")
            store.init_db()

            seeded = seed_conformance_fixture(store)
            self.assertEqual(seeded["status"], "seeded")
            self.assertEqual(seeded["ids"]["unsafe_status"], "quarantined")
            self.assertEqual(seeded["ids"]["secret_status"], "quarantined")
            self.assertEqual(seeded["ids"]["tool_injection_status"], "quarantined")
            self.assertEqual(seeded["ids"]["tool_claim_status"], "pending")
            self.assertEqual(seeded["ids"]["assistant_guess_status"], "pending")

            result = run_conformance_suite(store)
            self.assertEqual(result["status"], "pass")
            passed = {item["scenario"] for item in result["results"] if item["passed"]}
            self.assertIn("professional_memory_injected_with_provenance", passed)
            self.assertIn("prompt_envelope_contains_selected_content_only", passed)
            self.assertIn("personal_lane_is_withheld", passed)
            self.assertIn("personal_lane_absent_from_derived_surfaces", passed)
            self.assertIn("personal_lane_absent_from_graph_surfaces", passed)
            self.assertIn("stored_read_policy_denies_injection", passed)
            self.assertIn("resolved_conflict_suppresses_loser", passed)
            self.assertIn("deleted_memory_absent", passed)
            self.assertIn("distrusted_memory_absent_from_summaries_and_derived", passed)
            self.assertIn("derived_invalidation_is_auditable", passed)
            self.assertIn("unsafe_memory_absent", passed)
            self.assertIn("keeper_write_is_reviewable", passed)
            self.assertIn("keeper_retry_is_idempotent", passed)
            self.assertIn("keeper_change_is_inspectable", passed)
            self.assertIn("capability_report_blocks_denied_actions", passed)
            self.assertIn("golden_trace_outcome_pack_uses_success_and_failure", passed)
            self.assertIn("golden_trace_graph_browser_shows_source_previews", passed)
            self.assertIn("golden_trace_deterministic_ranking_snapshot", passed)
            self.assertIn("golden_trace_prompt_budget_trims_context_pack", passed)
            self.assertIn("golden_trace_large_history_prompt_is_bounded", passed)
            self.assertIn("golden_trace_safe_export_redacts_memory_content", passed)
            self.assertIn("golden_trace_export_preserves_lifecycle_tombstones", passed)
            self.assertIn("golden_trace_import_restores_lifecycle_tombstones", passed)
            self.assertIn("golden_trace_import_preserves_policy_metadata", passed)
            self.assertIn("golden_trace_portable_bundle_manifest_roundtrip", passed)
            self.assertIn("migration_status_is_compatible", passed)
            self.assertIn("secret_like_memory_is_quarantined", passed)
            self.assertIn("tool_prompt_injection_is_quarantined", passed)
            self.assertIn("untrusted_tool_claim_stays_reviewable", passed)
            self.assertIn("assistant_guess_stays_reviewable", passed)
            self.assertIn("personal_full_export_requires_approval", passed)
            self.assertIn("personal_safe_export_redacts_content", passed)

            asserted = assert_conformance_suite(store)
            self.assertEqual(asserted["status"], "pass")

            certification = conformance_certification_report(
                store,
                adapter_name="unit-test-adapter",
                adapter_version="0.1",
            )
            self.assertEqual(certification["status"], "pass")
            self.assertEqual(certification["adapter"]["name"], "unit-test-adapter")
            self.assertEqual(certification["badge"]["message"], "compatible")
            self.assertIn("migration_compatibility_trace", certification["summary"]["golden_trace_ids"])
            self.assertIn("security_red_team_trace", certification["summary"]["golden_trace_ids"])
            self.assertEqual(certification["summary"]["scenario_failed"], 0)

            registry = conformance_registry_entry(
                store,
                adapter_name="Unit Test Adapter",
                adapter_version="0.1",
                runtime="python",
                repository="https://example.test/unit-adapter",
                notes="unit test registry entry",
            )
            self.assertEqual(registry["version"], "agent-memory-adapter-registry-entry-v0.1")
            self.assertTrue(registry["compatible"])
            self.assertEqual(registry["registry_id"], "unit-test-adapter-0-1")
            self.assertEqual(registry["recommended_path"], "registry/adapters/unit-test-adapter-0-1.json")
            self.assertEqual(registry["adapter"]["runtime"], "python")
            self.assertEqual(registry["publication"]["ready_for_public_registry"], True)
            self.assertEqual(registry["certification"]["summary"]["scenario_failed"], 0)
            store.close()

    def test_conformance_certification_fails_cleanly_without_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "memory.db")
            store.init_db()

            certification = conformance_certification_report(
                store,
                adapter_name="empty-adapter",
            )
            self.assertEqual(certification["status"], "fail")
            self.assertEqual(certification["badge"]["message"], "failing")
            self.assertIn("conformance_suite_execution", certification["failed"])
            self.assertEqual(certification["summary"]["scenario_failed"], 1)
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

    def test_http_conformance_endpoints(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "memory.db")
            store.init_db()

            spec = handle_api_request(store, "/conformance/spec", {})
            self.assertEqual(spec["version"], "agent-memory-conformance-v0")
            spec_assert = handle_api_request(store, "/conformance/spec/assert", {})
            self.assertEqual(spec_assert["status"], "pass")

            seeded = handle_api_request(store, "/conformance/seed", {})
            self.assertEqual(seeded["status"], "seeded")
            result = handle_api_request(store, "/conformance/assert", {})
            self.assertEqual(result["status"], "pass")
            certification = handle_api_request(
                store,
                "/conformance/certify",
                {"adapter_name": "http-test-adapter", "adapter_version": "0.1"},
            )
            self.assertEqual(certification["status"], "pass")
            self.assertEqual(certification["adapter"]["name"], "http-test-adapter")
            self.assertEqual(certification["badge"]["color"], "brightgreen")
            registry = handle_api_request(
                store,
                "/conformance/registry-entry",
                {
                    "adapter_name": "http-test-adapter",
                    "adapter_version": "0.1",
                    "runtime": "http",
                    "repository": "https://example.test/http-adapter",
                },
            )
            self.assertEqual(registry["status"], "pass")
            self.assertEqual(registry["adapter"]["runtime"], "http")
            self.assertEqual(registry["recommended_path"], "registry/adapters/http-test-adapter-0-1.json")
            store.close()
