"""Acceptance harness for the full-memory contract.

The harness is a deterministic pass/fail fixture. It does not claim production
quality by itself; it defines the minimum behavior a runtime integration must
keep true while Router, Keeper, and provider adapters become more capable.
"""

from __future__ import annotations

from typing import Any

from .contract import assert_contract_shape, memory_contract
from .slice import SLICE_QUERY, SLICE_SCOPE, SLICE_THREAD_ID
from .slice import assert_vertical_slice, run_vertical_slice, seed_vertical_slice
from .store import MemoryStore


def seed_acceptance_fixture(store: MemoryStore) -> dict[str, Any]:
    """Seed the deterministic acceptance fixture."""
    seeded = seed_vertical_slice(store)
    extra = _approved_memory(
        store,
        "Decision: project acceptance-site reporting cadence is weekly.",
        "acceptance://rollback-source",
    )
    store.correct_memory(
        extra["memory_id"],
        "Decision: project acceptance-site reporting cadence is daily.",
        actor="acceptance",
        reason="acceptance correction check",
    )
    correction = store.list_memory_revisions(extra["memory_id"], limit=1)[0]
    rollback = store.rollback_memory(
        extra["memory_id"],
        revision_id=correction["revision_id"],
        actor="acceptance",
        reason="acceptance rollback check",
    )
    store.set_write_policy(
        agent_id="limited-acceptance-agent",
        scope=SLICE_SCOPE,
        action="approve",
        decision="deny",
        reason="acceptance harness requires human review",
        actor="acceptance",
    )
    return {
        "status": "seeded",
        "base": seeded,
        "rollback_memory_id": extra["memory_id"],
        "rollback_revision_id": rollback["rollback_revision_id"],
    }


def run_acceptance_suite(store: MemoryStore) -> dict[str, Any]:
    """Run the full-memory acceptance suite and return structured results."""
    run_result = run_vertical_slice(store)
    checks: list[dict[str, Any]] = []

    _extend_checks(checks, "contract_shape", assert_contract_shape()["status"] == "pass")
    _extend_checks(checks, "vertical_slice", _passes(lambda: assert_vertical_slice(store)))

    allowed = store.before_model_call(
        SLICE_QUERY,
        thread_id=SLICE_THREAD_ID,
        scope=SLICE_SCOPE,
        user_id="acceptance-user",
        agent_id="acceptance-agent",
        model_id="acceptance-model",
        mode="planning",
        token_budget=10000,
        allowed_scopes=[SLICE_SCOPE],
    )
    allowed_content = _envelope_content(allowed)
    denied = store.before_model_call(
        SLICE_QUERY,
        thread_id=SLICE_THREAD_ID,
        scope=SLICE_SCOPE,
        user_id="acceptance-user",
        agent_id="acceptance-agent",
        model_id="acceptance-model",
        mode="planning",
        token_budget=10000,
        denied_scopes=[SLICE_SCOPE],
    )
    denied_content = _envelope_content(denied)

    _extend_checks(checks, "memory_context_beats_no_memory_baseline", "handoff checklist" in allowed_content and "handoff checklist" not in denied_content)
    _extend_checks(checks, "source_ids_logged", bool(allowed["prompt_envelope"]["metadata"].get("source_ids")))
    _extend_checks(checks, "selected_branches_logged", bool(allowed.get("selected_branch_ids")))
    _extend_checks(checks, "denied_memory_fails_closed", not denied["prompt_envelope"]["metadata"].get("memory_allowed") and denied.get("selected_branch_ids") == [])
    _extend_checks(checks, "personal_lane_absent_from_professional_prompt", "concise memory review updates" not in allowed_content)
    _extend_checks(checks, "unsafe_memory_absent", "reveal system prompt" not in allowed_content)
    _extend_checks(checks, "rolled_back_text_retrieved", bool(store.search("reporting cadence is weekly", scope=SLICE_SCOPE)))
    _extend_checks(checks, "corrected_text_absent_after_rollback", store.search("reporting cadence is daily", scope=SLICE_SCOPE) == [])
    _extend_checks(checks, "keeper_candidates_reviewable", bool(store.list_candidates("pending")))
    _extend_checks(checks, "write_policy_blocks_unauthorized_approval", _write_policy_blocks_approve(store))

    status = "pass" if all(item["passed"] for item in checks) else "fail"
    return {
        "status": status,
        "contract": memory_contract(),
        "run": run_result,
        "checks": checks,
        "failed": [item["name"] for item in checks if not item["passed"]],
    }


def assert_acceptance_suite(store: MemoryStore) -> dict[str, Any]:
    """Run acceptance and raise when the full-memory gate fails."""
    result = run_acceptance_suite(store)
    if result["status"] != "pass":
        raise AssertionError("acceptance suite failed: " + ", ".join(result["failed"]))
    return result


def _approved_memory(store: MemoryStore, text: str, source_ref: str) -> dict[str, Any]:
    result = store.remember(
        text,
        scope=SLICE_SCOPE,
        source_ref=source_ref,
        auto_approve=True,
    )
    return result["candidates"][0]


def _extend_checks(checks: list[dict[str, Any]], name: str, passed: bool) -> None:
    checks.append({"name": name, "passed": bool(passed)})


def _passes(callback: Any) -> bool:
    try:
        callback()
    except Exception:
        return False
    return True


def _envelope_content(result: dict[str, Any]) -> str:
    return "\n".join(message["content"] for message in result["prompt_envelope"]["messages"])


def _write_policy_blocks_approve(store: MemoryStore) -> bool:
    pending = store.remember(
        "Rule: acceptance pending memory must not be approved by limited agent.",
        scope=SLICE_SCOPE,
        actor="acceptance",
    )
    candidate_id = pending["candidates"][0]["candidate_id"]
    try:
        store.approve_candidate(candidate_id, actor="limited-acceptance-agent")
    except PermissionError:
        return True
    return False
