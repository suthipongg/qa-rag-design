
from pydantic import BaseModel


class RetrieveResponse(BaseModel):
    document_id: int
    document_name: str
    chunk_text: str
    page_number: int | None = None
    row_range: str | None = None
    relevance_score: float