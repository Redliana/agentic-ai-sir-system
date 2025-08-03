# vectorstore.vectorstore_retriever.py

"""
Execution: python3 vectorstore_retriever.py --query "Which agents were infected at step 5 in run 3?"
"""

import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings

# Config
VECTORSTORE_PATH = "vectorstore/faiss_store"
OLLAMA_MODEL = "nomic-embed-text"
TOP_K = 5  # Number of results to return

def load_vectorstore() -> FAISS:
    if not os.path.exists(VECTORSTORE_PATH):
        raise FileNotFoundError("No vectorstore found. Run vectorstore_loader.py first.")
    
    print("📦 Loading vectorstore...")
    embeddings = OllamaEmbeddings(model=OLLAMA_MODEL)
    return FAISS.load_local(VECTORSTORE_PATH, embeddings, allow_dangerous_deserialization=True)

def query_vectorstore(query: str, top_k: int = TOP_K):
    vectorstore = load_vectorstore()
    results = vectorstore.similarity_search(query, k=top_k)
    
    print("\n🔎 Top Matches:\n" + "-"*40)
    for i, doc in enumerate(results, start=1):
        print(f"[{i}] {doc.page_content}")
        print("-" * 40)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Query a FAISS vectorstore using a natural language prompt.")
    parser.add_argument("--query", required=True, help="Your natural language query.")
    parser.add_argument("--top_k", type=int, default=TOP_K, help="Number of results to return.")
    args = parser.parse_args()

    query_vectorstore(args.query, args.top_k)
