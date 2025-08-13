# agents.rag_agent.py

"""
RAG agent is responsible for:
1. retrieving relevant log data and manuals for guidance 
2. combining these into a prompt
3. sending the prompt to an LLM
"""

# Import libraries
from utils.argo_utils import run_chat, run_embeddings, run_search

class RAGAgent:
    def __init__(
            self,
            collection_name="sir_collections",
            output_fields=["page_content"],
            limit=5
        ):
        self.collection_name = collection_name
        self.output_fields = output_fields
        self.limit = limit

        self.embedding_model = "v3small"
        self.chat_model = "gpt4o"

        # Prompt with context injection
        self.instructions = """
        You are an expert infectious disease AI agent, tasked with the responsibility of analyzing epidemic simulation data.
        Use the following context to answer the user's question.

        Please answer in a concise and friendly manner, as if you were speaking to a general audience.
        Your goal is to educate and expand understanding so please present your language in a way that aligns with this goal.
        """

    def generate_embeddings(self, text: str):
        """Generate embeddings using Argo API."""
        print(f"Generating embeddings for text: {text}")  # Debugging input
        embeddings = run_embeddings(model=self.embedding_model, prompts=[text])
        print(f"Embedding response: {embeddings}")  # Debugging response structure
        if embeddings and "embeddings" in embeddings:
            return embeddings["embeddings"]
        else:
            print(f"Embedding generation failed. Response: {embeddings}")  # Debugging response
            raise ValueError("Failed to generate embeddings.")

    def search_documents(self, vector):
        """Search for relevant documents in Milvus using Argo API."""
        results = run_search(
            collection=self.collection_name,
            data=[vector],
            output_fields=self.output_fields,
            limit=self.limit
        )
        if results and "results" in results:
            return [result["page_content"] for result in results["results"]]
        else:
            raise ValueError("Failed to retrieve documents.")

    def generate_response(self, context: str, question: str):
        """Generate response using Argo chat API."""
        response = run_chat(
            instructions=self.instructions,
            model=self.chat_model,
            prompt=f"Context: {context}\nQuestion: {question}"
        )
        if response:
            return response
        else:
            raise ValueError("Failed to generate response.")

    def answer(self, question: str) -> str:
        """Answer a question using RAG pipeline."""
        # Step 1: Generate embeddings for the question
        question_embeddings = self.generate_embeddings(question)

        # Step 2: Search for relevant documents in Milvus
        retrieved_docs = self.search_documents(question_embeddings)

        # Step 3: Combine retrieved documents into context
        context = "\n".join(retrieved_docs)

        # Step 4: Generate response using Argo chat API
        answer = self.generate_response(context=context, question=question)

        return answer