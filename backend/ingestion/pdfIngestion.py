import os
import warnings
warnings.filterwarnings('ignore')

from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from backend.vision.imageExtractor import extract_pdf_images
from dotenv import load_dotenv

load_dotenv()

# Loading
def loadPdfDocuments(DocumentPath):
    if not os.path.exists(DocumentPath):
        raise FileNotFoundError(f"Path not found in the System {DocumentPath}")
    loader = DirectoryLoader(
        path=DocumentPath,
        glob="*.pdf",
        loader_cls=PyPDFLoader
    )
    
    documents = loader.load()
    
    pdf_files = set()
    
    if not len(documents):
        raise FileNotFoundError("No file found in the directory")
    
    for i, document in enumerate(documents):
        pdf_files.add(document.metadata["source"])
        print(f"\nDocument: {i+1}")
        print(f"Source: {document.metadata.get('source', 'Unknown')}")
        print(f"Content Length: {len(document.page_content)}")
        print(f"Content Preview: {document.page_content[:100]}")
        print(f"Metadata: {document.metadata}")
    
    images = []
    for pdf_path in pdf_files:
        pdf_name = os.path.splitext(
            os.path.basename(pdf_path)
        )[0]
        image_folder = os.path.join(
            "temp",
            "pdf_images",
            pdf_name
        )
        image = extract_pdf_images(
            pdf_path,
            image_folder
        )
        images.extend(image)
    print("=" * 60)
    print(images)
    print("=" * 60)
    
    return documents, images
