from dotenv import load_dotenv
from backend.llm.prompt import rag_prompt 
from langchain_core.prompts import ChatPromptTemplate

from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_openai import ChatOpenAI

load_dotenv()

# Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    temperature=0
)

# openAI
# llm = ChatOpenAI(
#     model="gpt-4o-mini",
#     temperature=0
# )

chain = rag_prompt | llm

def generateAnswer(question, context):
    response = chain.invoke(
        {
            "question": question,
            "context": context
        }
    )
    content = response.content

    if isinstance(content, list):
        return "\n".join(
            block["text"]
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )

    return content