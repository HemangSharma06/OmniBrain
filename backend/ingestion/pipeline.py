import warnings
warnings.filterwarnings("ignore")

from pathlib import Path

from docsIngestion import loadWordDocuments
from pdfIngestion import loadPdfDocuments
from textIngestion import loadTextDocuments
from imageIngestion import loadImageDocuments
from tableIngestion import loadTabularDocuments

from chunking import split_documents
from VectorDB import createVectorStore


def main():

    print("=" * 60)
    print("          OmniBrain Ingestion Pipeline")
    print("=" * 60)

    project_root = Path(__file__).resolve().parents[2]

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
        loadImageDocuments(str(project_root / "data" / "images"))
    )

    # CSV / Excel
    print("=" * 60)
    print("\nLoading Tabular Documents...")
    print("=" * 60)
    documents.extend(
        loadTabularDocuments(str(project_root / "data" / "tabular"))
    )

    print(f"\nTotal Documents Loaded : {len(documents)}")

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
    createVectorStore(chunks)

    print("=" * 60)
    print("\nIngestion Pipeline Completed Successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()