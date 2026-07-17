from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from pathlib import Path

def createVectorStore(chunks):

    embedding_model = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5"
    )
    # Embedding Model
    # embedding_model = OpenAIEmbeddings(
    #     model="text-embedding-3-small"
    # )
    
    project_root = Path(__file__).resolve().parents[2]
    db_path = project_root / "db" / "qdrant_db"

    vectorstore = QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=embedding_model,
        path=str(db_path),
        collection_name="omnibrain"
    )

    return vectorstore
    