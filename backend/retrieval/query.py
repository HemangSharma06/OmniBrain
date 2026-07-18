from backend.retrieval.retriever import searchDocuments
from backend.llm.llm import generateAnswer

def processQuery(query):

    docs = searchDocuments(query)

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    sources = list(set(
        [doc.metadata["source"] for doc in docs]
    ))

    answer = generateAnswer(
        question=query,
        context=context
    )

    return {
        "query": query,
        "answer": answer,
        "sources": sources
    }