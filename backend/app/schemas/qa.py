from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, examples=["What is the price of the Premium package?"])
    conversation_id: str | None = Field(None, description="Pass to continue an existing conversation")


class CitationResponse(BaseModel):
    document_id: int
    document_name: str
    chunk_text: str
    page_number: int | None = None
    row_range: str | None = None
    relevance_score: float


class AnswerResponse(BaseModel):
    answer: str
    citations: list[CitationResponse]
    has_sufficient_evidence: bool
    conversation_id: str
    rewritten_question: str | None = None


class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    rewritten_question: str | None = None
    created_at: str

    class Config:
        from_attributes = True

