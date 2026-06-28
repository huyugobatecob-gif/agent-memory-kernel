from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from agent_memory_kernel import MemoryStore
from agent_memory_kernel.extractors import LLMKeeperExtractor
from agent_memory_kernel.extractors.llm import (
    KEEPER_EXTRACTION_SCHEMA_VERSION,
    keeper_request,
    parse_keeper_payload,
)


class LLMKeeperContractTests(unittest.TestCase):
    def test_keeper_request_declares_versioned_json_schema(self) -> None:
        request = keeper_request(
            "User said project demo-site uses WordPress.",
            scope="professional",
            model="cheap-keeper",
            max_memories=3,
        )

        self.assertEqual(request["model"], "cheap-keeper")
        self.assertEqual(request["response_format"]["type"], "json_schema")
        schema = request["response_format"]["json_schema"]["schema"]
        self.assertEqual(schema["properties"]["schema_version"]["const"], KEEPER_EXTRACTION_SCHEMA_VERSION)
        user_payload = json.loads(request["messages"][1]["content"])
        self.assertEqual(user_payload["schema_version"], KEEPER_EXTRACTION_SCHEMA_VERSION)
        self.assertEqual(user_payload["scope"], "professional")
        self.assertEqual(user_payload["max_memories"], 3)

    def test_llm_keeper_extracts_structured_memory_without_live_provider(self) -> None:
        calls = []

        def complete(request):
            calls.append(request)
            return {
                "output_text": json.dumps(
                    {
                        "schema_version": KEEPER_EXTRACTION_SCHEMA_VERSION,
                        "memories": [
                            {
                                "text": "Decision: project demo-site canonical CMS is WordPress.",
                                "kind": "decision",
                                "scope": "professional",
                                "confidence": "high",
                                "source_quote": "demo-site uses WordPress",
                                "reason": "user confirmed the CMS",
                                "nodes": [
                                    {
                                        "type": "project",
                                        "label": "demo-site",
                                        "summary": "SEO project",
                                    },
                                    {"type": "tool", "label": "WordPress"},
                                ],
                                "edges": [
                                    {
                                        "source": "demo-site",
                                        "target": "WordPress",
                                        "type": "uses",
                                    }
                                ],
                            }
                        ],
                    }
                )
            }

        extractor = LLMKeeperExtractor(complete, model="cheap-keeper")
        memories = extractor.extract(
            "User said: demo-site uses WordPress. Assistant answered: noted.",
            scope="professional",
        )

        self.assertEqual(len(memories), 1)
        self.assertEqual(memories[0].text, "Decision: project demo-site canonical CMS is WordPress.")
        self.assertEqual(memories[0].kind, "decision")
        self.assertEqual(memories[0].confidence, "high")
        self.assertEqual(memories[0].nodes[0]["type"], "project")
        self.assertEqual(memories[0].edges[0]["type"], "uses")
        self.assertEqual(memories[0].metadata["schema_version"], KEEPER_EXTRACTION_SCHEMA_VERSION)
        self.assertEqual(memories[0].metadata["source_quote"], "demo-site uses WordPress")
        self.assertEqual(calls[0]["model"], "cheap-keeper")

    def test_keeper_payload_requires_schema_version_when_strict(self) -> None:
        with self.assertRaises(ValueError):
            parse_keeper_payload(json.dumps({"memories": []}))

        extractor = LLMKeeperExtractor(
            lambda _request: json.dumps({"memories": []}),
            fallback_on_error=False,
        )
        with self.assertRaises(ValueError):
            extractor.extract("Rule: this should fail without schema version.")

    def test_invalid_model_output_falls_back_to_rules(self) -> None:
        extractor = LLMKeeperExtractor(lambda _request: "not json")

        memories = extractor.extract("Rule: fallback should still create a candidate.")

        self.assertEqual(len(memories), 1)
        self.assertEqual(memories[0].kind, "rule")
        self.assertIn("fallback", memories[0].text)

    def test_store_preserves_keeper_metadata_in_candidate_extraction_json(self) -> None:
        def complete(_request):
            return json.dumps(
                {
                    "schema_version": KEEPER_EXTRACTION_SCHEMA_VERSION,
                    "memories": [
                        {
                            "text": "Gotcha: demo-site thin pages need intent checks before publishing.",
                            "kind": "gotcha",
                            "confidence": "medium",
                            "source_quote": "thin pages need intent checks",
                            "nodes": [{"type": "project", "label": "demo-site"}],
                        }
                    ],
                }
            )

        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(
                Path(tmp) / "memory.db",
                extractor=LLMKeeperExtractor(complete),
            )
            store.init_db()
            result = store.remember(
                "User said: thin pages need intent checks before publishing.",
                scope="professional",
                actor="keeper",
                source_type="system",
            )
            candidate_id = result["candidates"][0]["candidate_id"]
            row = store.conn.execute(
                "SELECT extraction_json FROM candidate_memories WHERE candidate_id = ?",
                (candidate_id,),
            ).fetchone()
            extraction = json.loads(row["extraction_json"])

            self.assertEqual(extraction["metadata"]["schema_version"], KEEPER_EXTRACTION_SCHEMA_VERSION)
            self.assertEqual(extraction["metadata"]["source_quote"], "thin pages need intent checks")
            self.assertEqual(extraction["nodes"][0]["label"], "demo-site")
            store.close()


if __name__ == "__main__":
    unittest.main()
