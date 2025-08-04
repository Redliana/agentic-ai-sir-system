# vectorstore.embedder.py

"""
This script embeds a FAISS vectorstore with:
- Simulation log data (CSV rows)
- Calculation manual (plain text)
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
MANUAL_PATH = os.path.normpath(os.path.join(BASE_DIR, "..", "knowledge", "calculation_manual.txt"))
VECTORSTORE_DIR = os.path.join(BASE_DIR, "faiss_store")

# Loading the csv files as documents
def load_csv_as_documents(logs_dir):
    docs = []
    if not os.path.exists(logs_dir):
        raise FileNotFoundError(f"Logs directory not found: {logs_dir}")
    for filename in os.listdir(logs_dir):
        if filename.endswith(".csv"):
            filepath = os.path.join(logs_dir, filename)
            print(f"📄 Loading {filepath}...")
            df = pd.read_csv(filepath)
            for _, row in df.iterrows():
                row_text = ", ".join(f"{col}: {val}" for col, val in row.items())
                doc = Document(page_content=row_text, metadata={"source": filename})
                docs.append(doc)
    return docs

# Loading the calculation manaual as a document
def load_manual_as_document(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Calculation manual not found: {path}")
    print(f"📘 Loading manual: {path}")
    loader = TextLoader(path)
    return loader.load()

# Combine and embed all documents
def build_and_save_vectorstore():
    csv_docs = load_csv_as_documents(LOGS_DIR)
    manual_docs = load_manual_as_document(MANUAL_PATH)

    all_docs = csv_docs + manual_docs

    # Split for better embedding performance
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = splitter.split_documents(all_docs)

    # Setup embedding model
    embedding = OllamaEmbeddings(model="nomic-embed-text")

    # Build FAISS store
    print("Embedding documents...")
    vectorstore = FAISS.from_documents(split_docs, embedding)

    # Save vectorstore
    os.makedirs(VECTORSTORE_DIR, exist_ok=True)
    vectorstore.save_local(VECTORSTORE_DIR, index_name="index")
    print(f"FAISS vectorstore saved to: {VECTORSTORE_DIR}")

if __name__ == "__main__":
    build_and_save_vectorstore()
