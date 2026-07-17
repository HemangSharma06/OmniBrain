import os
import warnings
warnings.filterwarnings('ignore')
from chunking import split_documents
from pathlib import Path

import pandas as pd
from langchain_core.documents import Document
# from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from dotenv import load_dotenv

load_dotenv()

# Loading
def loadTabularDocuments(documentPath):

    if not os.path.exists(documentPath):
        raise FileNotFoundError(f"Path not found in the System: {documentPath}")

    documents = []

    for file in os.listdir(documentPath):

        file_path = os.path.join(documentPath, file)

        # CSV Files
        if file.lower().endswith(".csv"):

            df = pd.read_csv(file_path)

            documents.append(
                Document(
                    page_content=df.to_string(index=False),
                    metadata={
                        "source": file_path,
                        "type": "csv"
                    }
                )
            )

        # Excel Files
        elif file.lower().endswith((".xlsx", ".xls")):

            excel = pd.ExcelFile(file_path)

            for sheet in excel.sheet_names:

                df = pd.read_excel(file_path, sheet_name=sheet)

                documents.append(
                    Document(
                        page_content=df.to_string(index=False),
                        metadata={
                            "source": file_path,
                            "sheet": sheet,
                            "type": "excel"
                        }
                    )
                )

    if not documents:
        raise FileNotFoundError("No CSV or Excel files found in the directory")

    for i, document in enumerate(documents):
        print(f"\nDocument: {i+1}")
        print(f"Source: {document.metadata['source']}")
        print(f"Content Length: {len(document.page_content)}")
        print(f"Content Preview: {document.page_content[:100]}")
        print(f"Metadata: {document.metadata}")

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
        collection_metadata={"hnsw:space": "cosine"}
    )

    return vectorStore


def main():

    print("Main Function")

    project_root = Path(__file__).resolve().parents[2]
    path = project_root / "data" / "tabular"

    # 1. Loading Files
    documents = loadTabularDocuments(str(path))

    # 2. Chunking Files
    chunks = split_documents(documents)

    # 3. Embedding and Storing in Vector DB
    vectorspace = createVectorStore(chunks)


if __name__ == "__main__":
    main()