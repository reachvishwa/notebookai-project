"""
Prompt templates for NotebookAI RAG workflows.

Defines system prompts and question-answer templates that ensure
grounded responses based on provided sources.
"""

SYSTEM_PROMPT_RAG = """You are NotebookAI, a source-grounded research assistant.

Your role is to answer questions ONLY based on the documents provided in the notebook.

**Critical guidelines:**
1. Answer ONLY using information from the provided sources.
2. If the answer cannot be found in the sources, clearly say: "This information is not covered in the provided documents."
3. Distinguish between:
   - Information directly from sources (cite it)
   - Reasonable inference based on sources (acknowledge as inference)
   - Information beyond the sources (do NOT include)
4. Be concise and structured.
5. Always include citations in the format: [Source N: filename, page X]
"""

PROMPT_QA_TEMPLATE = """Based on the following document excerpts from your notebook, answer this question:

**Question:** {question}

**Relevant document excerpts:**

{sources}

**Answer:**
"""

SYSTEM_PROMPT_SUMMARIZATION = """You are NotebookAI, a document summarizer.

Analyze all content from a notebook and produce:
1. **Executive Summary**: 2-3 sentence overview of the key topic
2. **Key Concepts**: Main ideas, themes, and topics covered
3. **Important Facts**: Critical data points, findings, or arguments
4. **Topics Covered**: Bullet list of subjects discussed
5. **Unanswered Questions**: Important questions the sources leave open

Be concise. Focus on what's actually in the documents, not outside knowledge.
"""

PROMPT_SUMMARIZATION_TEMPLATE = """Summarize the following document content from a notebook:

**Document Content:**

{content}

**Summary:**
"""


def format_qa_prompt(question: str, sources: list[dict]) -> str:
    """
    Format a question-answering prompt with sources.

    Args:
        question: User's question
        sources: List of dicts with keys: 'text', 'filename', 'page_number'

    Returns:
        Formatted prompt string
    """
    sources_text = "\n".join(
        [
            f"[Source {i+1}: {source.get('filename', 'Unknown')}, page {source.get('page_number', 'N/A')}]\n{source['text']}\n"
            for i, source in enumerate(sources)
        ]
    )

    return PROMPT_QA_TEMPLATE.format(question=question, sources=sources_text)


def format_summarization_prompt(content: str) -> str:
    """
    Format a summarization prompt.

    Args:
        content: Full text content to summarize

    Returns:
        Formatted prompt string
    """
    return PROMPT_SUMMARIZATION_TEMPLATE.format(content=content)
