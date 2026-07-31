from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_openai import OpenAIEmbeddings

from langchain_qdrant import QdrantVectorStore
from qdrant_client.models import VectorParams, Distance, PointStruct
import uuid

def createVectorStore(chunks, client):

    if not client.collection_exists("omnibrain"):
        client.create_collection(
            collection_name="omnibrain",
            vectors_config=VectorParams(
                size=384,
                distance=Distance.COSINE
            )
        )

    # Embedding Model
    embedding_model = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5"
    )

    # embedding_model = OpenAIEmbeddings(
    #     model="text-embedding-3-small"
    # )

    vectorstore = QdrantVectorStore(
        embedding=embedding_model,
        client=client,
        collection_name="omnibrain"
    )

    vectorstore.add_documents(chunks)

    return vectorstore



def createImageVectorStore(image_vectors, client):

    collection = "omnibrain_images"
    if not client.collection_exists(collection):
        client.create_collection(
            collection_name=collection,
            vectors_config=VectorParams(
                size=512,
                distance=Distance.COSINE
            )
        )

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=image["embedding"],
            payload={
                "path": image["path"],
                "type": "image"
            }
        )
        for image in image_vectors
    ]
    client.upsert(
        collection_name=collection,
        points=points
    )
    return True