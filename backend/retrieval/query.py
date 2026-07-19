from backend.retrieval.retriever import searchDocuments


def processQuery(query):

    docs = searchDocuments(query)

    context_chunks = []
    formatted_sources = set()
    image_paths = []

    for doc in docs:

        context_chunks.append(doc.page_content)

        source = doc.metadata.get("source", "Unknown")

        if "sheet" in doc.metadata:
            source += f" (Sheet: {doc.metadata['sheet']})"

        formatted_sources.add(source)

        if "image_path" in doc.metadata:
            image_paths.append(doc.metadata["image_path"])

    return {
        "context": context_chunks,
        "sources": list(formatted_sources),
        "image_paths": image_paths
    }