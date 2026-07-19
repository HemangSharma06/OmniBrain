from langgraph.graph import StateGraph, END
from backend.graph.state import AgentState
from backend.graph.nodes import (
    router_node,
    search_node,
    vision_node,
    sql_node,
    synthesis_node,
    guardrails_node
)

workflow = StateGraph(AgentState)

workflow.add_node("router", router_node)
workflow.add_node("search", search_node)
workflow.add_node("vision", vision_node)
workflow.add_node("sql", sql_node)
workflow.add_node("synthesis", synthesis_node)
workflow.add_node("guardrails", guardrails_node)

workflow.set_entry_point("router")

def route_to_agent(state):
    next_agent = state.get("next_step", "").upper()
    if next_agent == "SEARCH":
        return "search"
    elif next_agent == "VISION":
        return "vision"
    elif next_agent == "SQL":
        return "sql"
    else:
        return END  
workflow.add_conditional_edges(
    "router",
    route_to_agent,
    {
        "search": "search",
        "vision": "vision",
        "sql": "sql",
    }
)

workflow.add_edge("search", "synthesis")
workflow.add_edge("vision", "synthesis")
workflow.add_edge("sql", "synthesis")

workflow.add_edge("synthesis", "guardrails")
workflow.add_edge("guardrails", END)

# Graph
app = workflow.compile()