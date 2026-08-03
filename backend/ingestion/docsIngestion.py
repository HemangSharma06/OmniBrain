import os
import warnings
warnings.filterwarnings('ignore')

from langchain_community.document_loaders import Docx2txtLoader, DirectoryLoader
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from backend.vision.imageExtractor import extract_docx_images
from dotenv import load_dotenv

load_dotenv()

# Loading
def loadWordDocuments(DocumentPath):
    if not os.path.exists(DocumentPath):
        raise FileNotFoundError(f"Path not found in the System {DocumentPath}")
    loader_docx = DirectoryLoader(
        path=DocumentPath,
        glob="**/*.docx",
        loader_cls=Docx2txtLoader
    )
    documents = loader_docx.load()
    
    loader_doc = DirectoryLoader(
        path=DocumentPath,
        glob="**/*.doc",
        loader_cls=UnstructuredWordDocumentLoader
    )
    documents.extend(loader_doc.load())
    
    document_files = set()
    
    if not len(documents):
        raise FileNotFoundError("No file found in the directory")
    
    for i, document in enumerate(documents):
        document_files.add(document.metadata["source"])
        print(f"\nDocument: {i+1}")
        print(f"Source: {document.metadata.get('source', 'Unknown')}")
        print(f"Content Length: {len(document.page_content)}")
        print(f"Content Preview: {document.page_content[:100]}")
        print(f"Metadata: {document.metadata}")
    
    images = []

    for document in document_files:

        image = extract_docx_images(
            document,
            "temp/docx_images"
        )

        images.extend(image)
    
    return documents, images