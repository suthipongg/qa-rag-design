import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Request, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import get_db
from app.db.sqlite.models import Document, Collection
from app.schemas.documents import DocumentResponse, DocumentListResponse
from app.schemas.common import StatusMessage
from app.services.ingestion import ingest_document, process_document_background, delete_document_file

router = APIRouter(tags=["Documents"])


@router.post("/collections/{collection_id}/documents", response_model=list[DocumentResponse], status_code=status.HTTP_201_CREATED)
async def upload_documents(
    collection_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Collection).where(Collection.id == collection_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail=f"Collection {collection_id} not found")

    uploaded_records = []
    for file in files:
        try:
            doc, file_path = await ingest_document(
                collection_id=collection_id, 
                file=file, 
                db=db,
                upload_dir=request.app.state.upload_dir
            )
            uploaded_records.append(doc)
            
            background_tasks.add_task(
                process_document_background,
                document_id=doc.id,
                file_path=file_path,
                filename=doc.filename,
                collection_id=collection_id,
                session_factory=request.app.state.db_manager.session_factory,
                embedding_provider=request.app.state.embedding,
                indexing_service=request.app.state.indexing,
                chunking_service=request.app.state.chunking
            )
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to ingest file '{file.filename}': {str(e)}")

    return uploaded_records


@router.get("/collections/{collection_id}/documents", response_model=DocumentListResponse)
async def list_collection_documents(
    collection_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Collection).where(Collection.id == collection_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail=f"Collection {collection_id} not found")

    result = await db.execute(
        select(Document)
        .where(Document.collection_id == collection_id)
        .order_by(Document.created_at.desc())
    )
    docs = result.scalars().all()
    return DocumentListResponse(documents=list(docs), total=len(docs))


@router.delete("/documents/{document_id}", response_model=StatusMessage)
async def delete_document(
    document_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")

    file_path = os.path.join(request.app.state.upload_dir, str(document.collection_id), document.filename)
    try:
        await delete_document_file(file_path)
    except Exception as e:
        print(f"⚠️ Warning: Failed to delete file {file_path}: {e}")

    try:
        indexing_service = request.app.state.indexing
        await indexing_service.delete_document_vectors(document.collection_id, document.id)
    except Exception as e:
        print(f"⚠️ Warning: Failed to delete vectors for document {document_id}: {e}")

    await db.delete(document)
    await db.commit()

    return StatusMessage(message=f"Document {document_id} deleted successfully")
