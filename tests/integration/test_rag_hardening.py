import os
import sys
import unittest
from unittest import mock


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from agents.rag_agent import RAGAgent
from core.providers.vector.argo_milvus import ArgoMilvusProvider


class _FakeVectorProvider:
    def __init__(self, search_payload):
        self.search_payload = search_payload
        self.chat_calls = 0

    def embed(self, model, prompts):
        return {"embedding": [[0.1, 0.2, 0.3]]}

    def search(self, collection, vector, output_fields, limit):
        return self.search_payload

    def chat(self, instructions, model, prompt):
        self.chat_calls += 1
        return "mocked answer"


class TestRAGHardening(unittest.TestCase):
    def test_search_documents_fallbacks_to_page_content(self):
        provider = _FakeVectorProvider({"data": [{"page_content": "doc from page_content"}]})
        agent = RAGAgent(domain_config={}, vector_provider=provider)
        response = agent.answer("test question")

        self.assertEqual(response, "mocked answer")
        self.assertEqual(provider.chat_calls, 1)

    def test_empty_retrieval_returns_fallback_without_chat(self):
        fallback = "no context fallback"
        domain_config = {"rag": {"no_context_fallback": fallback}}
        provider = _FakeVectorProvider({"data": [{}]})
        agent = RAGAgent(domain_config=domain_config, vector_provider=provider)

        response = agent.answer("question with no docs")
        self.assertEqual(response, fallback)
        self.assertEqual(provider.chat_calls, 0)

    def test_milvus_auth_token_is_required(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            provider = ArgoMilvusProvider(
                embed_url="https://example.com/embed",
                chat_url="https://example.com/chat",
                search_url="https://example.com/search",
            )
            with self.assertRaises(ValueError):
                provider.search(
                    collection="c",
                    vector=[0.1, 0.2],
                    output_fields=["text_content"],
                    limit=5,
                )


if __name__ == "__main__":
    unittest.main()

