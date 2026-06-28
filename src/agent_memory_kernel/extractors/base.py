"""Extractor interface."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ExtractedMemory:
    text: str
    kind: str = "fact"
    scope: str = "professional"
    confidence: str = "medium"
    nodes: list[dict] = field(default_factory=list)
    edges: list[dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


class Extractor:
    """Base extractor interface."""

    def extract(self, text: str, *, scope: str = "professional") -> list[ExtractedMemory]:
        raise NotImplementedError
