# vectorstore.embedder.py

"""
This script embeds a Vectorstore (FAISS) with agent infection data
"""

# Import libraries 
import os
import pandas as pd
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Calculate absolute path to logs directory (one level above this script)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "logs"))
VECTORSTORE_DIR = os.path.normpath(os.path.join(BASE_DIR, "faiss_store"))

def load_csv_as_documents(logs_dir):
    docs = []
    if not os.path.exists(logs_dir):
        raise FileNotFoundError(f"Logs directory not found: {logs_dir}")
    for filename in os.listdir(logs_dir):
        if filename.endswith(".csv"):
            filepath = os.path.join(logs_dir, filename)
            print(f"Loading {filepath}...")
            df = pd.read_csv(filepath)
            for _, row in df.iterrows():
                # Customize string formatting as needed
                row_text = ", ".join(f"{col}: {val}" for col, val in row.items())
                doc = Document(page_content=row_text, metadata={"source": filename})
                docs.append(doc)
    return docs

def build_and_save_vectorstore():
    # 1. Load CSV rows as documents
    docs = load_csv_as_documents(LOGS_DIR)

    # 2. Optionally split large documents for better embeddings
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = splitter.split_documents(docs)

    # 3. Setup embedding model
    embedding = OllamaEmbeddings(model="nomic-embed-text")

    # 4. Create FAISS vectorstore
    vectorstore = FAISS.from_documents(split_docs, embedding)

    # 5. Save vectorstore locally
    os.makedirs(VECTORSTORE_DIR, exist_ok=True)
    vectorstore.save_local(VECTORSTORE_DIR)
    print(f"✅ FAISS vectorstore saved to {VECTORSTORE_DIR}")

if __name__ == "__main__":
    build_and_save_vectorstore()

