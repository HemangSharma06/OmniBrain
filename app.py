from pathlib import Path
import sys
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil

project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

from backend.graph.graph import app as rag_graph
from backend.ingestion.docsIngestion import loadWordDocuments
from backend.ingestion.pdfIngestion import loadPdfDocuments
from backend.ingestion.textIngestion import loadTextDocuments
from backend.ingestion.imageIngestion import load_images
from backend.ingestion.tableIngestion import loadTabularDocuments
from backend.ingestion.visionIngestion import loadVisionDocuments
from backend.ingestion.chunking import split_documents
from backend.ingestion.VectorDB import createVectorStore
from qdrant_client import QdrantClient

app = FastAPI(
    title="OmniBrain API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

@app.get("/")
async def home():
    return {
        "message": "OmniBrain API Running"
    }

@app.post("/query")
async def query(request: QueryRequest):

    inputs = {
        "query": request.query,
        "messages": [],
        "next_step": "",
        "context": [],
        "documents": [],
        "sources": [],
        "image_paths": [],
        "sql_query": "",
        "sql_result": "",
        "answer": "",
        "final_response": ""
    }

    result = rag_graph.invoke(inputs)

    return {
        "answer": result.get("final_response"),
        "sources": result.get("sources"),
        "documents": result.get("documents"),
        "images": result.get("image_paths")
    }

UPLOAD_DIR = project_root / "data" / "temp_uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def process_document(filepath: str):

    filepath = Path(filepath)

    documents = []

    suffix = filepath.suffix.lower()

    if suffix == ".pdf":
        documents.extend(loadPdfDocuments(UPLOAD_DIR))

    elif suffix in [".doc", ".docx"]:
        documents.extend(loadWordDocuments(UPLOAD_DIR))

    elif suffix == ".txt":
        documents.extend(loadTextDocuments(UPLOAD_DIR))

    elif suffix in [".png", ".jpg", ".jpeg"]:
        documents.extend(load_images(UPLOAD_DIR))
        documents.extend(loadVisionDocuments(UPLOAD_DIR))

    elif suffix in [".csv", ".xlsx", ".xls"]:
        documents.extend(loadTabularDocuments(UPLOAD_DIR))

    else:
        raise ValueError(f"Unsupported file type: {suffix}")

    chunks = split_documents(documents)

    client = QdrantClient(
        path=project_root / "db" / "qdrant_db"
    )

    createVectorStore(chunks, client)
    print(f"{filepath.name} ingested successfully.")
    if filepath.exists():
        filepath.unlink()
        print(f"{filepath.name} removed from temp storage.")

@app.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    try:
        save_path = UPLOAD_DIR / file.filename

        with open(save_path, "wb") as f:
            f.write(await file.read())

        background_tasks.add_task(
            process_document,
            str(save_path)
        )

        return {
            "success": True,
            "message": "File uploaded successfully. Ingestion started.",
            "filename": file.filename
        }

    except Exception as e:

        if 'save_path' in locals() and save_path.exists():
            save_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )