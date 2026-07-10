import os
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.sqlite.models import Document, DocumentStatus, Collection
from app.utils.extractors import extract_text_content


async def ingest_document(
    collection_id: int, 
    file: UploadFile, 
    db: AsyncSession,
    upload_dir: str
) -> tuple[Document, str]:
    
    result = await db.execute(select(Collection).where(Collection.id == collection_id))
    collection = result.scalar_one_or_none()
    if not collection:
        raise ValueError(f"Collection {collection_id} not found")
        
    filename = file.filename or "unknown_file"
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    
    if ext not in ["pdf", "md", "txt", "csv", "xlsx", "xls"]:
        raise ValueError(f"Unsupported file format: .{ext}")
        
    collection_dir = os.path.join(upload_dir, str(collection_id))
    os.makedirs(collection_dir, exist_ok=True)
    file_path = os.path.join(collection_dir, filename)
    
    await file.seek(0)
    file_content = await file.read()
    
    with open(file_path, "wb") as buffer:
        buffer.write(file_content)
        
    doc_record = Document(
        collection_id=collection_id,
        filename=filename,
        file_type=ext,
        file_size=len(file_content),
        status=DocumentStatus.PENDING,
        chunk_count=0
    )
    db.add(doc_record)
    await db.commit()
    await db.refresh(doc_record)
    
    return doc_record, file_path


async def process_document_background(
    document_id: int,
    file_path: str,
    filename: str,
    collection_id: int,
    session_factory,
    embedding_provider,
    indexing_service,
    chunking_service
):
    async with session_factory() as db:
        try:
            result = await db.execute(select(Document).where(Document.id == document_id))
            doc_record = result.scalar_one_or_none()
            if not doc_record:
                print(f"❌ Background task error: Document {document_id} not found in DB")
                return
            
            doc_record.status = DocumentStatus.INDEXING
            await db.commit()
            
            with open(file_path, "rb") as f:
                file_content = f.read()
                
            extracted_pages = extract_text_content(file_content, filename)
            chunks = chunking_service.chunk_document(filename, extracted_pages)
            
            if chunks:
                texts = [c["text"] for c in chunks]
                embeddings = await embedding_provider.embed_documents(texts)
                await indexing_service.index_chunks(collection_id, doc_record.id, chunks, embeddings)
            
            doc_record.status = DocumentStatus.INDEXED
            doc_record.chunk_count = len(chunks)
            await db.commit()
            print(f"✅ Background task completed: Document {document_id} indexed successfully")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            try:
                result = await db.execute(select(Document).where(Document.id == document_id))
                doc_record = result.scalar_one_or_none()
                if doc_record:
                    doc_record.status = DocumentStatus.FAILED
                    doc_record.error_message = str(e)
                    await db.commit()
            except Exception as db_err:
                print(f"❌ Failed to update document failure status in DB: {db_err}")


async def delete_document_file(document_path: str):
    if os.path.exists(document_path):
        os.remove(document_path)
