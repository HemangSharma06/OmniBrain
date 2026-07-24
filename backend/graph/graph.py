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


# Router Decision
def router_decision(state):

    next_step = state.get("next_step", "").upper()

    if next_step == "SEARCH":
        return "search"

    elif next_step == "VISION":
        return "vision"

    elif next_step == "SQL":
        return "sql"

    return "search"


workflow.add_conditional_edges(
    "router",
    router_decision,
    {
        "search": "search",
        "vision": "vision",
        "sql": "sql"
    }
)


# After Search decide whether Vision is needed
def after_search(state):

    image_paths = state.get("image_paths", [])

    if image_paths:
        return "vision"

    return "synthesis"


workflow.add_conditional_edges(
    "search",
    after_search,
    {
        "vision": "vision",
        "synthesis": "synthesis"
    }
)


workflow.add_edge("vision", "synthesis")
workflow.add_edge("sql", "synthesis")
workflow.add_edge("synthesis", "guardrails")
workflow.add_edge("guardrails", END)

app = workflow.compile()