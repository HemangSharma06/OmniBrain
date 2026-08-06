from pathlib import Path
import sys
import os
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import text, inspect

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)

project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

from backend.graph.graph import app as rag_graph
from backend.ingestion.docsIngestion import loadWordDocuments
from backend.ingestion.pdfIngestion import loadPdfDocuments
from backend.ingestion.textIngestion import loadTextDocuments
from backend.ingestion.imageIngestion import load_images
from backend.ingestion.tableIngestion import loadTabularDocuments
from backend.ingestion.chunking import split_documents
from backend.ingestion.VectorDB import createVectorStore, createImageVectorStore
from backend.ingestion.qdrant import client
from backend.Database.db import engine
from backend.vision.clip import get_image_embedding

from backend.auth.models import create_users_table
from backend.auth.auth import get_current_user
from backend.auth.schemas import UserOut
from backend.auth.router import router as auth_router

app = FastAPI(
    title="OmniBrain API",
    version="1.0.0",
    description="Multimodal RAG assistant with JWT-protected endpoints.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the auth router at /auth prefix
app.include_router(auth_router, prefix="/auth")

# Create users table on startup if a database is available.
# Do not fail the entire application when Postgres is absent or unreachable.
try:
    create_users_table()
    logger.info("OmniBrain API started. Users table verified.")
except Exception as exc:
    logger.warning("OmniBrain API started without database-backed auth bootstrap: %s", exc)

class QueryRequest(BaseModel):
    query: str

@app.get("/")
async def home():
    return {
        "message": "OmniBrain API Running"
    }

@app.post("/query")
async def query(
    request: QueryRequest,
    current_user: UserOut = Depends(get_current_user),
):
    table_name = ""
    columns = []

    if engine is not None:
        try:
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
        except Exception as exc:
            logger.warning("Query endpoint could not read uploaded table metadata: %s", exc)

    inputs = {
        "query": request.query,
        "messages": [],
        "next_step": "",
        "context": [],
        "documents": [],
        "sources": [],
        "table_name": table_name,
        "columns": columns,
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
            images = []
            dir_path = os.path.dirname(file_str_path)
            if suffix == ".pdf":
                docs, imgs = loadPdfDocuments(dir_path)
                documents.extend(docs)
                images.extend(imgs)

            elif suffix in [".doc", ".docx"]:
                docs, imgs = loadWordDocuments(dir_path)
                documents.extend(docs)
                images.extend(imgs)

            elif suffix == ".txt":
                documents.extend(loadTextDocuments(dir_path))

            elif suffix in [".png", ".jpg", ".jpeg"]:
                documents.extend(load_images(dir_path))
                images.append(file_str_path)

            else:
                raise ValueError(f"Unsupported file type: {suffix}")
            
            if documents:
                print("\nDocuments Ingestion")
                chunks = split_documents(documents)
                createVectorStore(chunks, client)
                print(f"✅Documents of {filepath.name} chunked and ingested into Qdrant VectorDB.")
                
            if images:
                print("\nImages Ingestion")
                image_vectors = []

                for image_path in images:
                    vector = get_image_embedding(image_path)
                    image_vectors.append(
                        {
                            "path": image_path,
                            "embedding": vector
                        }
                    )

                createImageVectorStore(image_vectors,client)
                print(f"✅Images in {filepath.name} chunked and ingested into Qdrant VectorDB.")

    finally:
        if filepath.exists():
            filepath.unlink()
            print(f"{filepath.name} removed from temp storage.")


@app.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: UserOut = Depends(get_current_user),
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