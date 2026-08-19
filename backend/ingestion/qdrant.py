from pathlib import Path
from qdrant_client import QdrantClient


project_root = Path(__file__).resolve().parents[2]

db_path = project_root / "db" / "qdrant_db"


class SafeQdrantClient:
    """Lazy Qdrant wrapper so the real client is not created at import time."""

    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._client = None

    def _get_client(self):
        if self._client is None:
            self._client = QdrantClient(*self._args, **self._kwargs)
        return self._client

    def __getattr__(self, name):
        if self._client is None:
            self._client = QdrantClient(*self._args, **self._kwargs)
        return getattr(self._client, name)

    def close(self):
        try:
            if self._client is not None:
                self._client.close()
        except Exception:
            pass
        finally:
            self._client = None

    def __del__(self):
        try:
            if self._client is not None:
                self._client.close()
        except Exception:
            pass


client = SafeQdrantClient(
    path=str(db_path)
)