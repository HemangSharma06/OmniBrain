from backend.retrieval.query import searchDocuments 

def search_agent(state: dict) -> dict:
    print("\n🔍 [Search Agent]: Executing semantic document retrieval...")
    user_query = state.get("query", "")
    
    retrieved_docs = searchDocuments(user_query, k=5)
    
    context_chunks = [doc.page_content for doc in retrieved_docs]
    
    print(f"✅ [Search Agent]: Retrieved {len(context_chunks)} relevant text chunks.")
    return {"context": context_chunks}