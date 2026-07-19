from backend.llm.llm import runAgentChain
from backend.llm.prompt import guardrails_prompt


def guardrails_agent(state: dict) -> dict:

    print("\n🛡️ [Guardrails Agent]: Running strict alignment verification...")

    context = state.get("context", [])
    answer = state.get("answer", "")

    if isinstance(context, list):
        context = "\n\n".join(context)

    validated_answer = runAgentChain(
        guardrails_prompt,
        {
            "context": context,
            "answer": answer,
        },
    )

    print("[Guardrails Agent]: Output verified successfully.")

    return {
        "final_response": validated_answer
    }