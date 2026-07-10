from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.dependencies import get_db
from app.db.sqlite.models import Collection, Document
from app.schemas.collections import (
    CollectionCreate,
    CollectionResponse,
    CollectionListResponse,
)
from app.schemas.common import StatusMessage

router = APIRouter(prefix="/collections", tags=["Collections"])


@router.post("", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
async def create_collection(
    body: CollectionCreate,
    db: AsyncSession = Depends(get_db),
):
    collection = Collection(name=body.name, description=body.description)
    db.add(collection)
    await db.commit()
    await db.refresh(collection)
    return CollectionResponse(
        id=collection.id,
        name=collection.name,
        description=collection.description,
        created_at=collection.created_at,
        document_count=0,
    )


@router.get("", response_model=CollectionListResponse)
async def list_collections(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(
            Collection,
            func.count(Document.id).label("document_count"),
        )
        .outerjoin(Document, Document.collection_id == Collection.id)
        .group_by(Collection.id)
        .order_by(Collection.created_at.desc())
    )
    rows = result.all()

    collections = [
        CollectionResponse(
            id=col.id,
            name=col.name,
            description=col.description,
            created_at=col.created_at,
            document_count=doc_count,
        )
        for col, doc_count in rows
    ]
    return CollectionListResponse(collections=collections, total=len(collections))


@router.get("/{collection_id}", response_model=CollectionResponse)
async def get_collection(collection_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Collection, func.count(Document.id).label("document_count"))
        .outerjoin(Document, Document.collection_id == Collection.id)
        .where(Collection.id == collection_id)
        .group_by(Collection.id)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail=f"Collection {collection_id} not found")

    col, doc_count = row
    return CollectionResponse(
        id=col.id,
        name=col.name,
        description=col.description,
        created_at=col.created_at,
        document_count=doc_count,
    )


@router.delete("/{collection_id}", response_model=StatusMessage)
async def delete_collection(
    collection_id: int, 
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Collection).where(Collection.id == collection_id))
    collection = result.scalar_one_or_none()
    if not collection:
        raise HTTPException(status_code=404, detail=f"Collection {collection_id} not found")

    try:
        indexing_service = request.app.state.indexing
        await indexing_service.delete_collection(collection_id)
    except Exception as e:
        print(f"⚠️ Warning: Failed to delete Qdrant collection {collection_id}: {e}")

    await db.delete(collection)
    await db.commit()
    return StatusMessage(message=f"Collection {collection_id} deleted successfully")