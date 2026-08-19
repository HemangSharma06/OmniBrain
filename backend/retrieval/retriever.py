import warnings
warnings.filterwarnings("ignore")
from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from backend.ingestion.qdrant import client

embedding_model = None
retriever = None

def getRetriever(k):

    global embedding_model, retriever, image_client
    if retriever is None:
        print("Loading Retriever...")
        # embedding_model = OpenAIEmbeddings(
        #     model="text-embedding-3-small"
        # )
        embedding_model = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5"
        )
        project_root = Path(__file__).resolve().parents[2]
        db_path = project_root / "db" / "qdrant_db"

        vectorstore = QdrantVectorStore(
            client=client,
            embedding=embedding_model,
            collection_name="omnibrain"
        )
        retriever = vectorstore.as_retriever(
            search_kwargs={"k": k}
        )
    return retriever

def searchDocuments(query, k=10):
    return getRetriever(k).invoke(query)

def searchImages(query_vector, k=3):

    results = client.query_points(
        collection_name="omnibrain_images",
        query=query_vector,
        limit=k
    )
    image_paths = []

    for point in results.points:
        image_paths.append(
            point.payload["path"]
        )
    return image_paths