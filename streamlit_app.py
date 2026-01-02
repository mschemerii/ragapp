"""Streamlit web interface for the RAG application.

Run with: streamlit run streamlit_app.py
"""

import streamlit as st
from pathlib import Path

from ragapp import RAGPipeline

# Page configuration
st.set_page_config(
    page_title="RAG Document Q&A",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .stats-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 0.5rem 0;
    }
    .source-card {
        padding: 1rem;
        border-left: 4px solid #4CAF50;
        background-color: #f9f9f9;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_pipeline():
    """Initialize and cache the RAG pipeline."""
    return RAGPipeline()


# Initialize pipeline
try:
    pipeline = get_pipeline()
except Exception as e:
    st.error(f"Failed to initialize RAG pipeline: {e}")
    st.info("Make sure you have set OPENAI_API_KEY in your .env file")
    st.stop()

# Header
st.markdown('<p class="main-header">📚 RAG Document Q&A</p>', unsafe_allow_html=True)
st.markdown("Ask questions about your documents using Retrieval-Augmented Generation")

# Sidebar
with st.sidebar:
    st.header("System Information")

    # Get stats
    try:
        stats = pipeline.get_stats()

        st.markdown('<div class="stats-card">', unsafe_allow_html=True)
        st.metric("Documents in Vector Store", stats['documents_in_store'])
        st.metric("Source Files", stats['source_files'])
        st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Could not load stats: {e}")

    st.divider()

    # Settings
    st.header("Query Settings")

    show_sources = st.checkbox("Show source documents", value=True)
    streaming = st.checkbox("Stream response", value=False)

    st.divider()

    # Document management
    st.header("Document Management")

    if st.button("📊 Refresh Stats", use_container_width=True):
        st.cache_resource.clear()
        st.rerun()

    st.info("""
    **To add documents:**
    1. Place files in `data/documents/`
    2. Run: `python -m ragapp ingest --reset`
    3. Click 'Refresh Stats'
    """)

    st.divider()

    # About
    st.header("About")
    st.markdown("""
    This RAG application uses:
    - **LangChain** for document processing
    - **ChromaDB** for vector storage
    - **OpenAI** for embeddings & generation

    Supports: PDF, TXT, DOCX, Markdown
    """)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Ask a Question")

    # Question input
    question = st.text_input(
        "Enter your question:",
        placeholder="What is this document about?",
        key="question_input",
    )

    # Example questions
    with st.expander("💡 Example Questions"):
        st.markdown("""
        - What are the main topics covered?
        - Can you summarize the key points?
        - What is RAG and how does it work?
        - What are the technical details?
        """)

with col2:
    st.header("Quick Actions")

    submit_button = st.button("🔍 Search", type="primary", use_container_width=True)
    clear_button = st.button("🗑️ Clear", use_container_width=True)

    if clear_button:
        st.rerun()

# Process query
if submit_button and question:

    if stats['documents_in_store'] == 0:
        st.warning("⚠️ No documents in the vector store. Please ingest documents first.")
        st.info("Run: `python -m ragapp ingest --reset`")
    else:
        st.divider()

        # Answer section
        st.header("Answer")

        try:
            if streaming:
                # Streaming response
                answer_placeholder = st.empty()
                full_answer = ""

                with st.spinner("Generating answer..."):
                    for chunk in pipeline.stream_query(question):
                        full_answer += chunk
                        answer_placeholder.markdown(full_answer + "▌")

                answer_placeholder.markdown(full_answer)

                # Get sources separately for streaming
                if show_sources:
                    with st.spinner("Retrieving sources..."):
                        _, sources = pipeline.query(question, return_sources=True)

            else:
                # Non-streaming response
                with st.spinner("Searching documents and generating answer..."):
                    if show_sources:
                        answer, sources = pipeline.query(question, return_sources=True)
                    else:
                        answer = pipeline.query(question)
                        sources = []

                st.markdown(answer)

            # Display sources
            if show_sources and sources:
                st.divider()
                st.header("📄 Source Documents")
                st.markdown(f"*Answer based on {len(sources)} source(s)*")

                for i, doc in enumerate(sources, 1):
                    source_file = doc.metadata.get('source', 'Unknown')
                    chunk_id = doc.metadata.get('chunk_id', 'N/A')

                    with st.expander(f"📌 Source {i}: {Path(source_file).name}"):
                        st.markdown(f"**File:** `{source_file}`")
                        st.markdown(f"**Chunk ID:** {chunk_id}")
                        st.divider()
                        st.markdown("**Content:**")
                        st.text(doc.page_content)

        except Exception as e:
            st.error(f"Error processing query: {e}")
            st.info("Make sure your OpenAI API key is valid and you have credits available.")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>Built with ❤️ using Streamlit and RAGApp</p>
    <p>Run <code>python -m ragapp --help</code> for CLI options</p>
</div>
""", unsafe_allow_html=True)
