from datetime import datetime
from pydantic import BaseModel, Field


class CollectionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, examples=["Telecom FAQ"])
    description: str | None = Field(None, examples=["Customer-facing FAQ documents"])


class CollectionResponse(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime
    document_count: int = 0

    model_config = {"from_attributes": True}


class CollectionListResponse(BaseModel):
    collections: list[CollectionResponse]
    total: int
