# NotebookAI

A lightweight, source-grounded RAG (Retrieval-Augmented Generation) research assistant built with Python, Streamlit, and Supabase.

**Philosophy:** Demonstrate a complete, well-engineered RAG architecture that prioritizes clarity, low cost, and extensibility over feature completeness.

---

## Features (MVP)

- **Notebook Management:** Create and organize reading collections
- **Document Ingestion:** Upload and process PDF, DOCX, TXT, Markdown
- **Source-Grounded Q&A:** Ask questions answered only by your documents
- **Citations:** Every answer includes source references
- **Summarization:** Generate executive summaries of notebook content
- **Provider Abstraction:** Swap LLM and embedding models via environment config

---

## Architecture

### High-Level Data Flow

```
User Uploads Document
    ↓
Deterministic Processing (Python)
  • Extract text
  • Split into chunks
  • Track page numbers / metadata
    ↓
Call Embedding API
  • Generate vectors (NVIDIA NIM or OpenAI)
    ↓
Store in Supabase PostgreSQL + pgvector
  • Chunks + embeddings
  • Metadata (filename, page, chunk number)
    ↓
User Asks Question
    ↓
Embed Question
    ↓
pgvector Cosine Similarity Search
    ↓
Retrieve Top-K Chunks
    ↓
Call LLM (NVIDIA NIM / OpenAI / Anthropic)
  • System prompt: "Answer ONLY from sources"
  • Context: Retrieved chunks
    ↓
LLM Returns Grounded Answer
    ↓
Python Maps Answer Back to Source Chunks
    ↓
Display Answer + Citations
```

### Module Organization

```
notebookai/
├── config.py                 # Environment loading, provider factories
├── database/
│   ├── client.py            # Supabase connection, CRUD, pgvector search
│   └── models.py            # Schema definitions
├── embeddings/
│   ├── base.py              # Abstract EmbeddingProvider
│   ├── nvidia_nim.py        # NVIDIA NIM implementation
│   ├── openai.py            # OpenAI fallback
│   └── factory.py           # Provider instantiation
├── llm/
│   ├── base.py              # Abstract LLMProvider
│   ├── nvidia_nim.py        # NVIDIA NIM implementation
│   ├── openai.py            # OpenAI fallback
│   ├── anthropic.py         # Anthropic fallback
│   ├── prompts.py           # Prompt templates
│   └── factory.py           # Provider instantiation
├── ingestion/               # Document extraction, chunking
│   ├── loader.py            # PDF/DOCX/TXT/MD extraction
│   ├── chunker.py           # Text splitting
│   └── embedder.py          # Batch embedding
├── retrieval/               # pgvector search
│   └── search.py            # Query embedding + similarity search
└── utils/
    └── validation.py        # File type/size checks

app.py                        # Streamlit UI
supabase/
└── schema.sql               # Database schema + pgvector setup
```

### Key Design Decisions

1. **Provider Abstraction:** LLM and embedding clients are behind abstract base classes. Configuration via environment variables enables swapping providers without code changes.

2. **Deterministic vs. LLM-Driven Separation:**
   - **Python (deterministic):** Text extraction, chunking, page tracking, vector search ranking
   - **LLM (reasoning):** Synthesis, interpretation, grounding validation

3. **No Streaming/Async (v1):** Streamlit + blocking API calls. Add async/streaming in v2 if needed.

4. **Single-User (v1):** No authentication. Multi-user support requires `notebooks.user_id` + RLS policies.

5. **Minimal Ingestion:** Simple fixed-size chunking initially. Advanced strategies (recursive, semantic) in v2.

---

## Setup

### 1. Clone & Install

```bash
git clone <repo>
cd notebookai-project
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

**Required:**
- `SUPABASE_URL` and `SUPABASE_KEY` (from Supabase dashboard)
- Either `NVIDIA_NIM_API_KEY` (preferred) or `OPENAI_API_KEY`
- LLM API key (NVIDIA NIM, OpenAI, or Anthropic)

**Recommended:**
- Set `EMBEDDING_PROVIDER=nvidia_nim` and `LLM_PROVIDER=nvidia_nim` for zero cost (free tier)

### 3. Set Up Supabase

1. Create a Supabase project: https://supabase.com
2. Copy your project URL and anon key to `.env`
3. Open Supabase SQL Editor and run contents of `supabase/schema.sql`
4. Verify tables created: `notebooks`, `documents`, `document_chunks`

### 4. Run Streamlit

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`

---

## API Keys & Free Tiers

### NVIDIA NIM (Preferred - **Free**)

1. Register at https://account.nvidia.com
2. Go to https://build.nvidia.com/nvidia/nemotron-3-ultra-550b-a55b
3. Copy API key
4. Set `NVIDIA_NIM_API_KEY` in `.env`

**Includes:** Embeddings (nemotron-3-embed-1b) + LLM (nemotron-3-ultra-550b-a55b), both free tier.

### Fallback: OpenAI

1. Create account at https://platform.openai.com
2. Generate API key
3. Set `OPENAI_API_KEY` in `.env`
4. Add credit (costs ~$0.01 per 1K tokens for embeddings)

### Fallback: Anthropic

1. Create account at https://console.anthropic.com
2. Generate API key
3. Set `ANTHROPIC_API_KEY` in `.env`

---

## Implementation Roadmap

### ✅ Phase 1: Skeleton (Current)

- [x] Repository structure
- [x] Configuration system with provider factories
- [x] Abstract base classes for LLM + embeddings
- [x] NVIDIA NIM implementations (LLM + embeddings)
- [x] OpenAI & Anthropic fallback implementations
- [x] Supabase schema with pgvector
- [x] Database client (CRUD + search)
- [x] Streamlit skeleton UI
- [x] Health checks

**Current State:** Runnable skeleton. UI shows placeholders. No actual document processing.

### Phase 2: Ingestion

- [ ] `ingestion/loader.py` — PDF (PyPDF2), DOCX (python-docx), TXT, MD extraction
- [ ] `ingestion/chunker.py` — Recursive character splitter with overlap
- [ ] `ingestion/embedder.py` — Batch embedding generation + error handling
- [ ] File upload validation (size, type)
- [ ] UI: Document upload & processing

### Phase 3: Retrieval & Q&A

- [ ] `retrieval/search.py` — pgvector cosine similarity search
- [ ] `llm/prompts.py` — Finalize grounding prompts
- [ ] RAG pipeline (embed query → search → retrieve → LLM → parse → citations)
- [ ] UI: Chat interface, answer display with source citations

### Phase 4: Summarization

- [ ] Notebook summary endpoint (retrieve all chunks → LLM → parse)
- [ ] UI: Summary display (executive summary, key concepts, etc.)

### Phase 5: Polish & Testing

- [ ] Unit tests (`tests/` suite)
- [ ] Error handling & user feedback
- [ ] Token counting & cost estimation
- [ ] README examples & troubleshooting

### Future (Post-MVP)

- [ ] Async/streaming responses
- [ ] Chat history persistence
- [ ] Multi-user support + auth
- [ ] Advanced chunking strategies
- [ ] Export summaries / answers
- [ ] PWA / mobile app
- [ ] Dark mode

---

## Configuration Reference

### Environment Variables

| Variable | Default | Notes |
|----------|---------|-------|
| `EMBEDDING_PROVIDER` | `nvidia_nim` | Options: `nvidia_nim`, `openai` |
| `LLM_PROVIDER` | `nvidia_nim` | Options: `nvidia_nim`, `openai`, `anthropic` |
| `NVIDIA_NIM_EMBEDDING_MODEL` | `nvidia/nemotron-3-embed-1b` | 1024 dimensions |
| `NVIDIA_NIM_LLM_MODEL` | `nvidia/nemotron-3-ultra-550b-a55b` | — |
| `CHUNK_SIZE` | `1500` | Characters per chunk |
| `CHUNK_OVERLAP` | `100` | Overlap between chunks |
| `RETRIEVAL_TOP_K` | `5` | Top K chunks to retrieve per query |
| `MAX_UPLOAD_SIZE_MB` | `50` | Max file size in MB |
| `SUPABASE_VECTOR_DIMENSION` | `1024` | For nemotron-3-embed-1b (OpenAI: 1536) |

### Swapping Providers

**Use NVIDIA NIM (free):**
```bash
EMBEDDING_PROVIDER=nvidia_nim
LLM_PROVIDER=nvidia_nim
NVIDIA_NIM_API_KEY=nvapi-...
```

**Use OpenAI:**
```bash
EMBEDDING_PROVIDER=openai
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_EMBEDDING_MODEL=text-embedding-3-small  # 1536 dimensions
SUPABASE_VECTOR_DIMENSION=1536
```

---

## Limitations (v1)

- **Single-user only:** No authentication
- **No real ingestion yet:** Document processing pipeline not implemented
- **Simple chunking:** Fixed-size chunks, no semantic splitting
- **No streaming:** Responses are blocking
- **No persistence:** Chat history not saved between sessions
- **Mobile not tested:** UI should work but untested

---

## Troubleshooting

### Supabase Connection Fails
- Verify `SUPABASE_URL` and `SUPABASE_KEY`
- Ensure schema deployed

### Embedding/LLM API Fails
- Verify API key is valid
- Check NVIDIA NIM free tier limits

### Vector Dimension Mismatch
- Update `SUPABASE_VECTOR_DIMENSION` to match embedding model
- NVIDIA nemotron: 1024
- OpenAI text-embedding-3-small: 1536

---

## Next Steps

Start with **Phase 2: Ingestion**
- Implement `notebookai/ingestion/loader.py` for PDF/DOCX extraction
- Implement `notebookai/ingestion/chunker.py` for text splitting
- Wire up document upload in Streamlit

