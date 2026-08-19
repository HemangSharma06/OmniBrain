from backend.llm.llm import runAgentChain
from backend.llm.prompt import guardrails_prompt
import time


def guardrails_agent(state: dict) -> dict:
    print("\n[Guardrails Agent]: Validating final answer against retrieved evidence...")
    start = time.time()

    question = state.get("query", "").strip()
    answer = state.get("answer", "").strip()

    text_context = state.get("context", [])
    vision_context = state.get("vision_context", [])
    sql_context = state.get("sql_result", "")
    sql_query = state.get("sql_query", "")

    combined_context = "\n\n".join(text_context + vision_context)
    if sql_query:
        combined_context += "\n\nExecuted SQL Query:\n" + sql_query
    if sql_context:
        combined_context += "\n\nDatabase Result:\n" + sql_context
        
    print("\n========== GUARDRAILS DEBUG ==========")
    print("QUESTION:", question)
    print("ANSWER:", repr(answer))
    print("TEXT CONTEXT:", text_context)
    print("VISION CONTEXT:", vision_context)
    print("SQL QUERY:", sql_query)
    print("SQL RESULT:", sql_context)
    print("======================================")
    
    if not answer:
        final_response = "I don't have enough information to answer this question."
        return {
            "answer": final_response,
            "final_response": final_response
        }

    final_response = answer

    print(f"\n|---- Time Taken = {time.time()-start:.2f} ----|")
    return {
        "answer": final_response,
        "final_response": final_response
    }
