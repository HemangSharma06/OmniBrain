import warnings
warnings.filterwarnings("ignore")
from pathlib import Path

# from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore

embedding_model = None
retriever = None


def getRetriever(k):
    global embedding_model, retriever

    if retriever is None:
        print("Loading Retriever...")

        # Embedding Model
        # embedding_model = OpenAIEmbeddings(
        #     model="text-embedding-3-small"
        # )
        
        embedding_model = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5"
        )
        project_root = Path(__file__).resolve().parents[2]
        db_path = project_root / "db" / "qdrant_db"
        vectorstore = QdrantVectorStore.from_existing_collection(
            embedding=embedding_model,
            path=str(db_path),
            collection_name="omnibrain"
        )

        retriever = vectorstore.as_retriever(search_kwargs={"k": k})

    return retriever

def searchDocuments(query, k=5):
    return getRetriever(k).invoke(query)