from pathlib import Path
import sys
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import text, inspect

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
from backend.Database.db import engine
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
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name
            FROM uploaded_files_metadata
            ORDER BY uploaded_at DESC
            LIMIT 1
        """)).fetchone()
        if result:
            table_name = result[0]
            inspector = inspect(engine)
            columns = [
                col["name"]
                for col in inspector.get_columns(table_name)
            ]
    inputs = {
        "query": request.query,
        "messages": [],
        "next_step": "",
        "context": [],
        "documents": [],
        "sources": [],
        "table_name" : table_name,
        "columns" : columns,
        "image_paths": [],
        "sql_query": "",
        "sql_result": "",
        "answer": ""
    }

    result = rag_graph.invoke(inputs)

    return {
        "answer": result.get("answer"),
        "sources": result.get("sources"),
        "documents": result.get("documents"),
        "images": result.get("image_paths")
    }

UPLOAD_DIR = project_root / "data" / "temp_uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def process_document(filepath: str):
    filepath = Path(filepath)
    file_str_path = str(filepath)
    suffix = filepath.suffix.lower()

    try:
        # ROUTE A: TABULAR DATA (.csv, .xlsx, .xls) -> PostgreSQL ONLY
        if suffix in [".csv", ".xlsx", ".xls"]:
            print(f"Processing Tabular File for PostgreSQL: {filepath.name}")
            table_name = loadTabularDocuments(file_str_path)
            print(f"Ingested into Postgres Table: '{table_name}'")

        # ROUTE B: UNSTRUCTURED DATA -> Chunking -> Qdrant Vector DB
        else:
            documents = []
            dir_path = os.path.dirname(file_str_path)
            if suffix == ".pdf":
                documents.extend(loadPdfDocuments(dir_path))

            elif suffix in [".doc", ".docx"]:
                documents.extend(loadWordDocuments(dir_path))

            elif suffix == ".txt":
                documents.extend(loadTextDocuments(dir_path))

            elif suffix in [".png", ".jpg", ".jpeg"]:
                documents.extend(load_images(dir_path))
                documents.extend(loadVisionDocuments(dir_path))

            else:
                raise ValueError(f"Unsupported file type: {suffix}")

            if documents:
                chunks = split_documents(documents)

                client = QdrantClient(
                    path=str(project_root / "db" / "qdrant_db")
                )

                createVectorStore(chunks, client)
                print(f"✅ {filepath.name} chunked and ingested into Qdrant VectorDB.")

    finally:
        if filepath.exists():
            filepath.unlink()
            print(f"{filepath.name} removed from temp storage.")


@app.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    try:
        original_path = Path(file.filename)
        stem = original_path.stem
        ext = original_path.suffix

        # Format: filename_YYYY_MM_DD_HH_MM_SS.ext
        timestamp_str = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        timestamped_filename = f"{stem}_{timestamp_str}{ext}"

        save_path = UPLOAD_DIR / timestamped_filename

        with open(save_path, "wb") as f:
            f.write(await file.read())

        background_tasks.add_task(
            process_document,
            str(save_path)
        )

        return {
            "success": True,
            "message": "File uploaded successfully. Ingestion started.",
            "filename": file.filename,
            "saved_filename": timestamped_filename
        }

    except Exception as e:
        if 'save_path' in locals() and save_path.exists():
            save_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )