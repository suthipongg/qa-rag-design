from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
import enum


class Base(DeclarativeBase):
    pass


class DocumentStatus(str, enum.Enum):
    PENDING = "pending"
    INDEXING = "indexing"
    INDEXED = "indexed"
    FAILED = "failed"


class Collection(Base):
    __tablename__ = "collections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    documents: Mapped[list["Document"]] = relationship(
        "Document", back_populates="collection", cascade="all, delete-orphan"
    )
    chat_messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage", back_populates="collection", cascade="all, delete-orphan"
    )


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    collection_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("collections.id", ondelete="CASCADE"), nullable=False
    )
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(20), nullable=False)  # pdf, md, csv, xlsx
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)  # bytes
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False
    )
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    collection: Mapped["Collection"] = relationship("Collection", back_populates="documents")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    collection_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("collections.id", ondelete="CASCADE"), nullable=False
    )
    conversation_id: Mapped[str] = mapped_column(String(100), nullable=False)  # UUID grouping messages
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # "user" | "assistant"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    rewritten_question: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    collection: Mapped["Collection"] = relationship("Collection", back_populates="chat_messages")
