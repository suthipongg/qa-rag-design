# Document Q&A RAG Assistant

A RAG-powered document Q&A assistant that lets you load business documents, index them, ask questions, and receive grounded answers with source citations.

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Docker for Qdrant

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Run the backend
uvicorn app.main:app --reload --port 8000
```

### Docker

```bash
docker-compose up -d
# Qdrant Dashboard available at http://localhost:6333/dashboard
```

## 🛠️ Tech Stack

| Component    | Technology                        |
| :----------- | :-------------------------------- |
| Backend      | Python + FastAPI                  |
| LLM          | gemini-3.1-flash-lite (free tier) |
| Embeddings   | BGE-M3 (local)                    |
| Vector Store | Qdrant                            |
| Metadata DB  | SQLite                            |
