import os
import re
import hashlib
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

load_dotenv()

# Environment Credentials & DB URL Setup
DB_URL = os.getenv("DB_URL")
if not DB_URL:
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_DATABASE = os.getenv("DB_DATABASE", "omnibrain")

    if DB_USER and DB_PASSWORD:
        DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"

# SQLAlchemy Engine
engine = create_engine(DB_URL) if DB_URL else None


def hashFunction(filepath: str) -> str:
    """Memory-safe MD5 Hash calculation reading file in 8KB chunks."""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()


def ensure_metadata_table_exists():
    """Creates a tracking table in DB to store uploaded file hashes."""
    if not engine:
        return
        
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS uploaded_files_metadata (
                file_hash VARCHAR(32) PRIMARY KEY,
                file_name VARCHAR(255),
                table_name VARCHAR(255),
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))


def get_unique_table_name(base_table_name: str) -> str:
    """Ensures unique table name if a different file shares the same name."""
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    if base_table_name not in existing_tables:
        return base_table_name

    counter = 1
    new_table_name = f"{base_table_name}_{counter}"
    while new_table_name in existing_tables:
        counter += 1
        new_table_name = f"{base_table_name}_{counter}"

    return new_table_name


def loadTabularDocuments(filepath: str) -> str:
    if not engine:
        raise ValueError("Database engine is not configured.")
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Path not found in the System: {filepath}")
    
    filename = os.path.basename(filepath)
    file_hash = hashFunction(filepath)

    ensure_metadata_table_exists()

    # 1. Duplicate content check
    with engine.connect() as conn:
        query = text("SELECT table_name FROM uploaded_files_metadata WHERE file_hash = :hash")
        result = conn.execute(query, {"hash": file_hash}).fetchone()
        
        if result:
            existing_table = result[0]
            print(f"[DUPLICATE DETECTED] File content already exists in table '{existing_table}'. Skipping upload.")
            return existing_table

    # 2. Reading file first (Catch parsing errors BEFORE reserving table names)
    try:
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filepath.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(filepath)
        else:
            print(f"Unsupported tabular format: {filename}")
            return ""

        if df.empty:
            print(f"Warning: Uploaded file '{filename}' is empty.")
            return ""

        # Column names cleanup (spaces & special chars -> _, lowercase)
        df.columns = [
            re.sub(r'[^a-zA-Z0-9_]', '_', str(col)).lower().strip("_") 
            for col in df.columns
        ]

        # 3. Dynamic Base Name Creation & Uniqueness Check
        raw_table_name = re.sub(r'[^a-zA-Z0-9_]', '_', os.path.splitext(filename)[0]).lower().strip("_")
        
        if not raw_table_name:
            raw_table_name = "data_table"
            
        table_name = get_unique_table_name(raw_table_name)

        # 4. Save to Postgres
        df.to_sql(name=table_name, con=engine, if_exists="fail", index=False)

        # 5. Log metadata entry atomically
        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO uploaded_files_metadata (file_hash, file_name, table_name) 
                    VALUES (:hash, :fname, :tname) 
                    ON CONFLICT (file_hash) DO NOTHING
                """),
                {"hash": file_hash, "fname": filename, "tname": table_name}
            )

        print(f"Dynamic Postgres table created: '{table_name}' ({len(df)} rows)")
        return table_name

    except Exception as e:
        print(f"Ingestion Error for {filename}: {e}")
        return ""