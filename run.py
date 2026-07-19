import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

from backend.graph.graph import app

def main():
    print("OmniBrain Agentic RAG Framework Active")
    print("-" * 50)
    
    query_1 = "What was the Microsoft's revenue in 2025?"
    
    print(f"\nUser: {query_1}")
    inputs = {
        "query": query_1, 
        "context": [], 
        "messages": [],
        "next_step": "",
        "answer": "",
        "final_response": ""
    }
    
    result = app.invoke(inputs)
    
    print("\n================ FINAL RESPONSE ================")
    print(result.get("final_response", "No response generated."))
    print("================================================\n")
    sys.exit(0)
if __name__ == "__main__":
    main()