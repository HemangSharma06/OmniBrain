from backend.agents.routerAgent import router_agent
from backend.agents.searchAgent import search_agent
from backend.agents.visionAgent import vision_agent
from backend.agents.sqlAgent import sql_agent
from backend.agents.synthesisAgent import synthesis_agent
from backend.agents.guardRailsAgent import guardrails_agent

# 1. Router Node
def router_node(state):
    return router_agent(state)

# 2. Search Node
def search_node(state):
    return search_agent(state)

# 3. Vision Node
def vision_node(state):
    return vision_agent(state)

# 4. SQL Node
def sql_node(state):
    return sql_agent(state)

# 5. Synthesis Node
def synthesis_node(state):
    return synthesis_agent(state)

# 6. Guardrails Node
def guardrails_node(state):
    return guardrails_agent(state)