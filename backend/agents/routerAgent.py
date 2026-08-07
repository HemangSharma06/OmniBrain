from backend.llm.llm import getRouterDecision
from backend.llm.prompt import router_prompt
from backend.ingestion.tableIngestion import engine
from sqlalchemy import inspect
import time
def router_agent(state: dict) -> dict:
    start = time.time()
    print("\n[Router Agent]: Analyzing user intent...")

    user_query = state.get("query", "").strip()

    if not user_query:
        raise ValueError("Query not found in Agent State.")

    next_agent = getRouterDecision(user_query, router_prompt)

    # Safety fallback
    if next_agent not in ["SEARCH", "VISION", "SQL"]:
        next_agent = "SEARCH"

    print(f"\n[Router Agent]: Routing execution to -> {next_agent}")
    print(f"\n|---- Time Taken = {time.time()-start : .2f} ----|")
    
    return {
        "next_step": next_agent
    }