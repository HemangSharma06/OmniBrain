import warnings
warnings.filterwarnings("ignore")
from pathlib import Path

# from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient


def loadVectorStore():

    print("Connecting to Qdrant Vector Database...")

    project_root = Path(__file__).resolve().parents[2]
    db_path = project_root / "db" / "qdrant_db"

    # Embedding Model
    # embedding_model = OpenAIEmbeddings(
    #     model="text-embedding-3-small"
    # )
    embedding_model = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5"
    )

    client = QdrantClient(
        path=str(db_path)
    )

    vectorstore = QdrantVectorStore(
        client=client,
        collection_name="omnibrain",
        embedding=embedding_model
    )

    return vectorstore

def getRetriever():

    vectorstore = loadVectorStore()
    retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": 5
        }
    )
    return retriever

def searchDocuments(query):
    retriever = getRetriever()
    documents = retriever.invoke(query)
    return documents