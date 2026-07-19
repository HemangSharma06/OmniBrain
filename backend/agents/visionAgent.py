from backend.llm.llm import runAgentChain
from backend.llm.prompt import vision_prompt

def vision_agent(state: dict) -> dict:
    print("\n📊 [Vision Agent]: Processing visual charts/tables context...")
    user_query = state.get("query", "")
    
    image_context = state.get("image_data", "No raw image byte layout provided.")
    
    vision_analysis = runAgentChain(vision_prompt, {"question": user_query})
    
    return {"context": [vision_analysis]}