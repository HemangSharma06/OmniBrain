import os
from backend.llm.llm import runAgentChain
from backend.llm.prompt import sql_prompt
from langchain_community.utilities import SQLDatabase

DB_URL = os.getenv("DB_URL")
if not DB_URL:
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_PORT = os.getenv("DB_PORT")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_DATABASE = os.getenv("DB_DATABASE", "omnibrain")

    if not DB_PASSWORD or not DB_USER or not DB_PORT:
        raise ValueError(
            "CRITICAL: Missing Database Credentials! "
            "Please check DB_URL or DB_USER / DB_PASSWORD / DB_HOST env variables."
        )
        
    DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"

db = SQLDatabase.from_uri(DB_URL)

def sql_agent(state: dict) -> dict:
    print("\n[SQL Agent]: Inspecting PostgreSQL schema & generating query...")

    user_query = state.get("query", "").strip()

    live_schema = db.get_table_info()

    generated_sql = runAgentChain(
        sql_prompt,
        {
            "question": user_query,
            "schema": live_schema
        }
    ).strip()

    clean_sql = generated_sql.replace("```sql", "").replace("```", "").strip()
    print(f"[SQL Agent]: Generated SQL Query -> {clean_sql}")

    try:
        db_result = db.run(clean_sql)
        if not db_result:
            db_result = "Query executed successfully, but no matching records were found."
    except Exception as e:
        print(f"[SQL Agent Error]: {e}")
        db_result = f"SQL Execution Error: {str(e)}"

    print("[SQL Agent]: PostgreSQL query execution finished.")

    return {
        "sql_query": clean_sql,
        "sql_result": str(db_result),
        "context": [f"Database Query Output:\n{db_result}"]
    }