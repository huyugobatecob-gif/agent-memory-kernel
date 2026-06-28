from __future__ import annotations

import json
import unittest
from types import SimpleNamespace

from agent_memory_kernel.extractors import OpenAIExtractor


class _ResponsesEndpoint:
    def __init__(self, output_text: str):
        self.output_text = output_text
        self.last_kwargs = {}

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return SimpleNamespace(output_text=self.output_text)


class _ResponsesClient:
    def __init__(self, output_text: str):
        self.responses = _ResponsesEndpoint(output_text)


class _ChatCompletionsEndpoint:
    def __init__(self, output_text: str):
        self.output_text = output_text
        self.last_kwargs = {}

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        message = SimpleNamespace(content=self.output_text)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


class _ChatClient:
    def __init__(self, output_text: str):
        self.chat = SimpleNamespace(completions=_ChatCompletionsEndpoint(output_text))


class OpenAIExtractorTests(unittest.TestCase):
    def test_responses_client_extracts_structured_memories(self) -> None:
        payload = {
            "memories": [
                {
                    "text": "Rule: demo-site content refreshes must include internal links.",
                    "kind": "rule",
                    "confidence": "high",
                    "nodes": [{"type": "project", "label": "demo-site"}],
                    "edges": [
                        {
                            "source": "demo-site",
                            "target": "internal links",
                            "type": "requires",
                        }
                    ],
                }
            ]
        }
        client = _ResponsesClient(json.dumps(payload))
        extractor = OpenAIExtractor(client, model="cheap-memory-model")

        memories = extractor.extract("User discussed demo-site internal links.", scope="professional")

        self.assertEqual(len(memories), 1)
        self.assertEqual(memories[0].kind, "rule")
        self.assertEqual(memories[0].confidence, "high")
        self.assertEqual(memories[0].nodes[0]["label"], "demo-site")
        self.assertEqual(memories[0].edges[0]["type"], "requires")
        self.assertEqual(client.responses.last_kwargs["model"], "cheap-memory-model")

    def test_chat_client_shape_is_supported(self) -> None:
        payload = [
            {
                "text": "Decision: keep memory storage local-first.",
                "kind": "decision",
                "confidence": "medium",
                "nodes": [{"type": "memory", "label": "local-first"}],
            }
        ]
        client = _ChatClient("```json\n" + json.dumps(payload) + "\n```")
        extractor = OpenAIExtractor(client)

        memories = extractor.extract("We decided to keep memory local-first.")

        self.assertEqual(len(memories), 1)
        self.assertEqual(memories[0].kind, "decision")
        self.assertEqual(memories[0].nodes[0]["label"], "local-first")
        self.assertIn("messages", client.chat.completions.last_kwargs)

    def test_invalid_model_output_uses_deterministic_fallback(self) -> None:
        extractor = OpenAIExtractor(_ResponsesClient("not json"))

        memories = extractor.extract("Rule: fallback should still create a candidate.")

        self.assertEqual(len(memories), 1)
        self.assertEqual(memories[0].kind, "rule")
        self.assertIn("fallback", memories[0].text)


if __name__ == "__main__":
    unittest.main()
