from backend.llm.llm import getRouterDecision
from backend.llm.prompt import router_prompt

def router_agent(state: dict) -> dict:
    print("\n[Router Agent]: Analyzing user intent...")
    
    user_query = state.get("query", "")
    
    if not user_query:
        raise ValueError("Query not found in Agent State.")
        
    next_agent = getRouterDecision(user_query, router_prompt)
    
    print(f"🎯 [Router Agent]: Routing execution to -> {next_agent}")
    return {"next_step": next_agent}