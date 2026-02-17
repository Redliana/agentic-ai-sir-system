# src/utils/argo_utils.py

"""
Utility file for Argo and Milvus API Endpoints.
To be used by the RAG agent for:
1. Retrieving embeddings based on user prompts.
2. Performing searches based on Milvus collection.
3. Interacting with chat based on user prompts.
"""

# Import libraries
from core.providers.factory import create_vector_provider


def run_embeddings(model, prompts):
    """Sends a POST request to the Argo API and retrieves embeddings based on the provided model and prompts."""

    provider = create_vector_provider({"type": "argo_milvus"})
    return provider.embed(model=model, prompts=prompts)

def run_search(collection, data, output_fields, limit: int):
    """Performs a vector search query on a specific collection using a Milvus database API endpoint."""

    provider = create_vector_provider({"type": "argo_milvus"})
    return provider.search(
        collection=collection,
        vector=data,
        output_fields=output_fields,
        limit=limit,
    )


def run_chat(instructions, model, prompt):
    """Interacts with chat-based API endpoint for generating responses from LLM."""

    provider = create_vector_provider({"type": "argo_milvus"})
    return provider.chat(instructions=instructions, model=model, prompt=prompt)
