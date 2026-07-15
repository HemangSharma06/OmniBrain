# PDF Ingestion Pipeline

## Objective

The ingestion pipeline converts raw documents into a format supported by RAG.

---

## Workflow

```
PDF Document => Load PDF => Extract Text => Extract Images & Tables => Text Chunking => Generate Embeddings => Store in Vector Database
```

---

## Components

### 1. PDF Loader

* Reads PDF documents.
* Extracts text from each page.

### 2. Image Extraction

* Extracts charts, graphs, and figures.
* Stores images for future multimodal retrieval.

### 3. Table Extraction

* Extracts tabular data from financial reports.
* Preserves row and column structure.

### 4. Text Chunking

* Splits long text into smaller chunks.
* Improves retrieval accuracy.

### 5. Embedding Generation

* Converts text chunks into vector embeddings.
* Enables semantic similarity search.

### 6. Vector Database Storage

* Stores embeddings in a vector database (Qdrant/FAISS).
* Allows efficient retrieval of relevant information.

---

## Expected Output
The ingestion pipeline should produce:

* Clean text chunks
* Extracted images
* Extracted tables
* Vector embeddings
* Metadata (page number, source document)
---