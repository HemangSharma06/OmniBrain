"""
OmniBrain Chat History — protected page.
Displays saved conversations from browser storage and reopens them in the chat page.
"""

import streamlit as st

from components import inject_styles, load_chat_history, require_auth, render_auth_topbar, save_current_conversation_id
from config import CURRENT_CHAT_KEY, SESSION_TOKEN_KEY, SESSION_USER_KEY


def render_chat_history() -> None:
    """Render a list of saved conversations for reopening."""
    token = st.session_state.get(SESSION_TOKEN_KEY)
    user_info = st.session_state.get(SESSION_USER_KEY, {})
    username = user_info.get("username", "User") if user_info else "User"
    history = load_chat_history()

    render_auth_topbar(username, include_logout=True)
    st.markdown(
        '<div class="topbar"><div><div class="eyebrow">OMNIBRAIN WORKSPACE</div><div class="workspace-title">Chat history</div></div><div class="workspace-meta">{0} saved conversation{1}</div></div>'.format(
            len(history), "s" if len(history) != 1 else ""
        ),
        unsafe_allow_html=True,
    )

    if not history:
        st.info("No saved conversations yet. Start a chat and it will appear here.")
        if st.button("Go to Chat", use_container_width=True, type="primary"):
            st.switch_page("pages/2_Chat.py")
        return

    for index, item in enumerate(history):
        conversation_id = item.get("id")
        title = item.get("title") or f"Conversation {index + 1}"
        created_at = item.get("created_at") or "Unknown time"
        with st.container():
            st.markdown(
                f"""
                <div class="dash-card" style="margin-bottom:.8rem;padding:1rem 1.1rem">
                  <div class="dash-card-title">{title}</div>
                  <div class="dash-card-desc">Created: {created_at}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Open conversation", key=f"open_history_{conversation_id}_{index}", use_container_width=True):
                st.session_state["current_conversation_id"] = conversation_id
                st.session_state["messages"] = item.get("messages", [])
                save_current_conversation_id(conversation_id)
                st.switch_page("pages/2_Chat.py")


def main() -> None:
    """Configure and render the chat history page."""
    st.set_page_config(
        page_title="OmniBrain — Chat History",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    require_auth()
    inject_styles()
    render_chat_history()


if __name__ == "__main__":
    main()
