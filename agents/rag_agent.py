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

class RAGAgent:
    def __init__(self, manuals_store_dir="vectorstore/faiss_store_manuals"):
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        self.llm = Ollama(model="mistral")

        # Load only the manuals vectorstore
        self.manuals_store = FAISS.load_local(
            folder_path=manuals_store_dir,
            embeddings=self.embeddings,
            index_name="index",
            allow_dangerous_deserialization=True
        )

        # Create retriever for manuals
        self.manuals_retriever = self.manuals_store.as_retriever()

        # Prompt for manual-based answers
        self.prompt = ChatPromptTemplate.from_template(
            """You are a computational scientist with a background in modeling infectious disease spread.
            You are being asked to answer questions about epidemic simulations.
            Use the following information from the model documentation and manuals to answer the user's question.

            Please answer questions in concise and friendly manner, as if you were speaking to a general audience.

            Context:
            {context}

            Question:
            {input}

            Answer:"""
        )

        self.combine_docs_chain = create_stuff_documents_chain(
            llm=self.llm,
            prompt=self.prompt
        )

        # Retrieval-augmented generation chain (manuals only)
        self.rag_chain: Runnable = create_retrieval_chain(
            retriever=self.manuals_retriever,
            combine_docs_chain=self.combine_docs_chain
        )

    def answer(self, question: str) -> str:
        result = self.rag_chain.invoke({"input": question})
        return result["answer"]


# Import libraries 
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms.ollama import Ollama
from langchain.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.runnables import Runnable

class RAGAgent:
    def __init__(
            self,
            manuals_store_dir="vectorstore/faiss_store_manuals"
        ):

        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        self.llm = Ollama(model="mistral")

        # Load FAISS vectorstore
        # Load the instruction manual document
        self.manuals_store = FAISS.load_local(
            folder_path=manuals_store_dir,
            embeddings=self.embeddings,
            index_name="index",
            allow_dangerous_deserialization=True
        )

        # Create retrievers for both documents
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

    def answer(self, question: str) -> str:
        result = self.rag_chain.invoke({"input": question})

        # Get retrieved docs
        raw_docs = result["context"]
        doc_texts = [doc.page_content for doc in raw_docs]

        return result["answer"]