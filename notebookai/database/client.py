"""
Supabase database client for NotebookAI.

Handles connection, queries, and error management for PostgreSQL + pgvector.
"""

import logging
from typing import Optional, List
from uuid import UUID
from supabase import create_client, Client
from notebookai.config import settings

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Wrapper around Supabase PostgreSQL client with pgvector support."""

    def __init__(self):
        """Initialize Supabase client."""
        self.client: Client = create_client(settings.supabase_url, settings.supabase_key)
        self.vector_dimension = settings.supabase_vector_dimension
        logger.info(f"Initialized Supabase client (vector dimension: {self.vector_dimension})")

    # ============================================================================
    # Notebook Operations
    # ============================================================================

    def create_notebook(self, name: str, description: Optional[str] = None) -> dict:
        """
        Create a new notebook.

        Args:
            name: Notebook name
            description: Optional notebook description

        Returns:
            Created notebook record
        """
        try:
            data = self.client.table("notebooks").insert(
                {"name": name, "description": description}
            ).execute()
            logger.info(f"Created notebook: {name}")
            return data.data[0] if data.data else None

        except Exception as e:
            logger.error(f"Failed to create notebook: {e}")
            raise

    def get_notebook(self, notebook_id: UUID) -> Optional[dict]:
        """
        Get a notebook by ID.

        Args:
            notebook_id: Notebook UUID

        Returns:
            Notebook record or None
        """
        try:
            data = self.client.table("notebooks").select("*").eq("id", str(notebook_id)).execute()
            return data.data[0] if data.data else None

        except Exception as e:
            logger.error(f"Failed to get notebook {notebook_id}: {e}")
            raise

    def list_notebooks(self) -> List[dict]:
        """
        List all notebooks.

        Returns:
            List of notebook records
        """
        try:
            data = self.client.table("notebooks").select("*").order("created_at", desc=True).execute()
            return data.data

        except Exception as e:
            logger.error(f"Failed to list notebooks: {e}")
            raise

    def delete_notebook(self, notebook_id: UUID) -> bool:
        """
        Delete a notebook (cascade deletes documents and chunks).

        Args:
            notebook_id: Notebook UUID

        Returns:
            True if successful
        """
        try:
            self.client.table("notebooks").delete().eq("id", str(notebook_id)).execute()
            logger.info(f"Deleted notebook: {notebook_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete notebook {notebook_id}: {e}")
            raise

    # ============================================================================
    # Document Operations
    # ============================================================================

    def create_document(
        self, notebook_id: UUID, filename: str, file_type: str, file_size_bytes: int
    ) -> dict:
        """
        Create a document record.

        Args:
            notebook_id: Parent notebook UUID
            filename: Document filename
            file_type: File type (pdf, docx, txt, md)
            file_size_bytes: File size in bytes

        Returns:
            Created document record
        """
        try:
            data = self.client.table("documents").insert(
                {
                    "notebook_id": str(notebook_id),
                    "filename": filename,
                    "file_type": file_type,
                    "file_size_bytes": file_size_bytes,
                }
            ).execute()
            logger.info(f"Created document: {filename} in notebook {notebook_id}")
            return data.data[0] if data.data else None

        except Exception as e:
            logger.error(f"Failed to create document: {e}")
            raise

    def get_documents(self, notebook_id: UUID) -> List[dict]:
        """
        Get all documents in a notebook.

        Args:
            notebook_id: Notebook UUID

        Returns:
            List of document records
        """
        try:
            data = (
                self.client.table("documents")
                .select("*")
                .eq("notebook_id", str(notebook_id))
                .order("uploaded_at", desc=True)
                .execute()
            )
            return data.data

        except Exception as e:
            logger.error(f"Failed to get documents for notebook {notebook_id}: {e}")
            raise

    # ============================================================================
    # Document Chunk Operations (with pgvector)
    # ============================================================================

    def insert_chunks(self, chunks: List[dict]) -> bool:
        """
        Batch insert document chunks with embeddings.

        Args:
            chunks: List of dicts with:
                - document_id: UUID
                - notebook_id: UUID
                - chunk_number: int
                - page_number: int or None
                - source_text: str
                - embedding: list[float]

        Returns:
            True if successful
        """
        try:
            # Convert UUIDs to strings for Supabase
            for chunk in chunks:
                chunk["document_id"] = str(chunk["document_id"])
                chunk["notebook_id"] = str(chunk["notebook_id"])

            self.client.table("document_chunks").insert(chunks).execute()
            logger.info(f"Inserted {len(chunks)} chunks")
            return True

        except Exception as e:
            logger.error(f"Failed to insert chunks: {e}")
            raise

    def search_chunks(
        self, notebook_id: UUID, query_embedding: list, limit: int = 5
    ) -> List[dict]:
        """
        Search for similar document chunks using pgvector cosine similarity.

        Args:
            notebook_id: Restrict search to this notebook
            query_embedding: Query embedding vector
            limit: Number of results to return

        Returns:
            List of chunk records with similarity scores
        """
        try:
            # Use raw SQL for pgvector similarity search
            query_embedding_str = str(query_embedding)  # Format as [x, y, z, ...]

            response = self.client.rpc(
                "search_chunks",
                {
                    "query_embedding": query_embedding_str,
                    "notebook_id": str(notebook_id),
                    "limit": limit,
                },
            ).execute()

            return response.data if response.data else []

        except Exception as e:
            logger.error(f"Failed to search chunks in notebook {notebook_id}: {e}")
            # Fallback: return empty list instead of raising (graceful degradation)
            return []

    def get_chunks_by_document(self, document_id: UUID) -> List[dict]:
        """
        Get all chunks for a document.

        Args:
            document_id: Document UUID

        Returns:
            List of chunk records
        """
        try:
            data = (
                self.client.table("document_chunks")
                .select("*")
                .eq("document_id", str(document_id))
                .order("chunk_number", desc=False)
                .execute()
            )
            return data.data

        except Exception as e:
            logger.error(f"Failed to get chunks for document {document_id}: {e}")
            raise

    def get_chunks_by_notebook(self, notebook_id: UUID) -> List[dict]:
        """
        Get all chunks in a notebook (for summarization).

        Args:
            notebook_id: Notebook UUID

        Returns:
            List of chunk records
        """
        try:
            data = (
                self.client.table("document_chunks")
                .select("*")
                .eq("notebook_id", str(notebook_id))
                .order("created_at", desc=False)
                .execute()
            )
            return data.data

        except Exception as e:
            logger.error(f"Failed to get all chunks for notebook {notebook_id}: {e}")
            raise

    # ============================================================================
    # Health Check
    # ============================================================================

    def health_check(self) -> bool:
        """
        Verify database connection is working.

        Returns:
            True if connection is healthy
        """
        try:
            self.client.table("notebooks").select("id").limit(1).execute()
            return True

        except Exception as e:
            logger.warning(f"Database health check failed: {e}")
            return False


# Global instance
_db_client: Optional[SupabaseClient] = None


def get_db() -> SupabaseClient:
    """
    Get the Supabase client singleton.

    Returns:
        SupabaseClient instance
    """
    global _db_client
    if _db_client is None:
        _db_client = SupabaseClient()
    return _db_client
