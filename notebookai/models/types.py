"""
Domain models for NotebookAI entities.

Pydantic models for type validation and serialization.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class NotebookBase(BaseModel):
    """Base notebook data."""

    name: str
    description: Optional[str] = None


class Notebook(NotebookBase):
    """Notebook with metadata."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentBase(BaseModel):
    """Base document data."""

    filename: str
    file_type: str  # 'pdf', 'docx', 'txt', 'md'
    file_size_bytes: int


class Document(DocumentBase):
    """Document with metadata."""

    id: UUID
    notebook_id: UUID
    uploaded_at: datetime

    class Config:
        from_attributes = True


class DocumentChunkBase(BaseModel):
    """Base document chunk data."""

    chunk_number: int
    source_text: str
    page_number: Optional[int] = None


class DocumentChunk(DocumentChunkBase):
    """Document chunk with embedding and metadata."""

    id: UUID
    document_id: UUID
    notebook_id: UUID
    embedding: Optional[List[float]] = None  # Vector (will be queried from DB)
    created_at: datetime

    class Config:
        from_attributes = True


class Message(BaseModel):
    """Chat message."""

    role: str  # 'user' or 'assistant'
    content: str
    source_chunk_ids: Optional[List[UUID]] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
