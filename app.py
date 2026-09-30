"""
NotebookAI — Streamlit web application.

Main entry point for the NotebookAI UI.
Run with: streamlit run app.py
"""

import streamlit as st
import logging
from notebookai.config import settings
from notebookai.database import get_db
from notebookai.config import get_embedding_provider, get_llm_provider

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# ============================================================================
# Streamlit Config
# ============================================================================

st.set_page_config(
    page_title="NotebookAI",
    page_icon="📓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================================
# Session State Management
# ============================================================================

if "current_notebook_id" not in st.session_state:
    st.session_state.current_notebook_id = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ============================================================================
# Sidebar: Notebook Management
# ============================================================================

with st.sidebar:
    st.title("📓 NotebookAI")
    st.divider()

    # Health checks
    db = get_db()
    try:
        embedding_provider = get_embedding_provider()
        llm_provider = get_llm_provider()

        col1, col2 = st.columns(2)
        with col1:
            if db.health_check():
                st.success("✓ DB", help="Database connection OK")
            else:
                st.error("✗ DB", help="Database connection failed")

        with col2:
            if llm_provider.health_check():
                st.success("✓ LLM", help=f"LLM ({llm_provider.get_model_name()}) OK")
            else:
                st.error("✗ LLM", help="LLM connection failed")

        st.divider()

    except Exception as e:
        st.error(f"Configuration error: {e}")
        st.stop()

    # Create new notebook
    st.subheader("New Notebook")
    with st.form("create_notebook"):
        nb_name = st.text_input("Notebook Name", placeholder="e.g., AI Research, Paper Analysis")
        nb_desc = st.text_area("Description (optional)", placeholder="What's this about?", height=80)
        submit = st.form_submit_button("✨ Create Notebook", use_container_width=True)

        if submit:
            if nb_name.strip():
                try:
                    notebook = db.create_notebook(nb_name.strip(), nb_desc.strip() or None)
                    st.session_state.current_notebook_id = notebook["id"]
                    st.success(f"Created: {nb_name}")
                    st.rerun()

                except Exception as e:
                    st.error(f"Failed to create notebook: {e}")
            else:
                st.warning("Please enter a notebook name")

    st.divider()

    # List existing notebooks
    st.subheader("My Notebooks")
    try:
        notebooks = db.list_notebooks()

        if notebooks:
            for nb in notebooks:
                col1, col2 = st.columns([4, 1])

                with col1:
                    if st.button(
                        f"📖 {nb['name']}",
                        key=f"nb_{nb['id']}",
                        use_container_width=True,
                    ):
                        st.session_state.current_notebook_id = nb["id"]
                        st.rerun()

                with col2:
                    if st.button("🗑️", key=f"del_{nb['id']}", help="Delete notebook"):
                        try:
                            db.delete_notebook(nb["id"])
                            if st.session_state.current_notebook_id == nb["id"]:
                                st.session_state.current_notebook_id = None
                            st.success("Deleted")
                            st.rerun()

                        except Exception as e:
                            st.error(f"Failed to delete: {e}")

        else:
            st.info("No notebooks yet. Create one to get started.")

    except Exception as e:
        st.error(f"Failed to load notebooks: {e}")


# ============================================================================
# Main Content Area
# ============================================================================

if not st.session_state.current_notebook_id:
    st.title("👋 Welcome to NotebookAI")
    st.markdown(
        """
        NotebookAI is a lightweight, source-grounded research assistant.

        **Features:**
        - 📤 Upload documents (PDF, DOCX, TXT, MD)
        - 🔍 Ask questions grounded only in your sources
        - 📚 Get answers with citations
        - 📋 Summarize entire notebooks

        **Get Started:**
        1. Create a new notebook in the sidebar
        2. Upload documents
        3. Ask questions

        ---

        **Configuration:**
        - Embedding Provider: `{embedding_provider}`
        - LLM Provider: `{llm_provider}`
        - Chunk Size: `{chunk_size}`
        - Top-K Retrieval: `{retrieval_top_k}`
        """.format(
            embedding_provider=settings.embedding_provider,
            llm_provider=settings.llm_provider,
            chunk_size=settings.chunk_size,
            retrieval_top_k=settings.retrieval_top_k,
        )
    )

else:
    # Notebook view
    notebook = db.get_notebook(st.session_state.current_notebook_id)

    if notebook:
        st.title(f"📖 {notebook['name']}")
        if notebook.get("description"):
            st.markdown(f"_{notebook['description']}_")

        tab_sources, tab_chat, tab_summary = st.tabs(["📚 Sources", "💬 Chat", "📋 Summary"])

        # ========================================================================
        # Tab: Sources
        # ========================================================================

        with tab_sources:
            st.subheader("Manage Sources")

            col1, col2 = st.columns([2, 1])
            with col1:
                uploaded_files = st.file_uploader(
                    "Upload documents (PDF, DOCX, TXT, MD)",
                    accept_multiple_files=True,
                    type=settings.get_allowed_file_types(),
                )

            with col2:
                st.write("")  # Spacing
                if st.button("📤 Process Uploads", use_container_width=True):
                    if uploaded_files:
                        with st.spinner("Processing documents..."):
                            st.info(
                                "📋 Document ingestion pipeline:\n"
                                "1. Extract text → 2. Chunk → 3. Embed → 4. Store in pgvector\n\n"
                                "Placeholder: implement in next phase"
                            )
                    else:
                        st.warning("No files selected")

            st.divider()

            # List existing documents
            st.subheader("Uploaded Documents")
            try:
                documents = db.get_documents(st.session_state.current_notebook_id)

                if documents:
                    for doc in documents:
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.text(f"📄 {doc['filename']}")
                        with col2:
                            st.caption(f"{doc['file_size_bytes'] / 1024:.1f} KB")
                        with col3:
                            st.caption(doc['file_type'].upper())

                else:
                    st.info("No documents uploaded yet.")

            except Exception as e:
                st.error(f"Failed to load documents: {e}")

        # ========================================================================
        # Tab: Chat (Q&A)
        # ========================================================================

        with tab_chat:
            st.subheader("Ask Questions")

            # Display chat history
            for msg in st.session_state.chat_history:
                role_icon = "👤" if msg["role"] == "user" else "🤖"
                with st.chat_message(msg["role"]):
                    st.markdown(f"{role_icon} {msg['content']}")

            # Input form
            user_question = st.chat_input("Ask a question grounded in your documents...")

            if user_question:
                # Add user message
                st.session_state.chat_history.append({"role": "user", "content": user_question})

                with st.chat_message("user"):
                    st.markdown(f"👤 {user_question}")

                # Placeholder for RAG response
                with st.chat_message("assistant"):
                    with st.spinner("Searching documents..."):
                        st.info(
                            "🔍 RAG pipeline:\n"
                            "1. Embed query → 2. Search pgvector → 3. Retrieve chunks → 4. Generate answer → 5. Citations\n\n"
                            "Placeholder: implement in next phase"
                        )

                    # Placeholder response
                    response = "This feature will search your documents and provide answers with citations."
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    st.markdown(f"🤖 {response}")

        # ========================================================================
        # Tab: Summary
        # ========================================================================

        with tab_summary:
            st.subheader("Notebook Summary")

            if st.button("📋 Generate Summary", use_container_width=True):
                with st.spinner("Summarizing notebook..."):
                    st.info(
                        "📊 Summarization pipeline:\n"
                        "1. Retrieve all chunks → 2. Concat content → 3. Send to LLM → 4. Parse output\n\n"
                        "Placeholder: implement in next phase"
                    )

    else:
        st.error("Notebook not found")


# ============================================================================
# Footer
# ============================================================================

st.divider()
st.caption(
    f"NotebookAI v{settings.log_level} | "
    f"Embeddings: {settings.embedding_provider} | "
    f"LLM: {settings.llm_provider}"
)
