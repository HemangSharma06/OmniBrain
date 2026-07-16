import os
import warnings
warnings.filterwarnings('ignore')
from chunking import split_documents
from pathlib import Path

import easyocr
from langchain_core.documents import Document
# from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from dotenv import load_dotenv

load_dotenv()

# Loading
def loadImageDocuments(document_path):

    if not os.path.exists(document_path):
        raise FileNotFoundError(f"Path not found in the System: {document_path}")
    reader = easyocr.Reader(['en'], gpu=False)
    documents = []
    for file in os.listdir(document_path):
        if file.lower().endswith((".png", ".jpg", ".jpeg")):

            image_path = os.path.join(document_path, file)
            result = reader.readtext(image_path, detail=0)
            text = "\n".join(result)
            documents.append(
                Document(
                    page_content=text,
                    metadata={"source": image_path}
                )
            )
    if not documents:
        raise FileNotFoundError("No image files found in the directory")

    return documents

# Vector Database
def createVectorStore(chunks):
    print("Creating embeddings and storing in vectorDB")
    project_root = Path(__file__).resolve().parents[2]
    dir = project_root / "db" / "chroma_db"
    # Embedding Model
    # embedding_model = OpenAIEmbeddings(
    #     model="text-embedding-3-small"
    # )

    embedding_model = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5"
    )
    vectorStore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=dir,
        collection_metadata={"hnsw:space" : "cosine"}
    )
    return vectorStore

def main():
    print("Main Function")

    project_root = Path(__file__).resolve().parents[2]
    path = project_root / "data" / "images"

    # 1. Loading Files
    documents = loadImageDocuments(str(path))

    # 2. Chunking Files
    chunks = split_documents(documents)

    # 3. Embedding and Storing in vector DB
    vectorspace = createVectorStore(chunks)

if __name__ == "__main__":
    main()