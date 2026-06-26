"""Placeholder OpenAI extractor adapter.

The v0 package intentionally ships without a runtime OpenAI dependency. This
module documents the adapter seam so applications can wire their preferred LLM
client while the kernel remains local-first and dependency-light.
"""

from __future__ import annotations

from .base import Extractor


class OpenAIExtractor(Extractor):
    def __init__(self, client: object, model: str):
        self.client = client
        self.model = model

    def extract(self, text: str, *, scope: str = "professional"):
        raise NotImplementedError(
            "OpenAIExtractor is an integration seam. Use RuleBasedExtractor in v0 "
            "or implement this adapter in your application."
        )
