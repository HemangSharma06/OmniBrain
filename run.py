import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

from backend.graph.graph import app


def main():

    print("OmniBrain Agentic RAG Framework Active")
    print("-" * 50)
    print("Type 'exit' or 'quit' to stop.\n")

    while True:

        query = input("User: ").strip()

        if query.lower() in ["exit", "quit"]:
            print("\nShutting down OmniBrain...")
            break

        if not query:
            continue

        inputs = {
            "query": query,
            "messages": [],
            "next_step": "",
            "context": [],
            "documents": [],
            "sources": [],
            "image_paths": [],
            "sql_query": "",
            "sql_result": "",
            "answer": "",
            "final_response": ""
        }

        try:

            result = app.invoke(inputs)

            print("\n================ FINAL RESPONSE ================")
            print(result.get("final_response", "No response generated."))
            print("================================================\n")

        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()