from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

def createVectorStore(chunks, client):

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
    