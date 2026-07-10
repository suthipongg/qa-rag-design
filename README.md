# Document Q&A RAG Assistant

# QA RAG Design 🚀

A full-stack Retrieval-Augmented Generation (RAG) Q&A system that lets you upload documents and chat with them using local embeddings (BGE-M3) and Google Gemini.

## Features

- **Document Management**: Upload PDF, TXT, MD, CSV, XLSX files.
- **Smart Chunking & Indexing**: Automatic chunking and indexing into Qdrant vector database.
- **Conversational Q&A**: Asks questions with conversation memory (Query Rewriting).
- **Citations**: AI responses include exact source citations mapping to retrieved document chunks.
- **Clean UI**: Beautiful, glassmorphism-inspired React frontend.

## Prerequisites

- Python 3.12+
- Node.js 20+
- Docker
- A Google Gemini API Key

## Setup Instructions

### The Easy Way (Docker Compose)

Run the entire stack (Qdrant, Backend, Frontend) with a single command:

```bash
# 1. Setup your environment variable
cd backend
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
cd ..

# 2. Start the full stack
docker-compose up -d --build
```

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Qdrant DB**: http://localhost:6333

### Manual Setup (Without full Docker)

If you prefer running services manually for development:

#### 1. Start Qdrant

```bash
docker-compose up -d qdrant
```

#### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
uvicorn app.main:app --reload --port 8000
```

### Docker

```bash
docker-compose up -d
# Qdrant Dashboard available at http://localhost:6333/dashboard
```

## 🛠️ Tech Stack

| Component    | Technology                                          |
| :----------- | :-------------------------------------------------- |
| Backend      | Python + FastAPI                                    |
| LLM          | gemini-3.1-flash-lite (free tier)                   |
| Embeddings   | BGE-M3 (local) / gemini-embedding-2-preview (cloud) |
| Vector Store | Qdrant                                              |
| Metadata DB  | SQLite                                              |
