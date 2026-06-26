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


def normalize_confidence(confidence: str) -> str:
    confidence = (confidence or "medium").strip().lower()
    return confidence if confidence in ALLOWED_CONFIDENCE else "medium"


def classify_sensitivity(text: str, requested: str = "internal") -> str:
    requested = (requested or "internal").strip().lower()
    if any(pattern.search(text or "") for pattern in SECRET_PATTERNS):
        return "secret"
    return requested if requested in ALLOWED_SENSITIVITY else "internal"


def source_trust_for(source_type: str) -> str:
    source_type = (source_type or "manual").strip().lower()
    if source_type in {"manual", "user", "profile"}:
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
