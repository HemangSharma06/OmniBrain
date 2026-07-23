"""Configuration values for the OmniBrain Streamlit client."""

import os


FASTAPI_BASE_URL = os.getenv("OMNIBRAIN_API_URL", "http://localhost:8000").rstrip("/")
API_TIMEOUT_SECONDS = float(os.getenv("OMNIBRAIN_API_TIMEOUT", "60"))
SUPPORTED_FILE_TYPES = ["pdf", "docx", "txt", "png", "jpg", "jpeg", "csv", "xlsx"]