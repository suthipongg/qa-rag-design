from typing import List, Dict, Any
from qdrant_client import AsyncQdrantClient
from qdrant_client import models

class RetrievalService:
    def __init__(self, client: AsyncQdrantClient, embed_collection: str, embedding_provider, top_k: int = 5):
        self.client = client
        self.embedding_provider = embedding_provider
        self.collection_name = embed_collection
        self.top_k = top_k

    async def search(self, collection_id: int, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        k = top_k or self.top_k
        
        query_vector = await self.embedding_provider.embed_query(query)
        if not await self.client.collection_exists(self.collection_name):
            return []
        
        search_result = await self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="collection_id",
                        match=models.MatchValue(value=collection_id)
                    )
                ]
            ),
            limit=k,
            with_payload=True,
            with_vectors=False
        )
        
        results = []
        for scored_point in search_result.points:
            results.append({
                "score": scored_point.score,
                "payload": scored_point.payload
            })
            
        return results
