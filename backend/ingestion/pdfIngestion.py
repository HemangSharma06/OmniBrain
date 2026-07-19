import os
import warnings
warnings.filterwarnings('ignore')

from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader

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
    if not len(documents):
        raise FileNotFoundError("No file found in the directory")
    for i, document in enumerate(documents):
        print(f"\nDocument: {i+1}")
        print(f"Source: {document.metadata.get('source', 'Unknown')}")
        print(f"Content Length: {len(document.page_content)}")
        print(f"Content Preview: {document.page_content[:100]}")
        print(f"Metadata: {document.metadata}")
        
    return documents
