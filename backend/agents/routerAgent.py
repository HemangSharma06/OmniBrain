from backend.llm.llm import getRouterDecision
from backend.llm.prompt import router_prompt
from backend.ingestion.tableIngestion import engine
from sqlalchemy import inspect

def has_active_tables() -> bool:
    """Check if PostgreSQL has user-uploaded data tables."""
    if not engine:
        return False
    try:
        inspector = inspect(engine)
        tables = [t for t in inspector.get_table_names() if t != "uploaded_files_metadata"]
        return len(tables) > 0
    except Exception:
        return False

def router_agent(state: dict) -> dict:
    print("\n[Router Agent]: Analyzing user intent...")

    user_query = state.get("query", "").strip()

    if not user_query:
        raise ValueError("Query not found in Agent State.")

    # Rule-based fallback
    sql_keywords = ["count", "show", "list", "top", "average", "avg", "total", "sum", "customer", "rows", "table", "data"]
    if has_active_tables() and any(kw in user_query.lower() for kw in sql_keywords):
        print("[Router Agent]: Active database tables & SQL intent detected -> Routing directly to SQL")
        return {"next_step": "SQL"}

    next_agent = getRouterDecision(user_query, router_prompt)

    # Safety fallback
    if next_agent not in ["SEARCH", "VISION", "SQL"]:
        next_agent = "SEARCH"

    print(f"[Router Agent]: Routing execution to -> {next_agent}")

    return {
        "next_step": next_agent
    }