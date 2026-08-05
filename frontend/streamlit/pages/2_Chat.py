"""
OmniBrain Chat — protected page.
All original chat logic is preserved exactly. Auth guard added at top.
"""

import uuid
from datetime import datetime

import streamlit as st

from api import ApiError, query_agent
from components import (
    inject_styles,
    load_chat_history,
    load_current_conversation_id,
    require_auth,
    render_response,
    render_sidebar,
    render_auth_topbar,
    save_active_chat_conversation,
    save_chat_history,
)
from config import CURRENT_CHAT_KEY, SESSION_TOKEN_KEY, SESSION_USER_KEY


def _conversation_title(messages: list[dict]) -> str:
    """Create a readable title for the conversation from the first user message."""
    for message in messages:
        if message.get("role") == "user":
            text = str(message.get("content", "")).strip().replace("\n", " ")
            if text:
                return text[:36] + ("..." if len(text) > 36 else "")
    return datetime.now().strftime("New Chat %H:%M")


def _save_current_conversation() -> None:
    """Persist the active conversation into the browser-backed chat history."""
    print("SAVE CONVERSATION CALLED")
    messages = st.session_state.get("messages", [])
    conversation_id = st.session_state.get("current_conversation_id")
    saved_id = save_active_chat_conversation(messages, conversation_id)
    st.session_state["current_conversation_id"] = saved_id
    st.session_state["chat_history"] = load_chat_history()


def initialize_state() -> None:
    """Create session keys used by the chat interface and restore the active conversation."""
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("uploaded_files", [])
    st.session_state.setdefault("uploaded_file_keys", set())
    st.session_state.setdefault("current_conversation_id", None)
    st.session_state.setdefault("chat_history", [])

    history = load_chat_history()
    st.session_state["chat_history"] = history

    active_id = load_current_conversation_id()
    if active_id and isinstance(active_id, str):
        for item in history:
            if item.get("id") == active_id:
                st.session_state["current_conversation_id"] = active_id
                st.session_state["messages"] = item.get("messages", [])
                return

        st.session_state["current_conversation_id"] = active_id
        st.session_state["messages"] = []
        return

    if history:
        latest = history[-1]
        st.session_state["current_conversation_id"] = latest.get("id")
        st.session_state["messages"] = latest.get("messages", [])
    else:
        st.session_state["current_conversation_id"] = f"conversation-{uuid.uuid4().hex}"


def render_chat() -> None:
    """Render conversation history and handle the next user question."""
    token = st.session_state.get(SESSION_TOKEN_KEY)
    user_info = st.session_state.get(SESSION_USER_KEY, {})
    username = user_info.get("username", "User") if user_info else "User"

    render_auth_topbar(username, include_logout=True)

    conversation_count = len(st.session_state.get("chat_history", []))
    st.markdown(
        f'<div class="topbar"><div><div class="eyebrow">OMNIBRAIN WORKSPACE</div><div class="workspace-title">Multimodal research assistant</div></div><div class="workspace-meta">{conversation_count} conversation{"s" if conversation_count != 1 else ""}</div></div>',
        unsafe_allow_html=True,
    )

    if not st.session_state.messages:
        st.markdown(
            '<div class="welcome"><div class="eyebrow">OMNIBRAIN INTERFACE</div><br><p>Ask questions across documents, spreadsheets, and visual evidence. OmniBrain retrieves the context and brings the response of the question.</p></div>',
            unsafe_allow_html=True,
        )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                render_response(message["content"])
            else:
                st.markdown(message["content"])

    query = st.chat_input("Ask OmniBrain about your documents...")
    if query is None:
        return
    query = query.strip()
    if not query:
        st.warning("Please enter a question before sending.")
        return

    if not st.session_state.get("current_conversation_id"):
        st.session_state["current_conversation_id"] = f"conversation-{uuid.uuid4().hex}"

    st.session_state.messages.append({"role": "user", "content": query})
    _save_current_conversation()
    with st.chat_message("user"):
        st.markdown(query)
    with st.chat_message("assistant"):
        with st.status("Working through your knowledge base...", expanded=True) as status:
            st.write("Analyzing query...")
            st.write("Routing request...")
            st.write("Searching knowledge base...")
            st.write("Retrieving context...")
            try:
                response = query_agent(query, token=token)
            except ApiError as exc:
                status.update(label="Request could not be completed", state="error", expanded=False)
                st.error(str(exc))
                response = None
            else:
                status.update(label="Response ready", state="complete", expanded=False)
        if response is not None:
            render_response(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            _save_current_conversation()


def main() -> None:
    """Configure and run the chat page."""
    st.set_page_config(
        page_title="OmniBrain — Chat",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    require_auth()
    initialize_state()
    inject_styles()

    token = st.session_state.get(SESSION_TOKEN_KEY)
    render_sidebar(token=token)
    render_chat()


if __name__ == "__main__":
    main()
