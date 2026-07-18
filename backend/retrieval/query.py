from retriever import searchDocuments

def processQuery(query):

    documents = searchDocuments(query)
    context = "\nexit()".join(
        [doc.page_content for doc in documents]
    )

    sources = [
        doc.metadata.get("source", "Unknown")
        for doc in documents
    ]
    response = {
        "query": query,
        "documents": documents,
        "context": context,
        "sources": sources
    }
    return response