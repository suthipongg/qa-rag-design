from qdrant_client import AsyncQdrantClient

def init_qdrant_client(host: str, port: int) -> AsyncQdrantClient:
    print(f"Connecting to Qdrant at {host}:{port}...")
    return AsyncQdrantClient(host=host, port=port)
