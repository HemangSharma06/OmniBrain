from backend.llm.llm import runAgentChain
from backend.llm.prompt import sql_prompt


def sql_agent(state: dict) -> dict:
    print("\n[SQL Agent]: Generating SQL query...")

    user_query = state.get("query", "").strip()

    generated_sql = runAgentChain(
        sql_prompt,
        {"question": user_query}
    ).strip()

    print(f"[SQL Agent]: Generated SQL -> {generated_sql}")

    # Future:
    # db_result = execute_sql_query(generated_sql)

    db_result = f"Mock DB Result:\n{generated_sql}"

    return {
        "sql_query": generated_sql,
        "sql_result": db_result,
        "context": [db_result]
    }