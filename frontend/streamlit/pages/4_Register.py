"""
OmniBrain Register — public page for new account creation.
On success: auto-logs in and redirects to Dashboard.
"""

import streamlit as st

from api import ApiError, register_user, login_user, get_current_user_info
from components import clear_auth_state, inject_styles, persist_auth_state, restore_auth_state
from config import SESSION_TOKEN_KEY, SESSION_USER_KEY


def validate_inputs(username: str, email: str, password: str, confirm: str) -> list[str]:
    """Return a list of validation error messages (empty = valid)."""
    errors = []
    if len(username) < 3:
        errors.append("Username must be at least 3 characters.")
    if not all(c.isalnum() or c in "_-" for c in username):
        errors.append("Username may only contain letters, numbers, underscores, or hyphens.")
    if "@" not in email or "." not in email.split("@")[-1]:
        errors.append("Please enter a valid email address.")
    if len(password) < 8:
        errors.append("Password must be at least 8 characters.")
    if password != confirm:
        errors.append("Passwords do not match.")
    return errors


def render_register() -> None:
    """Render the registration form card."""
    st.markdown(
        """
        <div class="auth-card">
          <div class="auth-card-header">
            <div class="auth-card-logo">O</div>
            <h2>Create account</h2>
            <p class="auth-card-sub">Join OmniBrain and start exploring your knowledge base</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
        st.markdown("<br>", unsafe_allow_html=True)

        with st.form("register_form", clear_on_submit=False):
            username = st.text_input(
                "Username",
                placeholder="3–50 characters, letters / numbers / _ / -",
                key="reg_username",
            )
            email = st.text_input(
                "Email address",
                placeholder="you@example.com",
                key="reg_email",
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Minimum 8 characters",
                key="reg_password",
            )
            confirm = st.text_input(
                "Confirm password",
                type="password",
                placeholder="Re-enter your password",
                key="reg_confirm",
            )

            submitted = st.form_submit_button(
                "Create Account →",
                use_container_width=True,
                type="primary",
            )

        if submitted:
            errors = validate_inputs(
                username.strip(), email.strip(), password, confirm
            )
            if errors:
                for err in errors:
                    st.error(err)
            else:
                with st.spinner("Creating your account..."):
                    try:
                        # Register
                        register_user(username.strip(), email.strip(), password)

                        # Auto-login
                        token_data = login_user(username.strip(), password)
                        token = token_data["access_token"]
                        user_info = get_current_user_info(token)

                        st.session_state[SESSION_TOKEN_KEY] = token
                        st.session_state[SESSION_USER_KEY] = user_info
                        persist_auth_state(token, user_info)

                        st.success(f"Account created! Welcome to OmniBrain, {username}!")
                        st.switch_page("pages/1_Dashboard.py")

                    except ApiError as exc:
                        st.error(str(exc))

        st.markdown(
            '<hr class="auth-divider"><p style="text-align:center;font-size:.84rem;color:#8d9aaa">'
            'Already have an account? <a class="auth-link" href="/">Sign in</a></p>',
            unsafe_allow_html=True,
        )


def main() -> None:
    st.set_page_config(
        page_title="OmniBrain — Register",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    inject_styles()
    restore_auth_state()

    # If already authenticated, skip to dashboard
    if st.session_state.get(SESSION_TOKEN_KEY):
        st.switch_page("pages/1_Dashboard.py")

    col_left, col_form, col_right = st.columns([1, 1.4, 1])
    with col_left:
        st.markdown(
            """
            <div style="padding:6rem 0 2rem">
              <div class="eyebrow" style="margin-bottom:.8rem">OMNIBRAIN</div>
              <h1 style="background:linear-gradient(115deg,#fff 25%,#9debd8 72%,#a8b1ff);
                         -webkit-background-clip:text;background-clip:text;color:transparent;
                         font-size:clamp(2rem,5vw,3.8rem);line-height:1.1;margin:0 0 1rem">
                Start your<br>knowledge<br>journey
              </h1>
              <p style="color:#8d9aaa;font-size:.9rem;line-height:1.7;max-width:320px">
                Create a free account and get instant access to the full
                OmniBrain multimodal RAG platform.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_form:
        render_register()


if __name__ == "__main__":
    main()
