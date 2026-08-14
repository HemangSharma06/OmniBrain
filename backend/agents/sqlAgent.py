import os
from urllib.parse import quote_plus
from backend.llm.llm import runAgentChain
from backend.llm.prompt import sql_prompt
from langchain_community.utilities import SQLDatabase
import time

DB_URL = os.getenv("DB_URL")
if not DB_URL:
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_PORT = os.getenv("DB_PORT")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_DATABASE = os.getenv("DB_DATABASE", "omnibrain")

    if DB_USER and DB_PASSWORD and DB_PORT:
        encoded_password = quote_plus(DB_PASSWORD)
        DB_URL = f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"

try:
    db = SQLDatabase.from_uri(DB_URL) if DB_URL else None
except Exception as exc:
    print(f"[SQL Agent]: Database initialization failed: {exc}")
    db = None

def sql_agent(state: dict) -> dict:
    print("\n[SQL Agent]: Inspecting PostgreSQL schema & generating query...")
    start = time.time()
    user_query = state.get("query", "").strip()

    if db is None:
        return {
            "sql_query": "",
            "sql_result": "SQL database is unavailable. Please verify DB_URL and PostgreSQL credentials.",
        }

    live_schema = db.get_table_info()
    columns = state.get("columns", [])
    table_name = state.get("table_name", "")
    print()
    print("-"*40)
    print(f"Table Name: {table_name}\n columns: {columns}")
    print("-"*40)
    generated_sql = runAgentChain(
        sql_prompt,
        {
            "question": user_query,
            "schema": live_schema,
            "table_name":table_name,
            "columns":columns
        }
    ).strip()

    clean_sql = generated_sql.replace("```sql", "").replace("```", "").strip()
    print(f"[SQL Agent]: Generated SQL Query -> {clean_sql}")

    # Safety: block destructive statements unless explicitly allowed
    destructive = ["DROP", "DELETE", "TRUNCATE", "UPDATE", "INSERT", "ALTER", "CREATE", "GRANT", "REVOKE"]
    upper_sql = clean_sql.upper()
    if any(keyword in upper_sql for keyword in destructive):
        db_result = "Query blocked: destructive SQL statements are not allowed."
        print("[SQL Agent]: Blocked destructive SQL statement.")
    else:
        try:
            db_result = db.run(clean_sql)
            if not db_result:
                db_result = "Query executed successfully, but no matching records were found."
        except Exception as e:
            print(f"[SQL Agent Error]: {e}")
            db_result = "SQL Execution Error: An error occurred while executing the query."

    print("[SQL Agent]: PostgreSQL query execution finished.")
    
    print(f"\n|---- Time Taken = {time.time()-start : .2f} ----|")
    return {
        "sql_query": clean_sql,
        "sql_result": str(db_result),    
    }