import operator
from typing import Annotated, Sequence
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    query: str                                    
    messages: Annotated[Sequence[BaseMessage], operator.add] 
    next_step: str                                 
    context: Annotated[list, operator.add]        
    answer: str                                    
    final_response: str                            
    