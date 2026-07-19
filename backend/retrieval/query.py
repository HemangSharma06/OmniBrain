from backend.retrieval.retriever import searchDocuments

def processQuery(query):
    docs = searchDocuments(query)
    
    context_chunks = []
    formatted_sources = set()
    
    for doc in docs:
        context_chunks.append(doc.page_content)
        
        source_info = doc.metadata.get("source", "Unknown")
        if "sheet" in doc.metadata:
            source_info += f" (Sheet: {doc.metadata['sheet']})"
        formatted_sources.add(source_info)
        
    context = "\n\n".join(context_chunks)
    
    return {
        "context": context,
        "sources": list(formatted_sources)
    }