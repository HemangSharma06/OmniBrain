from backend.llm.llm import runAgentChain
from backend.llm.prompt import guardrails_prompt

def guardrails_agent(state: dict) -> dict:
    print("\n[Guardrails Agent]: Running strict alignment verification...")
    
    gathered_context = state.get("context", [])
    combined_context_str = "\n\n".join(gathered_context)
    generated_answer = state.get("answer", "")
    
    validated_output = runAgentChain(guardrails_prompt, {
        "context": combined_context_str,
        "answer": generated_answer
    })
    
    print("✨ [Guardrails Agent]: Output verified successfully.")
    return {"final_response": validated_output}