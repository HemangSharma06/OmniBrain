from pathlib import Path
from qdrant_client import QdrantClient


project_root = Path(__file__).resolve().parents[2]

db_path = project_root / "db" / "qdrant_db"


client = QdrantClient(
    path=str(db_path)
)