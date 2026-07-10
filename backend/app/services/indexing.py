from typing import List, Dict, Any
from qdrant_client import AsyncQdrantClient
from qdrant_client import models
import uuid


class IndexingService:
    def __init__(self, client: AsyncQdrantClient, embed_collection:str, embedding):
        self.client = client
        self.embedding_provider = embedding
        self.dimension = self.embedding_provider.get_dimension()
        self.collection_name = embed_collection

    async def ensure_collection(self) -> None:
        exists = await self.client.collection_exists(self.collection_name)
        if not exists:
            print(f"Creating Qdrant collection: {self.collection_name} with dimension {self.dimension}")
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.dimension,
                    distance=models.Distance.COSINE
                )
            )
            await self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="collection_id",
                field_schema=models.PayloadSchemaType.INTEGER
            )
            await self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="document_id",
                field_schema=models.PayloadSchemaType.INTEGER
            )

    async def index_chunks(
        self, 
        collection_id: int, 
        document_id: int, 
        chunks: List[Dict[str, Any]], 
        embeddings: List[List[float]]
    ) -> None:
        await self.ensure_collection()
        
        points = []
        for i, (chunk, vector) in enumerate(zip(chunks, embeddings)):
            point_id = str(uuid.uuid4())
            
            payload = {
                "collection_id": collection_id,
                "document_id": document_id,
                "text": chunk.get("text", ""),
                "chunk_index": chunk.get("chunk_index", i),
                "document_name": chunk.get("document_name", ""),
                "page_number": chunk.get("page_number"),
                "row_range": chunk.get("row_range"),
            }
            
            points.append(
                models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                )
            )

        await self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        print(f"Indexed {len(points)} points into Qdrant collection: {self.collection_name} for document: {document_id}")

    async def delete_document_vectors(self, collection_id: int, document_id: int) -> None:
        if await self.client.collection_exists(self.collection_name):
            await self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="collection_id",
                                match=models.MatchValue(value=collection_id)
                            ),
                            models.FieldCondition(
                                key="document_id",
                                match=models.MatchValue(value=document_id)
                            )
                        ]
                    )
                )
            )
            print(f"Deleted vectors for document_id {document_id} from Qdrant")

    async def delete_collection(self, collection_id: int) -> None:
        if await self.client.collection_exists(self.collection_name):
            await self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="collection_id",
                                match=models.MatchValue(value=collection_id)
                            )
                        ]
                    )
                )
            )
            print(f"Deleted vectors for collection_id {collection_id} from Qdrant")
