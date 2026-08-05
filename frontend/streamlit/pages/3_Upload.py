"""
OmniBrain Upload — protected dedicated upload page.
Provides a full-page upload experience in addition to the sidebar uploader.
"""

import streamlit as st

from api import ApiError, upload_document, check_api_status
from components import inject_styles, require_auth, render_auth_topbar, toast
from config import SESSION_TOKEN_KEY, SESSION_USER_KEY, SUPPORTED_FILE_TYPES


# Friendly labels for file types
FILE_TYPE_INFO: dict[str, tuple[str, str]] = {
    "pdf":  ("📄", "PDF Document"),
    "docx": ("📝", "Word Document"),
    "txt":  ("📃", "Plain Text"),
    "png":  ("🖼️",  "PNG Image"),
    "jpg":  ("🖼️",  "JPG Image"),
    "jpeg": ("🖼️",  "JPEG Image"),
    "csv":  ("📊", "CSV Spreadsheet"),
    "xlsx": ("📊", "Excel Spreadsheet"),
}


def render_upload_page() -> None:
    """Render the dedicated upload interface."""
    token = st.session_state.get(SESSION_TOKEN_KEY)
    user_info = st.session_state.get(SESSION_USER_KEY, {})
    username = user_info.get("username", "User") if user_info else "User"

    render_auth_topbar(username, include_logout=True)

    # Header
    st.markdown(
        """
        <div class="topbar">
          <div>
            <div class="eyebrow">KNOWLEDGE BASE</div>
            <div class="workspace-title">Upload Documents</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # API status check
    api_online = check_api_status()
    if not api_online:
        st.error("⚠️ The OmniBrain backend is offline. Please start the FastAPI server before uploading.")

    # Supported types display
    st.markdown('<div class="eyebrow" style="margin: 1.2rem 0 .6rem">SUPPORTED FORMATS</div>', unsafe_allow_html=True)
    chips_html = "".join(
        f'<span class="file-chip">{icon} .{ext}</span>'
        for ext, (icon, _) in FILE_TYPE_INFO.items()
    )
    st.markdown(chips_html, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Upload zone visual header
    st.markdown(
        """
        <div class="upload-zone">
          <div class="upload-zone-icon">☁️</div>
          <div class="upload-zone-title">Drop files here or click to browse</div>
          <div class="upload-zone-sub">Files are processed in the background — ingestion starts immediately after upload.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Actual Streamlit uploader
    uploaded = st.file_uploader(
        "Select files to upload",
        type=SUPPORTED_FILE_TYPES,
        accept_multiple_files=True,
        disabled=not api_online or st.session_state.get("page_uploading", False),
        label_visibility="collapsed",
    )

    uploaded_keys = st.session_state.setdefault("uploaded_file_keys", set())

    if uploaded:
        pending = [f for f in uploaded if (f.name, f.size) not in uploaded_keys]
        if pending:
            st.session_state["page_uploading"] = True
            progress_bar = st.progress(0, text=f"Uploading 0 of {len(pending)} files...")
            results_col, _ = st.columns([3, 1])

            successes, failures = [], []

            for i, file in enumerate(pending, start=1):
                progress_bar.progress(i / len(pending), text=f"Uploading {file.name} ({i}/{len(pending)})...")
                try:
                    result = upload_document(file, file.name, file.type, token=token)
                    if result.get("success", True):
                        uploaded_keys.add((file.name, file.size))
                        st.session_state.setdefault("uploaded_files", []).append(file.name)
                        successes.append(file.name)
                    else:
                        failures.append((file.name, result.get("message", "Unknown error")))
                except ApiError as exc:
                    failures.append((file.name, str(exc)))

            progress_bar.empty()
            st.session_state["page_uploading"] = False

            if successes:
                st.success(f"✅ {len(successes)} file(s) uploaded and ingestion started: {', '.join(successes)}")
            for fname, err_msg in failures:
                st.error(f"❌ {fname}: {err_msg}")

    # Uploaded this session
    uploaded_files = st.session_state.get("uploaded_files", [])
    if uploaded_files:
        st.markdown("---")
        st.markdown('<div class="eyebrow" style="margin-bottom:.8rem">UPLOADED THIS SESSION</div>', unsafe_allow_html=True)
        cols = st.columns(4)
        for idx, fname in enumerate(uploaded_files):
            ext = fname.rsplit(".", 1)[-1].lower() if "." in fname else ""
            icon, label = FILE_TYPE_INFO.get(ext, ("📁", "File"))
            with cols[idx % 4]:
                st.markdown(
                    f'<div class="stat-card" style="text-align:center;padding:.9rem .5rem">'
                    f'<div style="font-size:1.4rem">{icon}</div>'
                    f'<div style="font-size:.7rem;color:#8d9aaa;margin-top:.4rem;word-break:break-all">{fname}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="text-align:center;padding:2rem;color:#8d9aaa;font-size:.84rem">
              No files uploaded yet in this session.<br>
              <span style="font-size:.75rem">Files uploaded here are immediately ingested into the knowledge base.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Navigation footer
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Dashboard", use_container_width=True):
            st.switch_page("pages/1_Dashboard.py")
    with col2:
        if st.button("🧠 Go to Chat", use_container_width=True, type="primary"):
            st.switch_page("pages/2_Chat.py")


def main() -> None:
    st.set_page_config(
        page_title="OmniBrain — Upload",
        page_icon="📂",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    require_auth()
    inject_styles()
    render_upload_page()


if __name__ == "__main__":
    main()
