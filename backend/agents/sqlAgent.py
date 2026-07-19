from backend.llm.llm import runAgentChain
from backend.llm.prompt import sql_prompt

def sql_agent(state: dict) -> dict:
    print("\n[SQL Agent]: Synthesizing structured DB query...")
    user_query = state.get("query", "")
    
    generated_sql = runAgentChain(sql_prompt, {"question": user_query})
    print(f"⚙️ [SQL Agent]: Generated Query -> {generated_sql}")
    
    # db_result = execute_sql_query(generated_sql)
    db_result = f"Mock DB Result for query: {generated_sql}" 
    
    return {"context": [db_result]}