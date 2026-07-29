"""Reusable presentation components for OmniBrain."""

from typing import Any

import streamlit as st

from api import ApiError, check_api_status, upload_document
from config import SUPPORTED_FILE_TYPES
from utils import as_list, display_name, resolve_image_reference


def inject_styles() -> None:
    """Apply the application visual system."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
        :root { --bg: #0d1117; --panel: #141a22; --panel-2: #1a222d; --ink: #eef2f7; --muted: #8d9aaa; --line: #27313d; --accent: #78e0c3; --accent-2: #8b9cff; --danger: #ff8e8e; }
        html, body, [class*="css"] { font-family: 'Manrope', sans-serif; color: var(--ink); }
        h1, h2, h3, h4 { font-family: 'Manrope', sans-serif; letter-spacing: 0; }
        [data-testid="stAppViewContainer"] { background: radial-gradient(circle at 75% -10%, #1d3040 0, #0d1117 34rem); }
        [data-testid="stMainBlockContainer"] { max-width: 1080px; padding-top: 1.2rem; padding-bottom: 6rem; }
        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stSidebar"] { background: #10161e; border-right: 1px solid var(--line); }
        [data-testid="stSidebarContent"] { padding: 1.4rem 1.15rem; }
        [data-testid="stFileUploader"] section { background: var(--panel); border: 1px dashed #3a4857; border-radius: 14px; padding: .6rem; }
        [data-testid="stFileUploader"] section:hover { border-color: var(--accent); background: #17232b; }
        [data-testid="stChatMessage"] { background: transparent; border: 0; padding: 1rem 0; }
        [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] { line-height: 1.75; }
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) { background: rgba(120, 224, 195, .055); border: 1px solid rgba(120, 224, 195, .12); border-radius: 16px; padding: 1rem 1.15rem; }
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) { border-bottom: 1px solid rgba(255,255,255,.055); }
        [data-testid="stChatInput"] { background: rgba(20, 26, 34, .96); border: 1px solid #344252; border-radius: 18px; box-shadow: 0 16px 40px rgba(0,0,0,.28); }
        [data-testid="stChatInput"]:focus-within { border-color: var(--accent); box-shadow: 0 0 0 1px rgba(120,224,195,.18), 0 16px 40px rgba(0,0,0,.32); }
        [data-testid="stButton"] button { border-radius: 10px; border: 1px solid var(--line); background: var(--panel); color: var(--ink); transition: border-color .2s, transform .2s, background .2s; }
        [data-testid="stButton"] button:hover { border-color: var(--accent); background: #1c2a30; transform: translateY(-1px); }
        [data-testid="stExpander"] { background: rgba(20,26,34,.72); border: 1px solid var(--line); border-radius: 12px; overflow: hidden; }
        [data-testid="stProgressBar"] > div > div { background: linear-gradient(90deg, var(--accent-2), var(--accent)); }
        [data-testid="stStatusWidget"] { border-color: var(--line); background: var(--panel); }
        .brand { display: flex; align-items: center; gap: .75rem; padding: .2rem 0 1.1rem; }
        .brand-mark { display: inline-flex; align-items: center; justify-content: center; width: 40px; height: 40px; border-radius: 13px; background: linear-gradient(135deg, var(--accent), #5aa4ff); color: #0d1117; font-size: 1.25rem; font-weight: 800; box-shadow: 0 0 24px rgba(120,224,195,.22); }
        .brand-name { font: 800 1.28rem 'Manrope', sans-serif; }
        .eyebrow { color: var(--accent); font: 500 .67rem 'DM Mono', monospace; letter-spacing: .12em; text-transform: uppercase; }
        .subtitle { color: var(--muted); font-size: .79rem; line-height: 1.55; }
        .sidebar-section { color: #c6cfda; font-size: .72rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; margin: 1.4rem 0 .7rem; }
        .stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: .55rem; margin: 1rem 0; }
        .stat-card { background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: .7rem .75rem; }
        .stat-value { color: var(--ink); font-size: 1.15rem; font-weight: 800; }
        .stat-label { color: var(--muted); font: .62rem 'DM Mono', monospace; margin-top: .15rem; text-transform: uppercase; }
        .status-pill { display: inline-flex; align-items: center; gap: .45rem; color: var(--accent); font: 500 .72rem 'DM Mono', monospace; }
        .status-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--accent); box-shadow: 0 0 10px var(--accent); }
        .status-dot.offline { background: var(--danger); box-shadow: 0 0 10px var(--danger); }
        .main-shell { max-width: 980px; margin: 0 auto; padding: 1.4rem 1rem 7rem; }
        .topbar { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,.08); padding-bottom: 1.1rem; }
        .workspace-title { font-size: 1rem; font-weight: 700; }
        .workspace-meta { color: var(--muted); font: .7rem 'DM Mono', monospace; }
        .welcome { max-width: 780px; padding: 6rem 0 2.4rem; }
        .welcome h1 { background: linear-gradient(115deg, #fff 25%, #9debd8 72%, #a8b1ff); -webkit-background-clip: text; background-clip: text; color: transparent; font-size: clamp(2.35rem, 6vw, 4.8rem); line-height: 1.04; margin: .75rem 0 1rem; }
        .welcome p { color: var(--muted); font-size: 1rem; max-width: 560px; line-height: 1.7; }
        .prompt-card { background: linear-gradient(135deg, rgba(120,224,195,.08), rgba(139,156,255,.06)); border: 1px solid rgba(120,224,195,.15); border-radius: 14px; color: #bfccd8; font-size: .78rem; margin-top: 2rem; padding: .9rem 1rem; }
        .response-label { color: var(--accent); font: 500 .67rem 'DM Mono', monospace; letter-spacing: .12em; text-transform: uppercase; margin: 1.2rem 0 .5rem; }
        .source-item { align-items: center; border-bottom: 1px solid var(--line); display: flex; gap: .6rem; padding: .65rem 0; font-size: .84rem; }
        .source-index { color: var(--accent-2); font: .7rem 'DM Mono', monospace; }
        .file-chip { background: #1d2833; border: 1px solid #2d3b49; border-radius: 8px; color: #d2d9e2; display: inline-block; font: .72rem 'DM Mono', monospace; margin: .2rem .2rem 0 0; padding: .38rem .5rem; }
        .answer-card { background: rgba(20,26,34,.72); border: 1px solid rgba(255,255,255,.07); border-radius: 16px; padding: .15rem 1rem 1rem; }
        @media (max-width: 700px) { .main-shell { padding: .8rem .75rem 6rem; } .welcome { padding: 3rem 0 1.6rem; } .welcome h1 { font-size: 2.55rem; } .topbar { align-items: flex-start; flex-direction: column; gap: .4rem; } }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    """Render branding, document upload controls, and chat reset."""
    with st.sidebar:
        st.markdown('<div class="brand"><span class="brand-mark">O</span><span class="brand-name">OmniBrain</span></div>', unsafe_allow_html=True)
        api_online = check_api_status()
        status_class = "" if api_online else "offline"
        status_text = "Backend connected" if api_online else "Backend offline"
        st.markdown(f'<div class="status-pill"><span class="status-dot {status_class}"></span>{status_text}</div>', unsafe_allow_html=True)
        st.divider()
        st.markdown('<div class="sidebar-section">Knowledge base</div>', unsafe_allow_html=True)
        uploads = st.file_uploader(
            "Add documents or images",
            type=SUPPORTED_FILE_TYPES,
            accept_multiple_files=True,
            disabled=st.session_state.get("uploading", False),
            help="PDF, DOCX, TXT, PNG, JPG, JPEG, CSV, and XLSX files are supported.",
        )
        uploaded_keys = st.session_state.setdefault("uploaded_file_keys", set())
        if uploads:
            pending = [item for item in uploads if (item.name, item.size) not in uploaded_keys]
            if pending:
                st.session_state["uploading"] = True
                progress = st.progress(0, text="Preparing uploads...")
                for index, item in enumerate(pending, start=1):
                    try:
                        result = upload_document(item, item.name, item.type)
                        if result.get("success", True):
                            uploaded_keys.add((item.name, item.size))
                            st.session_state.setdefault("uploaded_files", []).append(item.name)
                            st.success(f"{item.name} uploaded")
                        else:
                            st.error(result.get("message", f"Upload failed for {item.name}"))
                    except ApiError as exc:
                        st.error(f"{item.name}: {exc}")
                    progress.progress(index / len(pending), text=f"Uploaded {index} of {len(pending)}")
                progress.empty()
                st.session_state["uploading"] = False

        uploaded_files = st.session_state.get("uploaded_files", [])
        if uploaded_files:
            st.markdown('<div class="sidebar-section">Uploaded this session</div>', unsafe_allow_html=True)
            for filename in uploaded_files:
                st.markdown(f'<span class="file-chip">{filename}</span>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="stat-grid"><div class="stat-card"><div class="stat-value">{len(uploaded_files)}</div><div class="stat-label">Documents</div></div><div class="stat-card"><div class="stat-value">{len(st.session_state.get("messages", [])) // 2}</div><div class="stat-label">Conversations</div></div></div>',
            unsafe_allow_html=True,
        )
        st.divider()
        if st.button("Clear conversation", use_container_width=True, type="secondary"):
            st.session_state["messages"] = []
            st.rerun()


# def render_sources(sources: Any) -> None:
#     """Render source references in a compact expandable section."""
#     source_items = as_list(sources)
#     if not source_items:
#         return
#     with st.expander(f"Sources  /  {len(source_items)} references", expanded=False):
#         for source in source_items:
#             page = source.get("page") if isinstance(source, dict) else None
#             page_label = f" | page {page}" if page else ""
#             st.markdown(f'<div class="source-item"><span class="source-index">REF</span><span>{display_name(source)}{page_label}</span></div>', unsafe_allow_html=True)


def render_documents(documents: Any) -> None:
    """Render retrieved document names when returned by the API."""
    document_items = as_list(documents)
    if not document_items:
        return
    st.markdown('<div class="response-label">Documents</div>', unsafe_allow_html=True)
    for document in document_items:
        st.markdown(f"- {display_name(document)}")


def render_images(images: Any) -> None:
    """Render referenced images, skipping paths unavailable to the frontend."""
    image_items = as_list(images)
    if not image_items:
        return
    st.markdown('<div class="response-label">Referenced images</div>', unsafe_allow_html=True)
    for image in image_items:
        reference = resolve_image_reference(image)
        if reference:
            st.image(reference, caption=display_name(image), use_container_width=True)
        else:
            st.caption(f"Image unavailable: {display_name(image)}")


def render_response(response: dict[str, Any]) -> None:
    """Render an assistant answer and all optional retrieval metadata."""
    answer = response.get("answer") or "No answer was returned by the agent."
    st.markdown(answer)
    # render_sources(response.get("sources"))
    render_documents(response.get("documents"))
    render_images(response.get("images"))
    # with st.expander("Agent thought process", expanded=False):
    #     thought_process = response.get("thought_process")
    #     st.write(thought_process or "Thought process unavailable.")
