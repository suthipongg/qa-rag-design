from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.dependencies import get_db
from app.db.sqlite.models import Collection, ChatMessage
from app.schemas.qa import QuestionRequest, AnswerResponse, CitationResponse, ChatMessageResponse
import uuid
from typing import List

router = APIRouter(prefix="/collections/{collection_id}/chat", tags=["Chat"])

@router.post("", response_model=AnswerResponse)
async def ask_question(
    collection_id: int,
    body: QuestionRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Collection).where(Collection.id == collection_id))
    collection = result.scalar_one_or_none()
    if not collection:
        raise HTTPException(status_code=404, detail=f"Collection {collection_id} not found")
        
    conversation_id = body.conversation_id or str(uuid.uuid4())
    
    retrieval_service = request.app.state.retrieval
    llm_service = request.app.state.llm
    
    try:
        history = []
        if body.conversation_id:
            history_result = await db.execute(
                select(ChatMessage)
                .where(ChatMessage.collection_id == collection_id)
                .where(ChatMessage.conversation_id == body.conversation_id)
                .order_by(ChatMessage.created_at.asc())
                .limit(request.app.state.context_window)
            )
            chat_messages = history_result.scalars().all()
            recent_messages = chat_messages[-10:]
            for msg in recent_messages:
                history.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        
        retrieved_chunks = await retrieval_service.search(
            collection_id=collection_id, 
            query=body.question
        )
        
        answer = await llm_service.generate_answer(
            query=body.question, 
            chunks=retrieved_chunks,
            history=history
        )
        
        citations = []
        for chunk in retrieved_chunks:
            payload = chunk.get("payload", {})
            citations.append(
                CitationResponse(
                    document_id=payload.get("document_id", 0),
                    document_name=payload.get("document_name", "Unknown"),
                    chunk_text=payload.get("text", ""),
                    page_number=payload.get("page_number"),
                    row_range=payload.get("row_range"),
                    relevance_score=chunk.get("score", 0.0)
                )
            )
            
        has_sufficient_evidence = len(retrieved_chunks) > 0 and not answer.startswith("I cannot find")
        
        user_msg = ChatMessage(
            collection_id=collection_id,
            conversation_id=conversation_id,
            role="user",
            content=body.question,
            rewritten_question=rewritten_question
        )
        db.add(user_msg)
        
        ai_msg = ChatMessage(
            collection_id=collection_id,
            conversation_id=conversation_id,
            role="assistant",
            content=answer
        )
        db.add(ai_msg)
        
        await db.commit()
        
        return AnswerResponse(
            answer=answer,
            citations=citations,
            has_sufficient_evidence=has_sufficient_evidence,
            conversation_id=conversation_id,
            rewritten_question=rewritten_question
        )
        
    except Exception as e:
        print(f"Error in ask_question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}", response_model=List[ChatMessageResponse])
async def get_conversation_history(
    collection_id: int,
    conversation_id: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.collection_id == collection_id)
        .where(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at.asc())
    )
    messages = result.scalars().all()
    
    response = []
    for msg in messages:
        response.append(
            ChatMessageResponse(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                rewritten_question=msg.rewritten_question,
                created_at=msg.created_at.isoformat()
            )
        )
    return response
