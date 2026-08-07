from backend.retrieval.query import processQuery
import time

def search_agent(state: dict) -> dict:
    print("\n[Search Agent]: Executing semantic document retrieval...")
    start = time.time()
    user_query = state.get("query", "")

    result = processQuery(user_query)

    context = result["context"]
    sources = result["sources"]
    image_paths = result["image_paths"]

    print(f"[Search Agent]: Retrieved {len(context)} text chunk(s).")
    print(f"[Search Agent]: Retrieved {len(image_paths)} image(s).")
    
    print(f"\n|---- Time Taken = {time.time()-start : .2f} ----|")
    
    return {
        "context": context,
        "sources": sources,
        "image_paths": image_paths
    }