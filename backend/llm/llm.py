from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    temperature=0
)

class RouteDecision(BaseModel):
    next_agent: str = Field(description="The next agent to route to: 'SEARCH', 'VISION', or 'SQL'")

router_llm = llm.with_structured_output(RouteDecision)

def getRouterDecision(question, prompt_template):
    chain = prompt_template | router_llm
    response = chain.invoke({"question": question})
    return response.next_agent.strip().upper()

def runAgentChain(prompt_template, input_variables: dict) -> str:
    chain = prompt_template | llm
    response = chain.invoke(input_variables)
    content = response.content

    if isinstance(content, list):
        return "\n".join(
            block["text"]
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return str(content).strip()