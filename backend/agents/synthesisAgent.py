from backend.llm.llm import runAgentChain
from backend.llm.prompt import synthesis_prompt

def synthesis_agent(state: dict) -> dict:
    print("\n[Synthesis Agent]: Combining findings into final memo...")
    user_query = state.get("query", "")
    
    gathered_context = state.get("context", [])
    combined_context_str = "\n\n".join(gathered_context)
    
    final_draft = runAgentChain(synthesis_prompt, {
        "question": user_query,
        "context": combined_context_str
    })
    
    return {"answer": final_draft}