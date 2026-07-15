from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(documents, chunk_size=1000, chunk_overlap=200):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    chunks = text_splitter.split_documents(documents)

    print(f"\nTotal Chunks Created: {len(chunks)}")

    for i, chunk in enumerate(chunks[:3]):
        print(f"\nChunk {i+1}")
        print(f"Source: {chunk.metadata.get('source', 'Unknown')}")
        print(f"Length: {len(chunk.page_content)}")
        print(chunk.page_content[:300])
        print("-" * 50)

    return chunks
