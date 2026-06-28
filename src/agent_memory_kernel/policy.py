"""Safety and admission policy for memory writes."""

from __future__ import annotations

import re
from dataclasses import dataclass


SECRET_PATTERNS = [
    re.compile(r"(?i)\b(api[_-]?key|token|secret|password|passwd|pwd)\b\s*[:=]\s*\S+"),
    re.compile(r"(?i)\b(bearer\s+[a-z0-9._~+/=-]{16,})\b"),
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |PGP )?PRIVATE KEY-----"),
    re.compile(r"(?i)\b(cookie|sessionid|refresh[_-]?token)\b\s*[:=]\s*\S+"),
]
PROMPT_INJECTION_PATTERNS = [
    re.compile(r"(?i)\bignore (?:all )?(?:previous|prior|earlier) instructions\b"),
    re.compile(r"(?i)\bdisregard (?:all )?(?:previous|prior|earlier) instructions\b"),
    re.compile(r"(?i)\breveal (?:the )?(?:system prompt|developer message|hidden instructions|secrets)\b"),
    re.compile(r"(?i)\btreat (?:this|the following) as (?:a )?(?:system|developer) instruction\b"),
    re.compile(r"(?i)\boverride (?:the )?(?:system|developer|user) instructions\b"),
]

ALLOWED_SCOPES = {"personal", "professional", "project", "agent", "session"}
ALLOWED_CONFIDENCE = {"low", "medium", "high", "confirmed"}
ALLOWED_SOURCE_TRUST = {"trusted", "untrusted", "system", "user"}
ALLOWED_SENSITIVITY = {"public", "internal", "personal", "secret"}


@dataclass(frozen=True)
class PolicyDecision:
    status: str
    sensitivity: str
    source_trust: str
    reason: str


def normalize_scope(scope: str) -> str:
    scope = (scope or "professional").strip().lower()
    return scope if scope in ALLOWED_SCOPES else "professional"


def normalize_scope_list(scopes: list[str] | tuple[str, ...] | set[str] | None) -> list[str]:
    normalized: list[str] = []
    for scope in scopes or []:
        item = normalize_scope(str(scope))
        if item not in normalized:
            normalized.append(item)
    return normalized


def resolve_scope_access(
    scope: str,
    *,
    requested_lanes: list[str] | None = None,
    allowed_scopes: list[str] | None = None,
    denied_scopes: list[str] | None = None,
) -> tuple[bool, list[dict[str, str]], list[str]]:
    active_scope = normalize_scope(scope)
    lanes = normalize_scope_list(requested_lanes or [active_scope])
    if active_scope not in lanes:
        lanes.insert(0, active_scope)
    allowed = set(normalize_scope_list(allowed_scopes if allowed_scopes is not None else [active_scope]))
    denied = set(normalize_scope_list(denied_scopes))
    warnings: list[str] = []
    decisions: list[dict[str, str]] = []

    for lane in lanes:
        if lane in denied:
            decisions.append(
                {
                    "scope": lane,
                    "decision": "deny",
                    "reason": "scope explicitly denied",
                }
            )
        elif lane not in allowed:
            decisions.append(
                {
                    "scope": lane,
                    "decision": "deny",
                    "reason": "scope not in allowed_scopes",
                }
            )
        elif lane == active_scope:
            decisions.append(
                {
                    "scope": lane,
                    "decision": "allow",
                    "reason": "scope allowed for this model call",
                }
            )
        else:
            decisions.append(
                {
                    "scope": lane,
                    "decision": "not_selected",
                    "reason": "v0 runtime retrieves one active scope per call",
                }
            )

    active_allowed = any(
        item["scope"] == active_scope and item["decision"] == "allow" for item in decisions
    )
    if not active_allowed:
        warnings.append(f"memory access denied for scope: {active_scope}")
    if len(set(lanes)) > 1:
        warnings.append("multi-lane request evaluated by scope access policy")
    return active_allowed, decisions, warnings


def normalize_confidence(confidence: str) -> str:
    confidence = (confidence or "medium").strip().lower()
    return confidence if confidence in ALLOWED_CONFIDENCE else "medium"


def classify_sensitivity(text: str, requested: str = "internal") -> str:
    requested = (requested or "internal").strip().lower()
    if any(pattern.search(text or "") for pattern in SECRET_PATTERNS):
        return "secret"
    return requested if requested in ALLOWED_SENSITIVITY else "internal"


def looks_like_prompt_injection(text: str) -> bool:
    return any(pattern.search(text or "") for pattern in PROMPT_INJECTION_PATTERNS)


def source_trust_for(source_type: str) -> str:
    source_type = (source_type or "manual").strip().lower()
    if source_type in {"manual", "user", "profile", "vault"}:
        return "trusted"
    if source_type in {"system"}:
        return "system"
    return "untrusted"


def admission_policy(
    text: str,
    *,
    source_type: str = "manual",
    sensitivity: str = "internal",
    auto_approve: bool = False,
) -> PolicyDecision:
    """Return the initial candidate status and trust metadata.

    v0 keeps admission intentionally conservative. Manual/user notes can be
    auto-approved only when requested and only if no secret-like text is found.
    External/tool/web sources remain pending by default.
    """
    detected_sensitivity = classify_sensitivity(text, sensitivity)
    trust = source_trust_for(source_type)

    if detected_sensitivity == "secret":
        return PolicyDecision(
            status="quarantined",
            sensitivity="secret",
            source_trust=trust,
            reason="secret-like content detected",
        )

    if looks_like_prompt_injection(text):
        return PolicyDecision(
            status="quarantined",
            sensitivity=detected_sensitivity,
            source_trust=trust,
            reason="prompt-injection-like content detected",
        )

    if auto_approve and trust in {"trusted", "user", "system"}:
        return PolicyDecision(
            status="approved",
            sensitivity=detected_sensitivity,
            source_trust=trust,
            reason="trusted source auto-approved",
        )

    return PolicyDecision(
        status="pending",
        sensitivity=detected_sensitivity,
        source_trust=trust,
        reason="candidate requires review",
    )
