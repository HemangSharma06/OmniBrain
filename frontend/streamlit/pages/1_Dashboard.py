"""
OmniBrain Dashboard — protected page.
Requires authentication. Redirects to login if no JWT found.
"""

import streamlit as st
from datetime import datetime

from components import inject_styles, require_auth, render_auth_topbar, render_dashboard_cards
from config import SESSION_TOKEN_KEY, SESSION_USER_KEY


def render_dashboard() -> None:
    """Render the main dashboard with welcome banner and quick-action cards."""
    user_info = st.session_state.get(SESSION_USER_KEY, {})
    username = user_info.get("username", "User") if user_info else "User"
    token = st.session_state.get(SESSION_TOKEN_KEY, "")

    inject_styles()
    render_auth_topbar(username, include_logout=True)

    # Welcome banner
    hour = datetime.now().hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
    st.markdown(
        f"""
        <div class="welcome-banner">
          <div class="wb-icon">🧠</div>
          <div>
            <div class="wb-title">{greeting}, {username}!</div>
            <div class="wb-sub">Your OmniBrain workspace is ready. What would you like to explore today?</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Quick action cards (visual only — navigation via sidebar)
    st.markdown('<div class="eyebrow" style="margin-bottom:.5rem">QUICK ACTIONS</div>', unsafe_allow_html=True)
    render_dashboard_cards()

    # Navigation buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🧠 Chat with OmniBrain", use_container_width=True, type="primary"):
            st.switch_page("pages/2_Chat.py")
    with col2:
        if st.button("📂 Upload Documents", use_container_width=True):
            st.switch_page("pages/3_Upload.py")
    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            logout_current_user()

    # Session info footer
    st.markdown("<br>", unsafe_allow_html=True)
    msg_count = len(st.session_state.get("messages", [])) // 2
    doc_count = len(st.session_state.get("uploaded_files", []))

    st.markdown(
        f"""
        <div class="stat-grid" style="max-width:400px">
          <div class="stat-card">
            <div class="stat-value">{doc_count}</div>
            <div class="stat-label">Documents this session</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{msg_count}</div>
            <div class="stat-label">Conversations</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(
        page_title="OmniBrain — Dashboard",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    require_auth()
    render_dashboard()


if __name__ == "__main__":
    main()
