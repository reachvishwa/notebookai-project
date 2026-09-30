-- ============================================================================
-- NotebookAI Database Schema
-- Deploy this directly to Supabase SQL editor
-- ============================================================================

-- Enable pgvector extension for vector embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- Notebooks Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS notebooks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notebooks_created_at ON notebooks(created_at DESC);

-- ============================================================================
-- Documents Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  notebook_id UUID NOT NULL REFERENCES notebooks(id) ON DELETE CASCADE,
  filename TEXT NOT NULL,
  file_type TEXT NOT NULL, -- 'pdf', 'docx', 'txt', 'md'
  file_size_bytes INT NOT NULL,
  uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(notebook_id, filename)
);

CREATE INDEX idx_documents_notebook ON documents(notebook_id);
CREATE INDEX idx_documents_file_type ON documents(file_type);

-- ============================================================================
-- Document Chunks Table (with pgvector embeddings)
-- ============================================================================
-- Vector dimension: 1024 (nemotron-3-embed-1b)
-- If switching to OpenAI embeddings (1536), update the VECTOR(1536) clause

CREATE TABLE IF NOT EXISTS document_chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  notebook_id UUID NOT NULL REFERENCES notebooks(id) ON DELETE CASCADE,
  chunk_number INT NOT NULL,
  page_number INT, -- For PDFs; NULL for text documents
  source_text TEXT NOT NULL,
  embedding VECTOR(1024), -- nemotron-3-embed-1b: 1024 dimensions
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT chunk_order UNIQUE(document_id, chunk_number)
);

-- Vector index for efficient similarity search
-- Using IVFFlat for cost-efficiency; HNSW available for production
CREATE INDEX idx_chunks_embedding ON document_chunks USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

-- Additional indexes for common queries
CREATE INDEX idx_chunks_notebook ON document_chunks(notebook_id);
CREATE INDEX idx_chunks_document ON document_chunks(document_id);
CREATE INDEX idx_chunks_chunk_number ON document_chunks(chunk_number);

-- ============================================================================
-- Chat Sessions Table (optional for v1, included for extensibility)
-- ============================================================================
CREATE TABLE IF NOT EXISTS chat_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  notebook_id UUID NOT NULL REFERENCES notebooks(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chat_sessions_notebook ON chat_sessions(notebook_id);

-- ============================================================================
-- Chat Messages Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS chat_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
  content TEXT NOT NULL,
  source_chunk_ids UUID[] DEFAULT ARRAY[]::UUID[], -- References to document_chunks IDs
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chat_messages_session ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_role ON chat_messages(role);

-- ============================================================================
-- Metadata & Configuration (optional, for tracking embedding models/versions)
-- ============================================================================
CREATE TABLE IF NOT EXISTS metadata (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Store embedding model info for traceability
INSERT INTO metadata (key, value) VALUES 
  ('embedding_model', 'nvidia/nemotron-3-embed-1b'),
  ('embedding_dimension', '1024'),
  ('schema_version', '1.0.0')
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = CURRENT_TIMESTAMP;

-- ============================================================================
-- Row-Level Security (optional, disabled by default for v1)
-- ============================================================================
-- If multi-user support is added later, enable RLS policies:
-- ALTER TABLE notebooks ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "users_see_own_notebooks" ON notebooks FOR ALL USING (auth.uid() = user_id);
