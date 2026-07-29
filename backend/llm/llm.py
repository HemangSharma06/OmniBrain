from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama
# from langchain_openai import ChatOpenAI

load_dotenv()

# OLLAMA
base_llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0,
    num_predict=512,
    keep_alive=-1,
    num_ctx=4096
)

vision_base_llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0
)

# OpenAI
# base_llm = ChatOpenAI(
#     model="gpt-4.1-mini",
#     temperature=0,
# )
llm = base_llm.with_retry(
    stop_after_attempt=5,
    wait_exponential_jitter=True
)

# FOR VISION AGENT
# vision_llm = ChatOpenAI(
#     model="gpt-4.1-mini",
#     temperature=0
# )

vision_llm = vision_base_llm.with_retry(
    stop_after_attempt=5,
    wait_exponential_jitter=True
)

# Router Schema
class RouteDecision(BaseModel):
    next_agent: str = Field(
        description="The next agent to route to: SEARCH, VISION or SQL"
    )
# Router
def getRouterDecision(question, prompt_template):

    prompt = prompt_template.format(question=question)

    print("=" * 80)
    print(prompt)
    print("=" * 80)

    response = base_llm.invoke(prompt)

    print("RAW LLM:")
    print(response.content)

    return response.content.strip().upper()


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