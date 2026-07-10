from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db.sqlite.connection import init_db_manager
from app.routers import collections, documents
from app.services.embeddings import get_embedding_provider
from app.services.indexing import IndexingService
from app.db.qdrant.connection import init_qdrant_client
from app.services.chunking import ChunkingService


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"📦 Embedding provider: {settings.EMBEDDING_PROVIDER}")
    print(f"🤖 LLM model: {settings.GEMINI_MODEL}")
    print(f"🔍 Qdrant: {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
    
    db_manager = init_db_manager(database_url=settings.DATABASE_URL, debug=settings.DEBUG)
    await db_manager.init_db()
    app.state.db_manager = db_manager
    print("✅ Database ready")
    
    embedding = get_embedding_provider(
        provider=settings.EMBEDDING_PROVIDER,
        model_name=settings.EMBEDDING_MODEL,
        api_key=settings.GEMINI_API_KEY
    )
    
    qdrant_client = init_qdrant_client(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
    indexing = IndexingService(client=qdrant_client, embedding=embedding)
    app.state.indexing = indexing
    
    chunking = ChunkingService(chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)
    
    yield
    
    print("👋 Shutting down...")
    await db_manager.close()
    print("💤 Database connection closed")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="A RAG-powered document Q&A assistant with grounded answers and citations.",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @app.get("/health", tags=["Health"])
    async def health_check():
        return {
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
        }

    app.include_router(collections.router, prefix="/api")
    app.include_router(documents.router, prefix="/api")

    return app


app = create_app()
