"""Configuration values for the OmniBrain Streamlit client."""

import os

# ── Backend URL ────────────────────────────────────────────────────────────────
FASTAPI_BASE_URL: str = os.getenv("OMNIBRAIN_API_URL", "http://localhost:8000").rstrip("/")
API_TIMEOUT_SECONDS: float = float(os.getenv("OMNIBRAIN_API_TIMEOUT", "600"))

# ── Supported file types ───────────────────────────────────────────────────────
SUPPORTED_FILE_TYPES: list[str] = ["pdf", "docx", "txt", "png", "jpg", "jpeg", "csv", "xlsx"]

# ── JWT / session ──────────────────────────────────────────────────────────────
SESSION_TOKEN_KEY: str = "omnibrain_token"       # st.session_state key for JWT
SESSION_USER_KEY: str = "omnibrain_user"         # st.session_state key for user info
AUTH_STORAGE_KEY: str = "omnibrain_auth_browser"  # localStorage key for session persistence
CHAT_HISTORY_KEY: str = "omnibrain_chat_history"  # browser-persisted chat history list
CURRENT_CHAT_KEY: str = "omnibrain_current_chat"  # browser-persisted active conversation id