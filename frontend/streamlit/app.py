"""
OmniBrain Streamlit entry point — Login page.

If the user already has a valid JWT in session_state, they are redirected
directly to the Dashboard. Otherwise, this page renders the Login form.
"""

import streamlit as st

from api import ApiError, login_user, get_current_user_info
from components import clear_auth_state, inject_styles, persist_auth_state, restore_auth_state, toast
from config import SESSION_TOKEN_KEY, SESSION_USER_KEY

def initialize_state() -> None:
    """Ensure session keys exist on first load."""
    st.session_state.setdefault(SESSION_TOKEN_KEY, None)
    st.session_state.setdefault(SESSION_USER_KEY, None)
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("uploaded_files", [])
    st.session_state.setdefault("uploaded_file_keys", set())
    restore_auth_state()

def render_login() -> None:
    """Render the login form card."""
    st.markdown(
        """
        <div class="auth-card">
          <div class="auth-card-header">
            <div class="auth-card-logo">O</div>
            <h2>Welcome back</h2>
            <p class="auth-card-sub">Sign in to your OmniBrain workspace</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Use a container for the form so it sits visually inside the card
    with st.container():
        st.markdown("<br>", unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input(
                "Username",
                placeholder="Enter your username",
                key="login_username",
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                key="login_password",
            )
            col1, col2 = st.columns([3, 1])
            with col1:
                submitted = st.form_submit_button(
                    "Sign In →",
                    use_container_width=True,
                    type="primary",
                )
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)

        if submitted:
            if not username.strip() or not password:
                st.error("Please enter both username and password.")
            else:
                with st.spinner("Authenticating..."):
                    try:
                        token_data = login_user(username.strip(), password)
                        token = token_data["access_token"]

                        # Fetch user info to store in session
                        user_info = get_current_user_info(token)

                        st.session_state[SESSION_TOKEN_KEY] = token
                        st.session_state[SESSION_USER_KEY] = user_info
                        persist_auth_state(token, user_info)

                        st.success(f"Welcome back, {user_info.get('username', username)}! Redirecting...")
                        st.switch_page("pages/1_Dashboard.py")

                    except ApiError as exc:
                        st.error(str(exc))

        st.markdown(
            '<hr class="auth-divider"><p style="text-align:center;font-size:.84rem;color:#8d9aaa">'
            'New to OmniBrain? <a class="auth-link" href="Register">Create an account</a></p>',
            unsafe_allow_html=True,
        )

def main() -> None:
    """Configure and run the login entry page."""
    st.set_page_config(
        page_title="OmniBrain — Sign In",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    initialize_state()
    inject_styles()

    # If already authenticated, go straight to dashboard
    if st.session_state.get(SESSION_TOKEN_KEY):
        st.switch_page("pages/1_Dashboard.py")

    # Hero left, form right
    col_left, col_form = st.columns([1.08, 0.92])
    with col_left:
        st.markdown(
            """
            <div style="padding:5.5rem 0 2rem; max-width:520px;">
              <div class="eyebrow" style="margin-bottom:.8rem">OMNIBRAIN</div>
              <h1 style="background:linear-gradient(115deg,#fff 25%,#9debd8 72%,#a8b1ff);
                         -webkit-background-clip:text;background-clip:text;color:transparent;
                         font-size:clamp(2.4rem,5.2vw,4.4rem);line-height:1.05;margin:0 0 1rem">
                Your AI<br>knowledge<br>workspace
              </h1>
              <p style="color:#8d9aaa;font-size:.95rem;line-height:1.7;max-width:360px;margin:0 0 1.6rem">
                Multimodal RAG assistant with LangGraph orchestration.
                Ask questions across PDFs, spreadsheets, images, and databases.
              </p>
              <div style="display:flex;flex-direction:column;gap:.6rem">
                <div style="display:flex;align-items:center;gap:.6rem;color:#c6cfda;font-size:.84rem">
                  <span style="color:#78e0c3">✦</span> Semantic document search
                </div>
                <div style="display:flex;align-items:center;gap:.6rem;color:#c6cfda;font-size:.84rem">
                  <span style="color:#78e0c3">✦</span> SQL agent for tabular data
                </div>
                <div style="display:flex;align-items:center;gap:.6rem;color:#c6cfda;font-size:.84rem">
                  <span style="color:#78e0c3">✦</span> Vision agent for images
                </div>
                <div style="display:flex;align-items:center;gap:.6rem;color:#c6cfda;font-size:.84rem">
                  <span style="color:#78e0c3">✦</span> JWT-secured workspace
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_form:
        render_login()


if __name__ == "__main__":
    main()