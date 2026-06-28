"""Offline eval gates for Keeper extraction quality."""

from __future__ import annotations

from typing import Any, Sequence

from .extractors.base import Extractor
from .extractors.rules import RuleBasedExtractor


KEEPER_EVAL_VERSION = "keeper-eval-v0.1"

DEFAULT_KEEPER_EVALS: list[dict[str, Any]] = [
    {
        "id": "seo_rule_internal_links",
        "scope": "professional",
        "input": "Rule: demo-site content refreshes must include internal links.",
        "expected_kind": "rule",
        "must_contain": ["internal links"],
        "forbid": ["api_key", "password"],
    },
    {
        "id": "failed_loop_gotcha",
        "scope": "professional",
        "input": "The title rewrite failed and did not work for organic CTR.",
        "expected_kind": "gotcha",
        "must_contain": ["failed"],
        "forbid": ["ignore previous instructions"],
    },
    {
        "id": "personal_preference_lane",
        "scope": "personal",
        "input": "I prefer short direct summaries before detailed implementation notes.",
        "expected_kind": "preference",
        "must_contain": ["prefer"],
        "forbid": ["system prompt"],
    },
]


def keeper_eval_spec() -> dict[str, Any]:
    return {
        "version": KEEPER_EVAL_VERSION,
        "purpose": "Offline regression cases for Keeper memory extraction quality.",
        "cases": DEFAULT_KEEPER_EVALS,
    }


def run_keeper_eval(
    extractor: Extractor | None = None,
    *,
    cases: Sequence[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    extractor = extractor or RuleBasedExtractor()
    active_cases = list(cases or DEFAULT_KEEPER_EVALS)
    results: list[dict[str, Any]] = []
    for case in active_cases:
        extracted = extractor.extract(
            str(case.get("input", "")),
            scope=str(case.get("scope", "professional")),
        )
        texts = [memory.text for memory in extracted]
        kinds = [memory.kind for memory in extracted]
        joined = "\n".join(texts).lower()
        expected_kind = str(case.get("expected_kind", "")).lower()
        missing = [
            item
            for item in case.get("must_contain", [])
            if str(item).lower() not in joined
        ]
        forbidden_hits = [
            item
            for item in case.get("forbid", [])
            if str(item).lower() in joined
        ]
        kind_passed = not expected_kind or expected_kind in kinds
        passed = bool(extracted) and kind_passed and not missing and not forbidden_hits
        results.append(
            {
                "id": case.get("id", ""),
                "passed": passed,
                "expected_kind": expected_kind,
                "kinds": kinds,
                "memory_count": len(extracted),
                "missing": missing,
                "forbidden_hits": forbidden_hits,
                "texts": texts,
            }
        )
    failed = [result for result in results if not result["passed"]]
    return {
        "version": KEEPER_EVAL_VERSION,
        "status": "pass" if not failed else "fail",
        "passed": not failed,
        "failed": failed,
        "results": results,
    }
