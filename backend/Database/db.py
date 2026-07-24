# backend/db/db.py
import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def execute_sql_query(sql_query: str) -> str:
    """
    Executes the generated SQL query on PostgreSQL database and returns result as string.
    """
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME", "omnibrain"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "password"),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432")
        )
        
        df = pd.read_sql_query(sql_query, conn)
        conn.close()

        if df.empty:
            return "No records found matching the query."

        return df.to_string(index=False)

    except Exception as e:
        return f"Error executing SQL query: {str(e)}"