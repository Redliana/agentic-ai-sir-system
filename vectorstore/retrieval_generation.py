# vectorstore.retrieval_generation.py

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms.ollama import Ollama
from langchain_core.runnables import RunnableMap
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# === Settings ===
INDEX_DIR = "faiss_store"
QUERY = "You are an expert data analysis agent. Please consider all runs when answering this question. When did peak infection occur?"

# === Load FAISS Index ===
embedding_model = OllamaEmbeddings(model="nomic-embed-text")
vectorstore = FAISS.load_local(INDEX_DIR, embedding_model, allow_dangerous_deserialization=True)
retriever = vectorstore.as_retriever()

# === LLM Setup ===
llm = Ollama(model="mistral")

# === Prompt Template ===
template = """Use the following context to answer the question.

Context:
{context}

Question:
{question}

Answer in a short and clear sentence."""
prompt = PromptTemplate.from_template(template)

# === Chain ===
chain = (
    RunnableMap({
        "context": lambda x: retriever.invoke(x["question"]),
        "question": lambda x: x["question"],
    })
    | prompt
    | llm
    | StrOutputParser()
)

# === Run Retrieval ===
result = chain.invoke({"question": QUERY})
print("\n🧠 Answer:")
print(result)