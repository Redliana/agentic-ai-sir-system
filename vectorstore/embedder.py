# vectorstore.embedder.py

"""
This script embeds a FAISS vectorstore with:
- Simulation log data (CSV rows)
- Calculation manual (plain text)
Stores are saved seperately to support fine-tuned retrieval.
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
VECTORSTORE_MANUALS_DIR = os.path.join(BASE_DIR, "faiss_store_manuals")

# Loader functions
def load_csv_as_documents(logs_dir):
    docs = []
    if not os.path.exists(logs_dir):
        raise FileNotFoundError(f"Logs directory not found: {logs_dir}")

    for filename in os.listdir(logs_dir):
        if filename.endswith(".csv"):
            filepath = os.path.join(logs_dir, filename)
            print(f"Grouping and loading {filepath}...")
            df = pd.read_csv(filepath)
            
            # Group rows by run_id and step
            grouped = df.groupby(['run_id', 'step'])
            for (run_id, step), group_df in grouped:
                # Turn entire group into one text blob
                row_texts = [
                    ", ".join(f"{col}: {val}" for col, val in row.items())
                    for _, row in group_df.iterrows()
                ]
                page_content = f"Run ID: {run_id}, Step: {step}\n" + "\n".join(row_texts)
                doc = Document(
                    page_content=page_content,
                    metadata={"run_id": run_id, "step": step, "source": filename}
                )
                docs.append(doc)
    return docs

def load_manual_as_documents(path):
    """Load knowledge manual as document"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Manual not found: {path}")
    print(f"Loading manual: {path}")
    loader = TextLoader(path)
    return loader.load()

# Builder functions
def build_vectorstore(docs, out_dir):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = splitter.split_documents(docs)
    embedding = OllamaEmbeddings(model="nomic-embed-text")
    vectorstore = FAISS.from_documents(split_docs, embedding)
    os.makedirs(out_dir, exist_ok=True)
    vectorstore.save_local(out_dir)
    print(f"Saved vectorstore to: {out_dir}")

def build_and_save_vectorstores():
    #print("\nEmbedding simulation logs...")
    #csv_docs = load_csv_as_documents(LOGS_DIR)
    #build_vectorstore(csv_docs, VECTORSTORE_LOGS_DIR)

    print("\nEmbedding calculation manual...")
    manual_docs = load_manual_as_documents(MANUAL_PATH)
    build_vectorstore(manual_docs, VECTORSTORE_MANUALS_DIR)

if __name__ == "__main__":
    build_and_save_vectorstores()
