# agents.rag_agent.py

"""
RAG agent is responsible for:
1. retrieving relevant log data and manuals for guidance 
2. combining these into a prompt
3. sending the prompt to an LLM
"""

# Import libraries 
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms.ollama import Ollama
from langchain.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.runnables import Runnable

from utils.extractors import extract_structured_data
from utils.math_tools import calculate_peak_infection

class RAGAgent:
    def __init__(
            self,
            logs_store_dir="vectorstore/faiss_store_logs",
            manuals_store_dir="vectorstore/faiss_store_manuals"
        ):

        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        self.llm = Ollama(model="mistral")

        # Load FAISS vectorstores
        # Load the logged data document
        self.logs_store = FAISS.load_local(
            folder_path=logs_store_dir,
            embeddings=self.embeddings,
            index_name="index",
            allow_dangerous_deserialization=True
        )
        # Load the instruction manual document
        self.manuals_store = FAISS.load_local(
            folder_path=manuals_store_dir,
            embeddings=self.embeddings,
            index_name="index",
            allow_dangerous_deserialization=True
        )

        # Create retrievers for both documents
        self.logs_retriever = self.logs_store.as_retriever()
        self.manuals_retriever = self.manuals_store.as_retriever()

        # Prompt with context injection
        self.prompt = ChatPromptTemplate.from_template(
            """You are a helpful AI agent analyzing epidemic simulation data.
            Use the following context to answer the user's question.

            Context: {context}

            Question: {input}
            """
        )

        # Combine documents into single generation call
        self.combine_docs_chain = create_stuff_documents_chain(
            llm=self.llm,
            prompt=self.prompt
        )

        # For now, use only logs for answering data questions
        self.rag_chain: Runnable = create_retrieval_chain(
            retriever=self.logs_retriever,
            combine_docs_chain=self.combine_docs_chain
        )

    def answer(self, question: str, run_math: bool = False) -> str:
        result = self.rag_chain.invoke({"input": question})

        # Get retrieved docs
        raw_docs = result["context"]
        doc_texts = [doc.page_content for doc in raw_docs]

        if not run_math:
            return result["answer"]

        # Extract structured data
        structured_data = extract_structured_data(doc_texts)
        if not structured_data:
            return "I couldn't extract structured data from the logs."

        # Example tool: calculate peak infection
        if "peak infection" in question.lower():
            return calculate_peak_infection(structured_data)

        # Default fallback
        return result["answer"]