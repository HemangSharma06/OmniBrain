import operator
from typing import Annotated, Sequence
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage


class AgentState(TypedDict):

    # User Input
    query: str

    # Conversation History
    messages: Annotated[Sequence[BaseMessage], operator.add]

    # Router Decision
    next_step: str

    # Retrieved Context
    context: Annotated[list[str], operator.add]

    # Retrieved Documents
    documents: list

    # Sources
    sources: list[str]

    # Image Path
    image_paths: list[str]
    
    # Vision Context
    vision_context: list[str]
    
    # SQL Query
    sql_query: str

    # SQL Result
    sql_result: str

    # Generated Answer
    answer: str

    # Final Verified Response
    final_response: str