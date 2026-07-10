from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.dependencies import get_db
from app.db.sqlite.models import Collection
from app.schemas.retrieve import RetrieveResponse
from typing import List

router = APIRouter(prefix="/collections/{collection_id}/retrieve", tags=["Retrieve"])

@router.get("", response_model=List[RetrieveResponse])
async def retrieve_only(
    collection_id: int,
    request: Request,
    query: str = Query(..., min_length=1),
    top_k: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Collection).where(Collection.id == collection_id))
    collection = result.scalar_one_or_none()
    if not collection:
        raise HTTPException(status_code=404, detail=f"Collection {collection_id} not found")
        
    retrieval_service = request.app.state.retrieval
    
    try:
        retrieved_chunks = await retrieval_service.search(
            collection_id=collection_id,
            query=query,
            top_k=top_k
        )
        
        citations = []
        for chunk in retrieved_chunks:
            payload = chunk.get("payload", {})
            citations.append(
                RetrieveResponse(
                    document_id=payload.get("document_id"),
                    document_name=payload.get("document_name"),
                    chunk_text=payload.get("text"),
                    page_number=payload.get("page_number"),
                    row_range=payload.get("row_range"),
                    relevance_score=chunk.get("score")
                )
            )
        return citations
    except Exception as e:
        print(f"Error in retrieve_only: {e}")
        raise HTTPException(status_code=500, detail=str(e))
