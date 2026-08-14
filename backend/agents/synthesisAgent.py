from backend.llm.llm import runAgentChain
from backend.llm.prompt import synthesis_prompt
import time

def synthesis_agent(state: dict) -> dict:
    print("\n[Synthesis Agent]: Combining findings into final memo...")
    start = time.time()

    user_query = state.get("query", "").strip()

    text_context = state.get("context", [])
    vision_context = state.get("vision_context", [])
    sql_context = state.get("sql_result", "")
    sql_query = state.get("sql_query", "")

    combined_context = "\n\n".join(text_context + vision_context)

    if sql_query:
        combined_context += "\n\nExecuted SQL Query:\n" + sql_query

    if sql_context:
        combined_context += "\n\nDatabase Result:\n" + sql_context

    if not combined_context:
        return {
            "answer": "I don't have enough information to answer this question."
        }

    print(f"\nCombined Context Characters: {len(combined_context)}")
    print(f"Combined Context Words: {len(combined_context.split())}")

    final_answer = runAgentChain(
        synthesis_prompt,
        {
            "question": user_query,
            "context": combined_context
        }
    ).strip()
    print(f"\n|---- Time Taken = {time.time()-start:.2f} ----|")
    return {
        "answer": final_answer
    }