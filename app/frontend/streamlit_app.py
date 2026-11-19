import re
import sys
import html
from pathlib import Path
from datetime import datetime
import streamlit as st
import ollama

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.ingestion.loaders.document_loader import load_document
from app.ingestion.chunker import split_into_chunks
from app.ingestion.embedder import generate_embeddings
from app.ingestion.vector_store import store_embeddings, get_chroma_client
from app.retrieval.retriever import search_documents
from app.generation.answer_generator import MODEL_NAME as DEFAULT_MODEL_NAME, format_source_location

try:
    from streamlit.runtime.scriptrunner_utils.exceptions import StopException, RerunException
except ImportError:
    try:
        from streamlit.runtime.scriptrunner import StopException, RerunException
    except ImportError:
        StopException = SystemExit
        RerunException = SystemExit

COLLECTION_NAME = "documents"
SUPPORTED_EXTENSIONS = [
    "pdf", "docx", "xlsx", "pptx", "txt", "md", "csv", "json", "html", "htm",
    "png", "jpg", "jpeg", "tiff", "tif", "bmp", "webp", "gif",
    "doc", "xls", "ppt"
]

# Configure Streamlit page
st.set_page_config(
    page_title="Universal Document Assistant",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom ChatGPT-style CSS injection (clean, theme-adaptive, native scrolling)
st.markdown("""
<style>
    /* Transparent Streamlit header with zero height impact */
    header[data-testid="stHeader"] {
        background: transparent !important;
        pointer-events: none !important;
        height: 0 !important;
        z-index: 999990 !important;
    }
    header[data-testid="stHeader"] button,
    header[data-testid="stHeader"] a {
        pointer-events: auto !important;
    }

    /* Page container spacing */
    .block-container {
        padding-top: 0.25rem !important;
        padding-bottom: 8rem !important;
        max-width: 900px !important;
    }
    
    /* Ensure Streamlit containers do not clip sticky header */
    div[data-testid="stVerticalBlock"]:has(.chat-top-navbar),
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.chat-top-navbar) {
        overflow: visible !important;
    }

    /* Fixed/Sticky Top Context Header Bar (Rounded corners, no bottom divider line) */
    div[data-testid="stElementContainer"]:has(.chat-top-navbar) {
        position: sticky !important;
        top: 0.5rem !important;
        z-index: 990 !important;
        width: 100% !important;
        background-color: var(--background-color, #18181b) !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35) !important;
        padding: 0.75rem 1.25rem !important;
        margin-bottom: 1.5rem !important;
    }

    div[data-testid="stElementContainer"]:has(.chat-top-navbar) div[data-testid="stMarkdownContainer"],
    div[data-testid="stElementContainer"]:has(.chat-top-navbar) p {
        margin: 0 !important;
        padding: 0 !important;
    }

    .chat-top-navbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        width: 100%;
        padding-right: 5rem; /* Room for Streamlit header controls */
        box-sizing: border-box;
    }

    .context-info {
        display: flex;
        align-items: center;
        gap: 8px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        max-width: 72%;
        font-size: 0.88rem;
    }

    .context-label {
        opacity: 0.65;
        font-weight: 500;
        margin-right: 2px;
    }

    .context-name {
        font-weight: 600;
        color: #f4f4f5;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .status-dot {
        height: 8px;
        width: 8px;
        background-color: #10b981;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 7px rgba(16, 185, 129, 0.8);
        flex-shrink: 0;
    }

    .model-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16, 185, 129, 0.12);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.35);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        white-space: nowrap;
        flex-shrink: 0;
    }

    .model-dot {
        font-size: 0.65rem;
        line-height: 1;
    }
    
    /* Empty State Hero */
    .hero-container {
        text-align: center;
        padding: 2.5rem 1rem 1.8rem 1rem;
    }
    
    .hero-icon {
        font-size: 2.8rem;
        margin-bottom: 0.6rem;
    }
    
    .hero-title {
        font-size: 1.65rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin-bottom: 0.4rem;
    }
    
    .hero-subtitle {
        opacity: 0.72;
        font-size: 0.95rem;
        max-width: 580px;
        margin: 0 auto 2rem auto;
        line-height: 1.55;
    }
    
    /* Suggestion Buttons styling */
    .stButton > button {
        border-radius: 10px;
        transition: all 0.2s ease;
    }
    
    /* Stop button styling in bottom dock */
    .stop-button-wrapper div[data-testid="stButton"] > button {
        background-color: rgba(239, 68, 68, 0.14) !important;
        border: 1px solid rgba(239, 68, 68, 0.5) !important;
        color: #ef4444 !important;
        font-weight: 600 !important;
        border-radius: 20px !important;
        box-shadow: 0 2px 10px rgba(239, 68, 68, 0.18) !important;
        padding: 0.45rem 1.2rem !important;
        margin-bottom: 0.4rem !important;
    }
    .stop-button-wrapper div[data-testid="stButton"] > button:hover {
        background-color: rgba(239, 68, 68, 0.26) !important;
        border-color: #ef4444 !important;
    }
    
    /* Citation & Source Card */
    .source-card {
        background: rgba(125, 125, 125, 0.07);
        border: 1px solid rgba(125, 125, 125, 0.18);
        border-left: 4px solid #3b82f6;
        border-radius: 8px;
        padding: 10px 14px;
        margin-top: 8px;
        margin-bottom: 8px;
        font-size: 0.85rem;
    }
    
    .source-meta {
        font-weight: 600;
        color: #3b82f6;
        margin-bottom: 6px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .source-score {
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
        padding: 1px 7px;
        border-radius: 10px;
        font-size: 0.72rem;
        font-weight: 600;
    }
    
    .source-text {
        opacity: 0.88;
        line-height: 1.45;
        white-space: pre-wrap;
        word-break: break-word;
    }
    
    /* Sidebar typography */
    .sidebar-title {
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 2px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .sidebar-subtitle {
        font-size: 0.8rem;
        opacity: 0.65;
        margin-bottom: 16px;
    }
    
    /* Stopped generation badge */
    .stopped-badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        background: rgba(245, 158, 11, 0.12);
        color: #f59e0b;
        border: 1px solid rgba(245, 158, 11, 0.3);
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.76rem;
        font-weight: 500;
        margin-top: 6px;
    }
</style>
""", unsafe_allow_html=True)


def get_indexed_documents():
    """Fetch unique documents and their chunk counts from ChromaDB."""
    try:
        client = get_chroma_client()
        collection = client.get_or_create_collection(COLLECTION_NAME)
        data = collection.get(include=["metadatas"])
        
        docs = {}
        for m in data.get("metadatas", []):
            if not m:
                continue
            doc_id = m.get("document_id")
            if not doc_id:
                continue
            if doc_id not in docs:
                docs[doc_id] = {
                    "document_id": doc_id,
                    "source": m.get("source", doc_id),
                    "source_type": m.get("source_type", "document"),
                    "chunk_count": 0
                }
            docs[doc_id]["chunk_count"] += 1
        return docs
    except Exception:
        return {}


def delete_indexed_document(document_id):
    """Delete all chunks for a document from ChromaDB."""
    try:
        client = get_chroma_client()
        collection = client.get_collection(COLLECTION_NAME)
        collection.delete(where={"document_id": document_id})
        return True
    except Exception as e:
        st.error(f"Failed to delete document: {e}")
        return False


def get_file_icon(extension):
    """Return an appropriate emoji icon based on file extension."""
    ext = str(extension).lower().lstrip(".")
    if ext == "pdf":
        return "📕"
    elif ext in ("docx", "doc"):
        return "📘"
    elif ext in ("xlsx", "xls", "csv"):
        return "📗"
    elif ext in ("pptx", "ppt"):
        return "📙"
    elif ext in ("png", "jpg", "jpeg", "webp", "tiff", "tif", "bmp", "gif"):
        return "🖼️"
    elif ext in ("json", "html", "htm", "xml"):
        return "🌐"
    else:
        return "📄"


def get_installed_ollama_models():
    """Detect available models from local Ollama service."""
    default_models = [DEFAULT_MODEL_NAME, "llama3.2:3b", "llama3.1:8b", "mistral:latest", "phi3:latest"]
    try:
        models_data = ollama.list()
        detected = []
        if hasattr(models_data, "models"):
            detected = [m.model for m in models_data.models]
        elif isinstance(models_data, dict) and "models" in models_data:
            detected = [m["name"] for m in models_data["models"]]
        
        if detected:
            if DEFAULT_MODEL_NAME not in detected:
                detected.insert(0, DEFAULT_MODEL_NAME)
            return detected
    except Exception:
        pass
    return default_models


def build_rag_prompt(query, retrieved_chunks):
    """Format prompt with context chunks and instructions for Ollama."""
    context_parts = []
    for index, chunk in enumerate(retrieved_chunks, start=1):
        metadata = chunk.get("metadata", {})
        source_location = format_source_location(metadata)
        context_parts.append(
            f"\n[Source {index} | {source_location}]\n{chunk['text']}\n"
        )

    context = "\n".join(context_parts)
    return f"""You are a universal document assistant.

Answer the user's question using ONLY the information provided in the document context below.

Rules:
1. Do not use outside knowledge.
2. Do not invent missing information.
3. If the answer is unavailable, clearly say so.
4. Preserve document placeholders exactly.
5. Keep your answer clear, well-structured, and concise.
6. Mention the relevant source location when possible.

DOCUMENT CONTEXT:
{context}

USER QUESTION:
{query}

ANSWER:
"""


# ==========================================
# INITIALIZE SESSION STATE
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "active_doc_id" not in st.session_state:
    st.session_state.active_doc_id = "all"

if "top_k_chunks" not in st.session_state:
    st.session_state.top_k_chunks = 3

if "selected_model" not in st.session_state:
    st.session_state.selected_model = DEFAULT_MODEL_NAME

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

if "stop_requested" not in st.session_state:
    st.session_state.stop_requested = False

if "is_generating" not in st.session_state:
    st.session_state.is_generating = False

if "partial_text" not in st.session_state:
    st.session_state.partial_text = ""

if "partial_sources" not in st.session_state:
    st.session_state.partial_sources = []


def request_stop_generation():
    """Callback fired immediately when user clicks the Stop generating button."""
    st.session_state.stop_requested = True
    st.session_state.is_generating = False


# ==========================================
# SAFETY RECOVERY: ENSURE CLEAN UNLOCKED STATE
# If stop button was pressed or stop was requested, finalize turn cleanly!
# ==========================================
if st.session_state.get("stop_btn") or st.session_state.get("stop_requested"):
    st.session_state.stop_requested = False
    st.session_state.is_generating = False

    # If the last message was a user message without an assistant reply, append the partial reply
    if st.session_state.messages and st.session_state.messages[-1].get("role") == "user":
        saved_reply = st.session_state.get("partial_text", "").strip() or "*(Generation stopped by user)*"
        st.session_state.messages.append({
            "role": "assistant",
            "content": saved_reply,
            "sources": st.session_state.get("partial_sources", []),
            "stopped": True
        })
    st.session_state.partial_text = ""
    st.session_state.partial_sources = []

# Core busy state: True ONLY while actively running generation!
is_busy = bool(st.session_state.get("is_generating", False))

indexed_docs = get_indexed_documents()
available_models = get_installed_ollama_models()


# ==========================================
# SIDEBAR: DOCUMENT & CHAT MANAGEMENT
# Controls locked while generating to protect consistency
# ==========================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-title">
        <span>💬 DocuAssistant</span>
    </div>
    <div class="sidebar-subtitle">Universal Document Assistant</div>
    """, unsafe_allow_html=True)
    
    # "New Chat" primary action button
    if st.button("➕ New Chat", use_container_width=True, type="primary", disabled=is_busy):
        st.session_state.messages = []
        st.session_state.stop_requested = False
        st.session_state.is_generating = False
        st.session_state.partial_text = ""
        st.session_state.partial_sources = []
        st.rerun()

    st.markdown("---")

    # Document Selection Section (Locked during generation)
    st.markdown("##### 📂 Active Document")
    
    doc_options = {"all": "🌐 All Indexed Documents (Global Scope)"}
    for doc_id, doc_info in indexed_docs.items():
        icon = get_file_icon(doc_info.get("source_type", ""))
        label = f"{icon} {doc_info.get('source', doc_id)} ({doc_info['chunk_count']} chunks)"
        doc_options[doc_id] = label

    if st.session_state.active_doc_id not in doc_options:
        st.session_state.active_doc_id = "all"

    selected_doc = st.selectbox(
        "Chat Context Scope:",
        options=list(doc_options.keys()),
        format_func=lambda x: doc_options[x],
        index=list(doc_options.keys()).index(st.session_state.active_doc_id),
        disabled=is_busy,
        help="Context switching is locked while generating a response." if is_busy else "Choose whether to search within a specific document or across all indexed files."
    )
    st.session_state.active_doc_id = selected_doc

    # Active Document Details Card
    if selected_doc != "all" and selected_doc in indexed_docs:
        active_info = indexed_docs[selected_doc]
        with st.expander("📄 Document Details", expanded=False):
            st.markdown(f"**Filename:** `{active_info['source']}`")
            st.markdown(f"**Doc ID:** `{active_info['document_id']}`")
            st.markdown(f"**Type:** `{active_info['source_type']}`")
            st.markdown(f"**Indexed Chunks:** `{active_info['chunk_count']}`")
            
            if st.button("🗑️ Remove Document", type="secondary", use_container_width=True, disabled=is_busy):
                if delete_indexed_document(selected_doc):
                    st.success(f"Removed `{active_info['source']}` from index.")
                    st.session_state.active_doc_id = "all"
                    st.rerun()

    st.markdown("---")

    # Document Upload Section
    st.markdown("##### 📤 Upload & Index Document")
    uploaded_file = st.file_uploader(
        "Add a new document:",
        type=SUPPORTED_EXTENSIONS,
        key=f"file_uploader_{st.session_state.uploader_key}",
        disabled=is_busy,
        help="Supported: PDF, Word, Excel, PowerPoint, Text, Markdown, CSV, JSON, HTML, and Images."
    )

    if uploaded_file is not None:
        upload_btn = st.button("⚡ Ingest & Process Document", type="secondary", use_container_width=True, disabled=is_busy)
        if upload_btn:
            with st.status("Processing document pipeline...", expanded=True) as status:
                try:
                    upload_dir = PROJECT_ROOT / "data" / "uploads"
                    upload_dir.mkdir(parents=True, exist_ok=True)
                    
                    saved_path = upload_dir / uploaded_file.name
                    saved_path.write_bytes(uploaded_file.getbuffer())

                    # Step 1: Parse document
                    status.update(label="[1/4] Extracting text & structure...")
                    doc = load_document(saved_path)
                    records = doc["content"]
                    if not records:
                        st.error("No readable text content extracted.")
                        status.update(label="Extraction failed", state="error")
                        st.stop()

                    for record in records:
                        record.setdefault("source", doc["filename"])
                        record.setdefault("source_type", doc["file_type"].lstrip("."))

                    # Step 2: Split into chunks
                    status.update(label=f"[2/4] Splitting into semantic chunks ({len(records)} records)...")
                    chunks = split_into_chunks(records)
                    if not chunks:
                        st.error("No chunks were generated.")
                        status.update(label="Chunking failed", state="error")
                        st.stop()

                    # Step 3: Embeddings
                    status.update(label=f"[3/4] Computing embeddings for {len(chunks)} chunks...")
                    embeddings = generate_embeddings(chunks)

                    # Step 4: ChromaDB upsert
                    status.update(label="[4/4] Storing embeddings in ChromaDB...")
                    raw_id = saved_path.stem
                    document_id = re.sub(r'[^\w\-_\.]', '_', raw_id)
                    total_stored = store_embeddings(
                        chunks=chunks,
                        embeddings=embeddings,
                        collection_name=COLLECTION_NAME,
                        document_id=document_id
                    )

                    status.update(
                        label=f"Done! {len(chunks)} chunks successfully indexed.",
                        state="complete"
                    )
                    st.session_state.active_doc_id = document_id
                    st.session_state.uploader_key += 1
                    st.rerun()

                except Exception as e:
                    status.update(label="Document ingestion failed", state="error")
                    st.error(f"Error: {str(e)}")

    st.markdown("---")

    # Settings & Model Selection
    with st.expander("⚙️ RAG Settings & Models", expanded=False):
        model_idx = 0
        if st.session_state.selected_model in available_models:
            model_idx = available_models.index(st.session_state.selected_model)
        
        st.session_state.selected_model = st.selectbox(
            "Ollama LLM Model:",
            options=available_models,
            index=model_idx,
            disabled=is_busy,
            help="Select the Ollama model to use for generating answers."
        )

        st.session_state.top_k_chunks = st.slider(
            "Top Chunks to Retrieve (k):",
            min_value=1,
            max_value=8,
            value=st.session_state.top_k_chunks,
            step=1,
            disabled=is_busy,
            help="Number of most relevant chunks passed as context to the LLM."
        )
        st.markdown("**Embedding:** `all-MiniLM-L6-v2`")
        st.markdown(f"**Indexed Documents:** `{len(indexed_docs)}`")
        total_chunks = sum(d["chunk_count"] for d in indexed_docs.values())
        st.markdown(f"**Total Chunks in DB:** `{total_chunks}`")

    # Download conversation export
    if len(st.session_state.messages) > 0:
        transcript_lines = ["# Universal Document Assistant - Chat Transcript\n"]
        transcript_lines.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        transcript_lines.append(f"**Scope:** {selected_doc}\n---\n")
        for m in st.session_state.messages:
            role = "User" if m["role"] == "user" else "Assistant"
            transcript_lines.append(f"### {role}\n{m['content']}\n")
        
        st.download_button(
            label="📥 Export Chat (.md)",
            data="\n".join(transcript_lines),
            file_name=f"chat_transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
            use_container_width=True,
            disabled=is_busy
        )


# ==========================================
# CENTRAL CONVERSATION AREA
# ==========================================

# Active Context Header (Sticky, solid non-transparent background pinned to top)
active_name = (
    "🌐 All Indexed Documents (Global Scope)"
    if st.session_state.active_doc_id == "all"
    else f"{get_file_icon(indexed_docs.get(st.session_state.active_doc_id, {}).get('source_type', ''))} {indexed_docs.get(st.session_state.active_doc_id, {}).get('source', st.session_state.active_doc_id)}"
)

st.markdown(f"""
<div class="chat-top-navbar">
    <div class="context-info" title="{active_name}">
        <span class="status-dot"></span>
        <span class="context-label">Context:</span>
        <strong class="context-name">{active_name}</strong>
    </div>
    <div class="model-pill">
        <span class="model-dot">●</span>
        <span>{st.session_state.selected_model}</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ==========================================
# EMPTY STATE OR CHAT HISTORY
# Never shows suggestions below messages!
# ==========================================
if len(st.session_state.messages) == 0:
    st.markdown("""
    <div class="hero-container">
        <div class="hero-icon">📑</div>
        <div class="hero-title">Universal Document Assistant</div>
        <div class="hero-subtitle">
            Chat with your documents using semantic search and local AI. Extract facts, summarize dense contracts, examine financial tables, or locate citations in seconds.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<p style='font-size: 0.82rem; opacity: 0.7; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;'>Suggested Questions</p>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📋 Summarize key points and takeaways", use_container_width=True, key="sug_summary"):
            st.session_state.messages.append({
                "role": "user",
                "content": "Summarize the key points, main objectives, and important takeaways from this document."
            })
            st.session_state.is_generating = True
            st.session_state.stop_requested = False
            st.session_state.partial_text = ""
            st.session_state.partial_sources = []
            st.rerun()

        if st.button("🔍 Identify critical dates, parties, and entities", use_container_width=True, key="sug_dates"):
            st.session_state.messages.append({
                "role": "user",
                "content": "List all parties, important dates, deadlines, and key entities mentioned in the document."
            })
            st.session_state.is_generating = True
            st.session_state.stop_requested = False
            st.session_state.partial_text = ""
            st.session_state.partial_sources = []
            st.rerun()

    with col2:
        if st.button("📊 Extract key numbers, tables, and metrics", use_container_width=True, key="sug_tables"):
            st.session_state.messages.append({
                "role": "user",
                "content": "Extract and tabulate key numerical figures, financial details, or statistics found in the document."
            })
            st.session_state.is_generating = True
            st.session_state.stop_requested = False
            st.session_state.partial_text = ""
            st.session_state.partial_sources = []
            st.rerun()

        if st.button("⚠️ Highlight obligations, terms, or liabilities", use_container_width=True, key="sug_terms"):
            st.session_state.messages.append({
                "role": "user",
                "content": "What are the primary obligations, liabilities, restrictions, or governing terms defined here?"
            })
            st.session_state.is_generating = True
            st.session_state.stop_requested = False
            st.session_state.partial_text = ""
            st.session_state.partial_sources = []
            st.rerun()

else:
    # Render all chat history messages
    for message in st.session_state.messages:
        avatar = "👤" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

            if message.get("stopped"):
                st.markdown("<span class='stopped-badge'>⏹️ Generation stopped</span>", unsafe_allow_html=True)

            # Display citations/sources if available
            if message.get("sources"):
                sources = message["sources"]
                with st.expander(f"📚 Sources & Citations ({len(sources)} references)", expanded=False):
                    for idx, src in enumerate(sources, 1):
                        meta = src.get("metadata", {})
                        location = format_source_location(meta)
                        distance = src.get("distance")
                        score_badge = ""
                        if distance is not None:
                            sim_pct = max(0, min(100, int((1.0 - float(distance)) * 100)))
                            score_badge = f"<span class='source-score'>{sim_pct}% match</span>"

                        safe_snippet = html.escape(src.get('text', '').strip())
                        st.markdown(f"""
                        <div class="source-card">
                            <div class="source-meta">
                                <span>Source {idx}: {location}</span>
                                {score_badge}
                            </div>
                            <div class="source-text">{safe_snippet}</div>
                        </div>
                        """, unsafe_allow_html=True)


# ==========================================
# INPUT PROCESSING
# Chat input disabled only during active generation
# ==========================================
user_input = st.chat_input(
    "Ask a question about your documents...",
    disabled=is_busy
)
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.is_generating = True
    st.session_state.stop_requested = False
    st.session_state.partial_text = ""
    st.session_state.partial_sources = []
    st.rerun()


# ==========================================
# ACTIVE GENERATION STEP
# ==========================================
if st.session_state.get("is_generating"):
    # Render Stop button in bottom dock above input
    with st.bottom:
        st.markdown('<div class="stop-button-wrapper">', unsafe_allow_html=True)
        col_s1, col_s2, col_s3 = st.columns([1, 1.4, 1])
        with col_s2:
            st.button(
                "⏹️ Stop generating",
                key="stop_btn",
                type="secondary",
                use_container_width=True,
                on_click=request_stop_generation
            )
        st.markdown('</div>', unsafe_allow_html=True)

    last_user_query = st.session_state.messages[-1]["content"]

    with st.chat_message("assistant", avatar="🤖"):
        text_placeholder = st.empty()
        target_doc_id = None if st.session_state.active_doc_id == "all" else st.session_state.active_doc_id

        was_interrupted = False
        try:
            # 1. Semantic retrieval
            retrieved_chunks = []
            with st.spinner("Searching document index..."):
                retrieved_chunks = search_documents(
                    query=last_user_query,
                    collection_name=COLLECTION_NAME,
                    top_k=st.session_state.top_k_chunks,
                    document_id=target_doc_id
                )
            st.session_state.partial_sources = retrieved_chunks

            if not retrieved_chunks:
                no_info_msg = (
                    "I couldn't find any relevant information in the selected document(s) "
                    "matching your query. Try choosing 'All Indexed Documents' or uploading additional files."
                )
                text_placeholder.markdown(no_info_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": no_info_msg,
                    "sources": [],
                    "stopped": False
                })
            else:
                prompt = build_rag_prompt(last_user_query, retrieved_chunks)
                accumulated_text = ""
                generation_stopped = False

                response_stream = ollama.chat(
                    model=st.session_state.selected_model,
                    messages=[{"role": "user", "content": prompt}],
                    stream=True
                )

                for chunk in response_stream:
                    # Check stop flag on each token chunk
                    if st.session_state.get("stop_requested"):
                        generation_stopped = True
                        break

                    delta = chunk.get("message", {}).get("content", "")
                    if delta:
                        accumulated_text += delta
                        st.session_state.partial_text = accumulated_text
                        text_placeholder.markdown(accumulated_text + " ▌")

                # Final display
                final_display = accumulated_text.strip() if accumulated_text.strip() else ("*(Generation stopped by user)*" if generation_stopped else "")
                text_placeholder.markdown(final_display)

                if generation_stopped:
                    st.markdown("<span class='stopped-badge'>⏹️ Generation stopped</span>", unsafe_allow_html=True)

                # Record completed turn
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": final_display,
                    "sources": retrieved_chunks,
                    "stopped": generation_stopped
                })

        except (StopException, RerunException, KeyboardInterrupt):
            was_interrupted = True
            saved_reply = st.session_state.get("partial_text", "").strip() or "*(Generation stopped by user)*"
            st.session_state.messages.append({
                "role": "assistant",
                "content": saved_reply,
                "sources": st.session_state.get("partial_sources", []),
                "stopped": True
            })
            raise
        except Exception as gen_err:
            err_msg = f"⚠️ Generation error: {gen_err}"
            text_placeholder.markdown(err_msg)
            st.session_state.messages.append({
                "role": "assistant",
                "content": err_msg,
                "sources": st.session_state.get("partial_sources", []),
                "stopped": True
            })
        finally:
            st.session_state.is_generating = False
            st.session_state.stop_requested = False
            st.session_state.partial_text = ""
            st.session_state.partial_sources = []
            if not was_interrupted:
                st.rerun()
