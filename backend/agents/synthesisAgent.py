from backend.llm.llm import runAgentChain
from backend.llm.prompt import synthesis_prompt


def synthesis_agent(state: dict) -> dict:
    print("\n[Synthesis Agent]: Combining findings into final memo...")

    user_query = state.get("query", "").strip()

    text_context = state.get("context", [])
    vision_context = state.get("vision_context", [])

    combined_context = "\n\n".join(text_context + vision_context)

    if not combined_context:
        return {
            "answer": "I don't have enough information to answer this question."
        }

    final_answer = runAgentChain(
        synthesis_prompt,
        {
            "question": user_query,
            "context": combined_context
        }
    ).strip()

    return {
        "answer": final_answer
    }