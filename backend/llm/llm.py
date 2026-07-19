from dotenv import load_dotenv

from pydantic import BaseModel, Field

from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_openai import ChatOpenAI

load_dotenv()

# Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    temperature=0
)
vision_llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    temperature=0
)

# OpenAI
# llm = ChatOpenAI(
#     model="gpt-4.1-mini",
#     temperature=0
# )
# vision_llm = ChatOpenAI(
#     model="gpt-4.1-mini",
#     temperature=0
# )

# Router Schema
class RouteDecision(BaseModel):
    next_agent: str = Field(
        description="The next agent to route to: SEARCH, VISION or SQL"
    )


router_llm = llm.with_structured_output(RouteDecision)

# Router
def getRouterDecision(question, prompt_template):

    chain = prompt_template | router_llm

    response = chain.invoke({
        "question": question
    })

    return response.next_agent.strip().upper()


# Generic LLM Chain
def runAgentChain(prompt_template, variables):

    chain = prompt_template | llm

    response = chain.invoke(variables)

    if hasattr(response, "content"):

        if isinstance(response.content, list):

            text = []

            for block in response.content:

                if (
                    isinstance(block, dict)
                    and block.get("type") == "text"
                ):
                    text.append(block["text"])

            return "\n".join(text).strip()

        return str(response.content).strip()

    return str(response).strip()