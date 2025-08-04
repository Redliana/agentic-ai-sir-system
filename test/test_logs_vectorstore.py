# test.test_logs_vectorstore.py

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings

# Load the log vectorstore directly
vectorstore = FAISS.load_local(
    folder_path="faiss_store_logs",
    embeddings=OllamaEmbeddings(model="nomic-embed-text"),
    index_name="index",
    allow_dangerous_deserialization=True
)

# Create retriever
retriever = vectorstore.as_retriever()

# Test query
query = "What happened at step 3 of run 2?"

# Retrieve docs
docs = retriever.invoke(query)

# Show results
print(f"\n🔍 Retrieved {len(docs)} documents:")
for i, doc in enumerate(docs):
    print(f"\n--- Document {i+1} ---")
    print(doc.page_content[:500])
