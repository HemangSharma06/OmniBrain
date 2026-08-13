# backend/db/db.py
import os
from urllib.parse import quote_plus, unquote
from sqlalchemy import create_engine
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL")
if not DB_URL:
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME") or os.getenv("DB_DATABASE", "omnibrain")

    if DB_USER and DB_PASSWORD:
        normalized_password = unquote(DB_PASSWORD)
        encoded_password = quote_plus(normalized_password)
        DB_URL = f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLAlchemy Engine
engine = create_engine(DB_URL) if DB_URL else None