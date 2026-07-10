from datetime import datetime
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    collection_id: int
    filename: str
    file_type: str
    file_size: int
    status: str
    chunk_count: int
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int
