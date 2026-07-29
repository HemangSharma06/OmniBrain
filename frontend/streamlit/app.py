import streamlit as st

from api import ApiError, query_agent
from components import inject_styles, render_response, render_sidebar


def initialize_state() -> None:
    """Create session keys used by the chat interface."""
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("uploaded_files", [])
    st.session_state.setdefault("uploaded_file_keys", set())


def render_chat() -> None:
    """Render conversation history and handle the next user question."""
    conversation_count = len(st.session_state.messages) // 2
    st.markdown(
        f'<div class="topbar"><div><div class="eyebrow">OMNIBRAIN WORKSPACE</div><div class="workspace-title">Multimodal research assistant</div></div>',
        unsafe_allow_html=True,
    )
    if not st.session_state.messages:
        st.markdown(
            '<div class="welcome"><div class="eyebrow">OMNIBRAIN INTERFACE</div><br><p>Ask the questions across documents, spreadsheets, and visual evidence. OmniBrain retrieves the context and brings the response of the question.</p></div>',
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

    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)
    with st.chat_message("assistant"):
        with st.status("Working through your knowledge base...", expanded=True) as status:
            st.write("Analyzing query...")
            st.write("Routing request...")
            st.write("Searching knowledge base...")
            st.write("Retrieving context...")
            try:
                response = query_agent(query)
            except ApiError as exc:
                status.update(label="Request could not be completed", state="error", expanded=False)
                st.error(str(exc))
                response = None
            else:
                status.update(label="Response ready", state="complete", expanded=False)
        if response is not None:
            render_response(response)
            st.session_state.messages.append({"role": "assistant", "content": response})


def main() -> None:
    """Configure and run the Streamlit application."""
    st.set_page_config(page_title="OmniBrain", page_icon="O", layout="wide", initial_sidebar_state="expanded")
    initialize_state()
    inject_styles()
    render_sidebar()
    render_chat()


if __name__ == "__main__":
    main()