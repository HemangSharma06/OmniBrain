import warnings
warnings.filterwarnings("ignore")

from pathlib import Path

from backend.ingestion.docsIngestion import loadWordDocuments
from backend.ingestion.pdfIngestion import loadPdfDocuments
from backend.ingestion.textIngestion import loadTextDocuments
from backend.ingestion.imageIngestion import load_images
from backend.ingestion.tableIngestion import loadTabularDocuments
from backend.ingestion.chunking import split_documents
from backend.ingestion.VectorDB import createVectorStore

from chunking import split_documents
from VectorDB import createVectorStore
from qdrant_client import QdrantClient


def main():
    project_root = Path(__file__).resolve().parents[2]
    db_path = project_root / "db" / "qdrant_db"
    client = QdrantClient(
        path=db_path
    )
    print("=" * 60)
    print("          OmniBrain Ingestion Pipeline")
    print("=" * 60)

    documents = []

    # Word Documents
    print("=" * 60)
    print("\nLoading Word Documents...")
    print("=" * 60)
    documents.extend(
        loadWordDocuments(str(project_root / "data" / "docs"))
    )

    # PDF Documents
    print("=" * 60)
    print("\nLoading PDF Documents...")
    print("=" * 60)
    documents.extend(
        loadPdfDocuments(str(project_root / "data" / "pdf"))
    )

    # Text Documents
    print("=" * 60)
    print("\nLoading Text Documents...")
    print("=" * 60)
    documents.extend(
        loadTextDocuments(str(project_root / "data" / "text"))
    )

    # Images
    print("=" * 60)
    print("\nLoading Images...")
    print("=" * 60)
    documents.extend(
        load_images(str(project_root / "data" / "images"))
    )
 
    # CSV / Excel
    print("=" * 60)
    print("\nLoading Tabular Documents...")
    print("=" * 60)
    documents.extend(
        loadTabularDocuments(str(project_root / "data" / "tabular"))
    )

    print(f"\nTotal Documents Loaded : {len(documents)}")

    # vlm
    print("="*60)
    print("\nLoading Vision Documents...")
    print("="*60)
    documents.extend(
        load_images(str(project_root / "data" / "images"))
    )
    
    # Chunking
    print("=" * 60)
    print("\nChunking Documents...")
    print("=" * 60)
    chunks = split_documents(documents)

    print(f"Total Chunks Created : {len(chunks)}")

    # Vector Store
    print("=" * 60)
    print("\nCreating Vector Store...")
    print("=" * 60)
    createVectorStore(chunks, client)

    print("=" * 60)
    print("\nIngestion Pipeline Completed Successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()