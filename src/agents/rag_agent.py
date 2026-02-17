# src/agents/rag_agent.py

"""
RAG agent is responsible for:
1. retrieving relevant log data and manuals for guidance 
2. combining these into a prompt
3. sending the prompt to an LLM
"""

# Import libraries
import numpy as np
# Import dependencies
from core.providers.factory import create_vector_provider
from core.providers.vector.base import VectorProvider

class RAGAgent:
    def __init__(
        self,
        domain_config=None,
        collection_name="sir_collections",
        output_fields=None,
        limit=5,
        vector_provider: VectorProvider = None,
    ):
        self.domain_config = domain_config or {}
        rag_cfg = self.domain_config.get("rag", {})
        self.collection_name = rag_cfg.get("collection_name", collection_name)
        self.output_fields = rag_cfg.get("output_fields", output_fields or ["text_content"])
        self.result_text_field = rag_cfg.get("result_text_field", "text_content")
        self.limit = rag_cfg.get("limit", limit)
        self.no_context_fallback = rag_cfg.get(
            "no_context_fallback",
            "I couldn't retrieve supporting context for that request. Please try rephrasing your question.",
        )

        provider_cfg = dict(
            self.domain_config.get("providers", {}).get("vector", {"type": "argo_milvus"})
        )
        self.vector_provider = vector_provider or create_vector_provider(provider_cfg)

        self.embedding_model = rag_cfg.get("embedding_model", "v3large")
        self.chat_model = rag_cfg.get("chat_model", "gpt4o")

        self.instructions = self.domain_config.get("prompts", {}).get(
            "rag_system_prompt",
            (
                "You are a domain expert agent. Use provided context to answer the question "
                "clearly and concisely for a general audience."
            ),
        )

    def generate_embeddings(self, text: str):
        """Generate embeddings using Argo API."""

        print(f"[DEBUG] Generating embeddings for input: {text}")
        embeddings = self.vector_provider.embed(model=self.embedding_model, prompts=[text])

        # Normalize expected structure
        if isinstance(embeddings, dict) and "embedding" in embeddings:
            vec = embeddings["embedding"]
            print(f"[DEBUG] Received vector (dict): dim={len(vec[0])}")
            return vec[0]

        elif isinstance(embeddings, list) and isinstance(embeddings[0], list):
            print(f"[DEBUG] Received vector (list): dim={len(embeddings[0])}")
            return embeddings[0]

        raise ValueError(f"[ERROR] Unexpected embedding format: {embeddings}")

    def search_documents(self, vector):
        """Search for relevant documents in Milvus using Argo API."""
        vector = np.array(vector, dtype=np.float32).tolist()
        print(f"[DEBUG] Searching Milvus with vector of dim: {len(vector)}")

        results = self.vector_provider.search(
            collection=self.collection_name,
            vector=vector,
            output_fields=self.output_fields,
            limit=self.limit,
        )

        if not results or "data" not in results:
            raise ValueError(f"[ERROR] Failed to retrieve documents. Got: {results}")

        docs = []
        for row in results["data"]:
            text = row.get(self.result_text_field)
            if not text:
                for fallback_key in ["text_content", "page_content", "content", "text"]:
                    if row.get(fallback_key):
                        text = row.get(fallback_key)
                        break
            if not text:
                for value in row.values():
                    if isinstance(value, str) and value.strip():
                        text = value
                        break
            if text:
                docs.append(text)

        return docs

    def generate_response(self, context: str, question: str):
        """Generate natural language answer using Argo chat API."""
        prompt = f"Context:\n{context}\n\nQuestion:\n{question}"
        print(f"[DEBUG] Sending prompt to chat model...")

        response = self.vector_provider.chat(
            instructions=self.instructions,
            model=self.chat_model,
            prompt=prompt,
        )

        if response:
            print(f"[DEBUG] Chat model response received")
            return response.strip()
        else:
            raise ValueError("[ERROR] Failed to generate response.")

    def answer(self, question: str) -> str:
        """Main RAG pipeline."""
        print(f"[RAG] Answering: {question}")

        # Step 1: Embed question
        question_embeddings = self.generate_embeddings(question)

        # Step 2: Retrieve relevant chunks
        retrieved_docs = self.search_documents(question_embeddings)
        if not retrieved_docs:
            return self.no_context_fallback

        # Step 3: Build context
        context = "\n---\n".join(retrieved_docs)

        # Step 4: Generate and return answer
        return self.generate_response(context=context, question=question)
