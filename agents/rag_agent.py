# agents.rag_agent.py

from langchain_core.runnables import Runnable
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms.ollama import Ollama
from langchain.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain

class RAGAgent:
    def __init__(self, vectorstore_dir="vectorstore/faiss_store"):
        # Load vectorstore
        self.vectorstore_dir = vectorstore_dir
        self.vectorstore = FAISS.load_local(
            folder_path=self.vectorstore_dir,
            embeddings=OllamaEmbeddings(),
            index_name="index",
            allow_dangerous_deserialization=True
        )

        # Setup retriever
        self.retriever = self.vectorstore.as_retriever()

        # Load LLM
        self.llm = Ollama(model="mistral")

        # Create prompt (optional: customize this template)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI agent analyzing epidemic simulation data."),
            ("user", "{input}")
        ])

        # Create document combination chain
        self.combine_docs_chain = create_stuff_documents_chain(
            llm=self.llm,
            prompt=self.prompt
        )

        # Create retrieval-augmented generation chain
        self.rag_chain: Runnable = create_retrieval_chain(
            retriever=self.retriever,
            combine_docs_chain=self.combine_docs_chain
        )

    def answer(self, question: str) -> str:
        response = self.rag_chain.invoke({"input": question})
        return response["answer"]
