# Document Q&A RAG Architecture

This document provides a high-level overview of the architectural design and data flow of the Document Q&A Retrieval-Augmented Generation (RAG) system.

## System Components

### 1. Frontend (React + Vite)

- Built with React, TypeScript, and Vite.
- Manages Collections and Documents via REST API.
- Provides a Knowledge Management to upload knowledge files.
- Provides a Retrieval Playground to test chunking and similarity search.
- Provides a Q&A Chat UI that streams/displays responses with citations.

### 2. Backend (FastAPI)

- Exposes RESTful endpoints for the frontend.
- Follows a layered architecture (`routers` -> `services` -> `db/models`).
- Uses dependency injection (`request.app.state`) for services.

### 3. Database (SQLite via SQLAlchemy)

- Stores metadata: `Collection`, `Document`, and `ChatMessage`.
- Provides transactional integrity for metadata.

### 4. Vector Database (Qdrant)

- Used for semantic similarity search.
- Stores document chunks and their embeddings.
- Indexed by `collection_id` to ensure queries are isolated to a specific collection.

### 5. Embedding & LLM Services (BGE-M3 & Gemini)

- **Embedding**: Local `BAAI/bge-m3` model via FastEmbed/Transformers for dense vector embeddings.
- **LLM**: Google Gemini (`gemini-3.1-flash-lite`) used for:
  - **Query Rewriting**: Contextualizing follow-up questions.
  - **Answer Generation**: Synthesizing answers strictly from retrieved context.

## Data Flows

### A. Document Ingestion Flow

1. User uploads a file (PDF, MD, TXT, CSV, XLSX) via UI.
2. `documents.py` router accepts the file and creates a DB record.
3. `ingestion.py` extracts text using specific extractors.
4. `chunking.py` splits the text into manageable chunks.
5. `embeddings.py` generates vector embeddings for each chunk.
6. `indexing.py` uploads chunks + embeddings + payload to Qdrant.

### B. Q&A Flow

1. User submits a question.
2. Backend retrieves conversation history (up to 5 turns).
3. `llm.py` (Gemini) rewrites the query into a standalone search query based on context.
4. `embeddings.py` generates an embedding for the rewritten query.
5. `retrieval.py` searches Qdrant for the top-k most similar chunks.
6. `llm.py` (Gemini) takes the retrieved chunks + the rewritten query and generates a grounded answer with citations.
7. Backend saves the message to the DB and returns the payload to the UI.

## Assumptions & Known Limitations

### Assumptions

- **Language**: The primary language for documents is English/Thai, and Gemini is sufficient for multilingual QA.
- **Scale**: The app is designed for small to medium document collections (1-100 documents). Memory requirements are small enough for local Qdrant.
- **Hardware**: The system assumes the user can run BGE-M3 locally (takes ~2.5GB RAM) for embeddings.

### Limitations (Incomplete Features)

- **Table-aware Extraction**: The current PDF extractor (`PyMuPDF`) captures raw text well but does not preserve complex nested tables or multi-column layouts perfectly.
- **DOCX Support**: Currently unsupported (only PDF, MD, TXT, CSV, XLSX).
- **Security**: The application lacks authentication (SSO) and multi-tenant data isolation.
- **In-flight Cancellation**: Deleting a document removes it from the DB and Qdrant, but doesn't cancel in-progress background chunking jobs.

## Production Improvements & MCP Mapping

### What we would improve for production

- **Advanced Chunking**: Implement Semantic Chunking (grouping sentences by embedding similarity) rather than naive recursive chunking.
- **Evaluation Pipeline**: Implement a CI/CD evaluation runner using `Ragas` to monitor Faithfulness and Answer Relevance against a golden dataset of QA pairs.
- **Cost & Latency Monitoring**: Add LangSmith or Arize Phoenix to trace LLM calls, monitor token usage, and track API latencies.
- **Reranker**: Add a Cross-Encoder reranker step after the Hybrid Search retrieval to further improve top-K accuracy.

### MCP (Model Context Protocol) Mapping

The API and Service boundary is explicitly designed to easily map to an MCP server:

- **`RetrievalService.search()`** acts as an isolated boundary that an MCP server can wrap to expose a `query_knowledge_base(query, collection_id)` tool.
- By decoupling ingestion from retrieval, the Retrieval layer can be deployed as a standalone, read-only MCP Server, allowing agents like Claude or Cursor to query the vector database without needing access to the web UI.
