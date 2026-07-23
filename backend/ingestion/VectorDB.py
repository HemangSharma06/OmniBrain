from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client.models import VectorParams, Distance

def createVectorStore(chunks, client):
    from qdrant_client.http.exceptions import UnexpectedResponse

    if not client.collection_exists("omnibrain"):
        client.create_collection(
            collection_name="omnibrain",
            vectors_config=VectorParams(
                size=384,
                distance=Distance.COSINE
            )
        )
        
    embedding_model = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5"
    )
    # Embedding Model
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
    