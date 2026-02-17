# vectorstore.embedder.py

"""
This script embeds a FAISS vectorstore with:
- SIR Model Inforamtion (markdown language)

The script chunks the data based on markdown syntax such as title: (#), header (##), and sub-header (###) symbols.
It then embeds the FAISS vectorstore with the data such that the RAG agent can retrieve it to help answer user questions.
"""

# Import libraries 
import os
import pandas as pd
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# Paths for retrieving and augmenting files to the vectorstore
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "logs"))
MANUAL_PATH = os.path.normpath(
    os.path.join(BASE_DIR, "..", "domains", "sir", "knowledge", "sir_model_information.md")
)
VECTORSTORE_MANUALS_DIR = os.path.join(BASE_DIR, "faiss_store_manuals")

def load_manual_as_documents(path):
    """Load knowledge manual as document"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Manual not found: {path}")
    print(f"Loading manual: {path}")
    loader = TextLoader(path)
    return loader.load()

# Builder functions
def build_vectorstore(docs, out_dir):
    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=50)
    split_docs = splitter.split_documents(docs)
    embedding = OllamaEmbeddings(model="nomic-embed-text")
    vectorstore = FAISS.from_documents(split_docs, embedding)
    os.makedirs(out_dir, exist_ok=True)
    vectorstore.save_local(out_dir)
    print(f"Saved vectorstore to: {out_dir}")

def build_and_save_vectorstores():
    print("\nEmbedding calculation manual...")
    manual_docs = load_manual_as_documents(MANUAL_PATH)
    build_vectorstore(manual_docs, VECTORSTORE_MANUALS_DIR)

if __name__ == "__main__":
    build_and_save_vectorstores()
