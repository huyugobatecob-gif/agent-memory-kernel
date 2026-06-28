"""Small deterministic extractor for v0.

This is intentionally modest. Production users can plug in an LLM extractor,
but the kernel should be useful and testable without a model.
"""

from __future__ import annotations

import re

from .base import ExtractedMemory, Extractor


PROJECT_RE = re.compile(r"(?i)\b(project|repo|client|workspace)\s+([A-Za-z0-9_.-]+)")
PERSON_RE = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b")


class RuleBasedExtractor(Extractor):
    """Extract one conservative candidate from a note."""

    def extract(self, text: str, *, scope: str = "professional") -> list[ExtractedMemory]:
        clean = " ".join((text or "").strip().split())
        if not clean:
            return []

        lowered = clean.lower()
        kind = "fact"
        if "i prefer" in lowered or "my preference" in lowered or "i like" in lowered:
            kind = "preference"
        elif "outcome:" in lowered or "result:" in lowered:
            kind = "outcome"
        elif "attempt:" in lowered or "attempted " in lowered:
            kind = "attempt"
        elif "rule:" in lowered or "must " in lowered or "should " in lowered:
            kind = "rule"
        elif "decided" in lowered or "decision:" in lowered:
            kind = "decision"
        elif "pattern:" in lowered or "successful" in lowered or "worked" in lowered:
            kind = "pattern"
        elif "failed" in lowered or "did not work" in lowered:
            kind = "gotcha"

        nodes: list[dict] = []
        if project_match := PROJECT_RE.search(clean):
            nodes.append(
                {
                    "type": "project",
                    "label": project_match.group(2),
                }
            )

        if scope == "personal":
            for name in PERSON_RE.findall(clean)[:3]:
                if name.lower() not in {"I", "The", "This", "That"}:
                    nodes.append({"type": "person", "label": name})

        if not nodes:
            nodes.append({"type": "memory", "label": kind})

        return [
            ExtractedMemory(
                text=clean,
                kind=kind,
                scope=scope,
                confidence="medium",
                nodes=nodes,
            )
        ]
