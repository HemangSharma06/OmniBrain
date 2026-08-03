from backend.retrieval.retriever import searchDocuments, searchImages
from backend.vision.clip import get_text_embedding


def processQuery(query):

    docs = searchDocuments(query)

    context_chunks = []
    sources = set()
    image_paths = []


    need_images = any(
        word in query.lower()
        for word in [
            "image",
            "images",
            "figure",
            "diagram",
            "chart",
            "graph",
            "visual"
        ]
    )

    if need_images:
        query_vector = get_text_embedding(query)
        image_paths = searchImages(query_vector)


    for doc in docs:
        context_chunks.append(
            doc.page_content
        )
        sources.add(
            doc.metadata.get(
                "source",
                "Unknown"
            )
        )

    return {
        "context": context_chunks,
        "sources": list(sources),
        "image_paths": image_paths
    }