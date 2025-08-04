# agents.rag_agent.py

from langchain_core.runnables import Runnable
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms.ollama import Ollama
from langchain.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
import os

class RAGAgent:
    def __init__(self, vectorstore_dir: str = "vectorstore/faiss_store"):
        
        # === Load Vectorstore ===
        if not os.path.exists(os.path.join(vectorstore_dir, "index.faiss")):
            raise FileNotFoundError(f"FAISS index not found in: {vectorstore_dir}")

        self.vectorstore = FAISS.load_local(
            folder_path=vectorstore_dir,
            embeddings=OllamaEmbeddings(model="nomic-embed-text"),
            index_name="index",
            allow_dangerous_deserialization=True
        )

        self.llm = Ollama(model="mistral")

        # === Retriever ===
        self.retriever = self.vectorstore.as_retriever()

        # === Prompt ===
        self.prompt = ChatPromptTemplate.from_template(
            """You are a helpful AI agent analyzing epidemic simulation data.
            Use the following context to answer the user's question.
            
            Context: {context}

            Question: {input}
            
            Answer:
            """
            )

        # === Combine Documents + Retrieval Chain ===
        self.combine_docs_chain = create_stuff_documents_chain(llm=self.llm, prompt=self.prompt)
        self.rag_chain: Runnable = create_retrieval_chain(retriever=self.retriever, combine_docs_chain=self.combine_docs_chain)

    def answer(self, question: str) -> str:
        """
        Runs RAG pipeline on the user's question.
        Returns the answer as a string.
        """
        print(f"RAGAgent received question: {question}")
        result = self.rag_chain.invoke({"input": question})
        return result["answer"]
