"""
Reusable presentation components for OmniBrain.

Original functions preserved exactly:
  - inject_styles()         ← extended with auth/dashboard CSS
  - render_sidebar()        ← unchanged
  - render_documents()      ← unchanged
  - render_images()         ← unchanged
  - render_response()       ← unchanged

New auth/UI helpers:
  - require_auth()
  - render_auth_topbar()
  - render_login_form()
  - render_register_form()
  - render_dashboard_cards()
  - toast()
"""

import json
import uuid
from datetime import datetime
from typing import Any
from urllib.parse import quote, unquote

import streamlit as st
import streamlit.components.v1 as components

from api import ApiError, check_api_status, get_current_user_info, upload_document
from config import (
    AUTH_STORAGE_KEY,
    CHAT_HISTORY_KEY,
    CURRENT_CHAT_KEY,
    SESSION_TOKEN_KEY,
    SESSION_USER_KEY,
    SUPPORTED_FILE_TYPES,
)
from utils import as_list, display_name, resolve_image_reference


# ══════════════════════════════════════════════════════════════════════════════
# STYLES
# ══════════════════════════════════════════════════════════════════════════════

def inject_styles() -> None:
    """Apply the full OmniBrain visual design system."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@300;400;500;600;700;800&display=swap');

        /* ── Tokens ─────────────────────────────────────────────────────── */
        :root {
          --bg:        #0d1117;
          --panel:     #141a22;
          --panel-2:   #1a222d;
          --ink:       #eef2f7;
          --muted:     #8d9aaa;
          --line:      #27313d;
          --accent:    #78e0c3;
          --accent-2:  #8b9cff;
          --danger:    #ff8e8e;
          --warning:   #ffd580;
          --success:   #78e0c3;
          --radius-sm: 10px;
          --radius-md: 14px;
          --radius-lg: 20px;
        }

        /* ── Base ───────────────────────────────────────────────────────── */
        html, body, [class*="css"] {
          font-family: 'Manrope', sans-serif;
          color: var(--ink);
        }
        h1, h2, h3, h4 { font-family: 'Manrope', sans-serif; letter-spacing: 0; }

        /* ── App shell ──────────────────────────────────────────────────── */
        [data-testid="stAppViewContainer"] {
          background: radial-gradient(circle at 75% -10%, #1d3040 0, #0d1117 34rem);
        }
        [data-testid="stMainBlockContainer"] {
          max-width: 1080px;
          padding-top: 1.2rem;
          padding-bottom: 6rem;
        }
        [data-testid="stHeader"] { background: transparent; }

        /* ── Sidebar ────────────────────────────────────────────────────── */
        [data-testid="stSidebar"] { background: #10161e; border-right: 1px solid var(--line); }
        [data-testid="stSidebarContent"] { padding: 1.4rem 1.15rem; }

        /* ── File uploader ──────────────────────────────────────────────── */
        [data-testid="stFileUploader"] section {
          background: var(--panel);
          border: 1px dashed #3a4857;
          border-radius: 14px;
          padding: .6rem;
        }
        [data-testid="stFileUploader"] section:hover {
          border-color: var(--accent);
          background: #17232b;
        }

        /* ── Chat messages ──────────────────────────────────────────────── */
        [data-testid="stChatMessage"] { background: transparent; border: 0; padding: 1rem 0; }
        [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] { line-height: 1.75; }
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
          background: rgba(120, 224, 195, .055);
          border: 1px solid rgba(120, 224, 195, .12);
          border-radius: 16px;
          padding: 1rem 1.15rem;
        }
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
          border-bottom: 1px solid rgba(255,255,255,.055);
        }

        /* ── Chat input ─────────────────────────────────────────────────── */
        [data-testid="stChatInput"] {
          background: rgba(20, 26, 34, .96);
          border: 1px solid #344252;
          border-radius: 18px;
          box-shadow: 0 16px 40px rgba(0,0,0,.28);
        }
        [data-testid="stChatInput"]:focus-within {
          border-color: var(--accent);
          box-shadow: 0 0 0 1px rgba(120,224,195,.18), 0 16px 40px rgba(0,0,0,.32);
        }

        /* ── Buttons ────────────────────────────────────────────────────── */
        [data-testid="stButton"] button {
          border-radius: 10px;
          border: 1px solid var(--line);
          background: var(--panel);
          color: var(--ink);
          transition: border-color .2s, transform .15s, background .2s;
        }
        [data-testid="stButton"] button:hover {
          border-color: var(--accent);
          background: #1c2a30;
          transform: translateY(-1px);
        }
        [data-testid="stButton"] button[kind="primary"] {
          background: linear-gradient(135deg, #78e0c3, #5aa4ff);
          border: none;
          color: #0d1117;
          font-weight: 700;
        }
        [data-testid="stButton"] button[kind="primary"]:hover {
          background: linear-gradient(135deg, #8aebd0, #6db5ff);
          transform: translateY(-2px);
          box-shadow: 0 8px 24px rgba(120,224,195,.25);
        }

        /* ── Inputs ─────────────────────────────────────────────────────── */
        [data-testid="stTextInput"] input,
        [data-testid="stTextInput"] input:focus {
          background: var(--panel-2) !important;
          border-color: var(--line) !important;
          color: var(--ink) !important;
          border-radius: var(--radius-sm) !important;
          transition: border-color .2s, box-shadow .2s;
        }
        [data-testid="stTextInput"] input:focus {
          border-color: var(--accent) !important;
          box-shadow: 0 0 0 1px rgba(120,224,195,.2) !important;
        }

        /* ── Expanders / status ─────────────────────────────────────────── */
        [data-testid="stExpander"] {
          background: rgba(20,26,34,.72);
          border: 1px solid var(--line);
          border-radius: 12px;
          overflow: hidden;
        }
        [data-testid="stProgressBar"] > div > div {
          background: linear-gradient(90deg, var(--accent-2), var(--accent));
        }
        [data-testid="stStatusWidget"] { border-color: var(--line); background: var(--panel); }

        /* ── Alerts ─────────────────────────────────────────────────────── */
        [data-testid="stAlert"] { border-radius: var(--radius-md) !important; }

        /* ══ BRAND / NAV ═══════════════════════════════════════════════════ */
        .brand { display: flex; align-items: center; gap: .75rem; padding: .2rem 0 1.1rem; }
        .brand-mark {
          display: inline-flex; align-items: center; justify-content: center;
          width: 40px; height: 40px; border-radius: 13px;
          background: linear-gradient(135deg, var(--accent), #5aa4ff);
          color: #0d1117; font-size: 1.25rem; font-weight: 800;
          box-shadow: 0 0 24px rgba(120,224,195,.22);
          animation: pulse-glow 3s ease-in-out infinite;
        }
        @keyframes pulse-glow {
          0%, 100% { box-shadow: 0 0 24px rgba(120,224,195,.22); }
          50%       { box-shadow: 0 0 40px rgba(120,224,195,.45); }
        }
        .brand-name { font: 800 1.28rem 'Manrope', sans-serif; }

        /* ══ TYPOGRAPHY UTILS ══════════════════════════════════════════════ */
        .eyebrow { color: var(--accent); font: 500 .67rem 'DM Mono', monospace; letter-spacing: .12em; text-transform: uppercase; }
        .subtitle { color: var(--muted); font-size: .79rem; line-height: 1.55; }
        .sidebar-section { color: #c6cfda; font-size: .72rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; margin: 1.4rem 0 .7rem; }

        /* ══ SIDEBAR STATS ═════════════════════════════════════════════════ */
        .stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: .55rem; margin: 1rem 0; }
        .stat-card { background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: .7rem .75rem; }
        .stat-value { color: var(--ink); font-size: 1.15rem; font-weight: 800; }
        .stat-label { color: var(--muted); font: .62rem 'DM Mono', monospace; margin-top: .15rem; text-transform: uppercase; }

        /* ══ STATUS PILL ═══════════════════════════════════════════════════ */
        .status-pill { display: inline-flex; align-items: center; gap: .45rem; color: var(--accent); font: 500 .72rem 'DM Mono', monospace; }
        .status-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--accent); box-shadow: 0 0 10px var(--accent); animation: blink 2s ease infinite; }
        .status-dot.offline { background: var(--danger); box-shadow: 0 0 10px var(--danger); animation: none; }
        @keyframes blink { 0%,100%{opacity:1} 50%{opacity:.45} }

        /* ══ TOPBAR ════════════════════════════════════════════════════════ */
        .topbar { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,.08); padding-bottom: 1.1rem; margin-bottom: 1.4rem; }
        .workspace-title { font-size: 1rem; font-weight: 700; }
        .workspace-meta { color: var(--muted); font: .7rem 'DM Mono', monospace; }

        /* ══ AUTH TOPBAR ═══════════════════════════════════════════════════ */
        .auth-topbar {
          display: flex; align-items: center; justify-content: space-between;
          background: rgba(20,26,34,.82); backdrop-filter: blur(12px);
          border: 1px solid var(--line); border-radius: var(--radius-md);
          padding: .65rem 1.1rem; margin-bottom: 1.6rem;
        }
        .auth-topbar .user-info { display: flex; align-items: center; gap: .6rem; }
        .auth-topbar .avatar {
          width: 32px; height: 32px; border-radius: 50%;
          background: linear-gradient(135deg, var(--accent), var(--accent-2));
          display: flex; align-items: center; justify-content: center;
          color: #0d1117; font-weight: 800; font-size: .8rem;
        }
        .auth-topbar .username { font-weight: 700; font-size: .88rem; }
        .auth-topbar .user-role { color: var(--muted); font: .67rem 'DM Mono', monospace; text-transform: uppercase; }

        /* ══ WELCOME / HERO ════════════════════════════════════════════════ */
        .welcome { max-width: 780px; padding: 6rem 0 2.4rem; }
        .welcome h1 {
          background: linear-gradient(115deg, #fff 25%, #9debd8 72%, #a8b1ff);
          -webkit-background-clip: text; background-clip: text; color: transparent;
          font-size: clamp(2.35rem, 6vw, 4.8rem); line-height: 1.04; margin: .75rem 0 1rem;
        }
        .welcome p { color: var(--muted); font-size: 1rem; max-width: 560px; line-height: 1.7; }

        /* ══ AUTH CARD (login / register) ══════════════════════════════════ */
        .auth-card {
          background: linear-gradient(160deg, rgba(26,34,45,.95), rgba(16,22,30,.95));
          border: 1px solid rgba(120,224,195,.12);
          border-radius: var(--radius-lg);
          padding: 2.4rem 2rem;
          max-width: 440px;
          margin: 4rem auto 0;
          box-shadow: 0 32px 80px rgba(0,0,0,.48), 0 0 0 1px rgba(255,255,255,.04);
          animation: card-in .4s cubic-bezier(.16,1,.3,1) both;
        }
        @keyframes card-in { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:none} }
        .auth-card-header { text-align: center; margin-bottom: 2rem; }
        .auth-card-logo {
          display: inline-flex; align-items: center; justify-content: center;
          width: 52px; height: 52px; border-radius: 16px;
          background: linear-gradient(135deg, var(--accent), #5aa4ff);
          color: #0d1117; font-size: 1.5rem; font-weight: 800; margin-bottom: 1rem;
          box-shadow: 0 0 32px rgba(120,224,195,.3);
        }
        .auth-card h2 { font-size: 1.5rem; font-weight: 800; margin: 0 0 .3rem; }
        .auth-card-sub { color: var(--muted); font-size: .82rem; }
        .auth-divider { border: none; border-top: 1px solid var(--line); margin: 1.5rem 0; }
        .auth-link { color: var(--accent); text-decoration: none; font-weight: 600; }

        /* ══ DASHBOARD CARDS ═══════════════════════════════════════════════ */
        .dash-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
          gap: 1rem;
          margin: 2rem 0;
        }
        .dash-card {
          background: linear-gradient(160deg, var(--panel) 0%, rgba(26,34,45,.8) 100%);
          border: 1px solid var(--line);
          border-radius: var(--radius-lg);
          padding: 1.6rem 1.5rem;
          cursor: pointer;
          transition: border-color .25s, transform .2s, box-shadow .25s;
          position: relative;
          overflow: hidden;
          text-decoration: none;
        }
        .dash-card::before {
          content: '';
          position: absolute; top: 0; left: 0; right: 0; height: 2px;
          background: linear-gradient(90deg, transparent, var(--accent), transparent);
          opacity: 0;
          transition: opacity .3s;
        }
        .dash-card:hover { border-color: var(--accent); transform: translateY(-3px); box-shadow: 0 20px 48px rgba(0,0,0,.32); }
        .dash-card:hover::before { opacity: 1; }
        .dash-card-icon { font-size: 1.8rem; margin-bottom: .9rem; }
        .dash-card-title { font-size: 1.05rem; font-weight: 700; margin-bottom: .4rem; }
        .dash-card-desc { color: var(--muted); font-size: .78rem; line-height: 1.55; }
        .dash-card-badge {
          display: inline-block; font: .6rem 'DM Mono', monospace;
          padding: .2rem .5rem; border-radius: 20px;
          background: rgba(139,156,255,.12); border: 1px solid rgba(139,156,255,.25);
          color: var(--accent-2); margin-top: .7rem; text-transform: uppercase;
        }

        /* ══ WELCOME BANNER ════════════════════════════════════════════════ */
        .welcome-banner {
          background: linear-gradient(135deg, rgba(120,224,195,.08), rgba(139,156,255,.06));
          border: 1px solid rgba(120,224,195,.15);
          border-radius: var(--radius-md);
          padding: 1.4rem 1.6rem;
          margin-bottom: 2rem;
          display: flex;
          align-items: center;
          gap: 1.1rem;
        }
        .welcome-banner .wb-icon { font-size: 2rem; }
        .welcome-banner .wb-title { font-size: 1.15rem; font-weight: 800; }
        .welcome-banner .wb-sub { color: var(--muted); font-size: .82rem; margin-top: .2rem; }

        /* ══ RESPONSE / SOURCE ═════════════════════════════════════════════ */
        .response-label { color: var(--accent); font: 500 .67rem 'DM Mono', monospace; letter-spacing: .12em; text-transform: uppercase; margin: 1.2rem 0 .5rem; }
        .source-item { align-items: center; border-bottom: 1px solid var(--line); display: flex; gap: .6rem; padding: .65rem 0; font-size: .84rem; }
        .source-index { color: var(--accent-2); font: .7rem 'DM Mono', monospace; }
        .file-chip { background: #1d2833; border: 1px solid #2d3b49; border-radius: 8px; color: #d2d9e2; display: inline-block; font: .72rem 'DM Mono', monospace; margin: .2rem .2rem 0 0; padding: .38rem .5rem; }
        .answer-card { background: rgba(20,26,34,.72); border: 1px solid rgba(255,255,255,.07); border-radius: 16px; padding: .15rem 1rem 1rem; }

        /* ══ UPLOAD PAGE ═══════════════════════════════════════════════════ */
        .upload-zone {
          background: linear-gradient(160deg, rgba(120,224,195,.04), rgba(139,156,255,.03));
          border: 2px dashed rgba(120,224,195,.2);
          border-radius: var(--radius-lg);
          padding: 2.5rem 2rem;
          text-align: center;
          transition: border-color .2s, background .2s;
        }
        .upload-zone:hover { border-color: rgba(120,224,195,.45); background: rgba(120,224,195,.06); }
        .upload-zone-icon { font-size: 2.5rem; margin-bottom: .8rem; }
        .upload-zone-title { font-size: 1.05rem; font-weight: 700; margin-bottom: .4rem; }
        .upload-zone-sub { color: var(--muted); font-size: .78rem; }

        /* ══ TOAST / NOTIFICATION ══════════════════════════════════════════ */
        .toast {
          padding: .7rem 1rem; border-radius: var(--radius-sm);
          font-size: .82rem; font-weight: 600;
          animation: toast-in .3s ease both;
          margin-bottom: .5rem;
        }
        @keyframes toast-in { from{opacity:0;transform:translateY(-6px)} to{opacity:1;transform:none} }
        .toast.success { background: rgba(120,224,195,.12); border: 1px solid rgba(120,224,195,.3); color: var(--accent); }
        .toast.error   { background: rgba(255,142,142,.12); border: 1px solid rgba(255,142,142,.3); color: var(--danger); }
        .toast.info    { background: rgba(139,156,255,.12); border: 1px solid rgba(139,156,255,.3); color: var(--accent-2); }

        /* ══ MISC ══════════════════════════════════════════════════════════ */
        .prompt-card { background: linear-gradient(135deg, rgba(120,224,195,.08), rgba(139,156,255,.06)); border: 1px solid rgba(120,224,195,.15); border-radius: 14px; color: #bfccd8; font-size: .78rem; margin-top: 2rem; padding: .9rem 1rem; }
        .main-shell { max-width: 980px; margin: 0 auto; padding: 1.4rem 1rem 7rem; }
        @media (max-width: 700px) {
          .main-shell { padding: .8rem .75rem 6rem; }
          .welcome { padding: 3rem 0 1.6rem; }
          .welcome h1 { font-size: 2.55rem; }
          .topbar { align-items: flex-start; flex-direction: column; gap: .4rem; }
          .auth-card { margin: 2rem .5rem 0; padding: 1.8rem 1.2rem; }
          .dash-grid { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# BROWSER STORAGE HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _query_param_key(key: str) -> str:
    """Scope query param keys to the authenticated user."""
    return f"{key}:{_browser_storage_identity()}"


def _read_query_json(key: str) -> Any | None:
    """Read a JSON value stored in Streamlit query params as a fallback."""
    raw = st.query_params.get(_query_param_key(key))
    if not raw:
        return None
    try:
        return json.loads(unquote(str(raw)))
    except (TypeError, json.JSONDecodeError):
        return None


def _write_query_json(key: str, payload: Any) -> None:
    """Write a JSON value into Streamlit query params as a fallback."""
    st.query_params[_query_param_key(key)] = quote(json.dumps(payload), safe="")


def _browser_storage_identity() -> str:
    """Build a stable user storage identity for browser-scoped keys."""
    user_info = st.session_state.get(SESSION_USER_KEY, {}) or {}
    if isinstance(user_info, dict):
        user_id = user_info.get("id")
        username = user_info.get("username")
        email = user_info.get("email")
    else:
        user_id = None
        username = None
        email = None

    if user_id is not None:
        return f"id:{_sanitize_component_key(str(user_id))}"
    if username:
        return f"username:{_sanitize_component_key(str(username))}"
    if email:
        return f"email:{_sanitize_component_key(str(email))}"
    return "anon"


def _browser_cache_key(key: str) -> str:
    """Scope in-memory browser cache entries to the authenticated user."""
    return f"_browser_cache_{key}:{_browser_storage_identity()}"


def _browser_storage_key(key: str) -> str:
    """Scope browser storage keys to the authenticated user when available."""
    return f"{key}:{_browser_storage_identity()}"


def _browser_storage_key_with_identity(key: str, identity: str) -> str:
    """Build a browser storage key for a known user identity."""
    return f"{key}:{identity}"


def _sanitize_component_key(key: str) -> str:
    return "".join(c if c.isalnum() or c in "_-" else "_" for c in key)


def _next_browser_component_key(prefix: str, key: str) -> str:
    counter_key = "_browser_storage_component_counter"
    counter = st.session_state.setdefault(counter_key, 0)
    st.session_state[counter_key] = counter + 1
    safe_key = _sanitize_component_key(key)
    return f"omnibrain_browser_storage_{prefix}_{safe_key}_{counter}"


def _browser_storage_component(ops: list[dict[str, str]], component_key: str) -> dict[str, Any]:
    payload = json.dumps(ops).replace("</", "<\\/")
    html = f"""
    <script>
      const ops = {payload};
      const result = {{ results: {{}} }};
      for (const op of ops) {{
        try {{
          if (op.type === 'read') {{
            result.results[op.key] = window.localStorage.getItem(op.key);
          }} else if (op.type === 'write') {{
            window.localStorage.setItem(op.key, op.value);
          }} else if (op.type === 'remove') {{
            window.localStorage.removeItem(op.key);
          }}
        }} catch (error) {{
          result.error = error?.toString?.() || String(error);
        }}
      }}
      const sendValue = (value) => {{
        window.parent.postMessage({{ isStreamlitMessage: true, type: 'streamlit:setComponentValue', value }}, '*');
      }};
      if (document.readyState === 'complete' || document.readyState === 'interactive') {{
        sendValue(result);
      }} else {{
        window.addEventListener('DOMContentLoaded', () => sendValue(result));
      }}
    </script>
    """

    try:
        result = components.html(html, height=0, scrolling=False, key=component_key)
    except Exception:
        result = None

    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            result = None

    return result or {}


def _browser_storage_read(key: str) -> str | None:
    component_key = _next_browser_component_key("read", key)
    result = _browser_storage_component([
        {"type": "read", "key": key}
    ], component_key)
    return result.get("results", {}).get(key)


def _browser_storage_write(key: str, value: str) -> None:
    component_key = _next_browser_component_key("write", key)
    _browser_storage_component([
        {"type": "write", "key": key, "value": value}
    ], component_key)


def _browser_storage_remove(key: str) -> None:
    component_key = _next_browser_component_key("remove", key)
    _browser_storage_component([
        {"type": "remove", "key": key}
    ], component_key)


def _read_browser_json(key: str) -> Any | None:
    """Read a JSON value from browser localStorage when available."""

    cache_key = _browser_cache_key(key)
    if cache_key in st.session_state:
        return st.session_state[cache_key]

    raw = _browser_storage_read(_browser_storage_key(key))
    if not raw:
        st.session_state[cache_key] = None
        return None

    try:
        value = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        value = None

    st.session_state[cache_key] = value
    return value


def _write_browser_json(key: str, payload: Any) -> None:
    cache_key = _browser_cache_key(key)
    st.session_state[cache_key] = payload
    _browser_storage_write(_browser_storage_key(key), json.dumps(payload))


def load_browser_json(key: str) -> Any | None:
    return _read_browser_json(key)


def save_browser_json(key: str, payload: Any) -> None:
    _write_browser_json(key, payload)


def remove_browser_key(key: str, identity: str | None = None) -> None:
    storage_key = _browser_storage_key_with_identity(key, identity or _browser_storage_identity())
    _browser_storage_remove(storage_key)
    st.session_state.pop(_browser_cache_key(key), None)


def load_chat_history() -> list[dict[str, Any]]:
    """Read the persisted chat history collection from browser storage."""
    history = _read_browser_json(CHAT_HISTORY_KEY)
    return history if isinstance(history, list) else []


def save_chat_history(history: list[dict[str, Any]]) -> None:
    """Write the current chat history collection to browser storage."""
    _write_browser_json(CHAT_HISTORY_KEY, history)


def load_current_conversation_id() -> str | None:
    """Read the active conversation id from the same browser-backed store."""
    value = _read_browser_json(CURRENT_CHAT_KEY)
    if isinstance(value, str):
        return value

    value = _read_query_json(CURRENT_CHAT_KEY)
    return value if isinstance(value, str) else None


def save_current_conversation_id(conversation_id: str | None) -> None:
    """Persist the active conversation id in the browser-backed store."""
    if conversation_id:
        _write_browser_json(CURRENT_CHAT_KEY, conversation_id)
        _write_query_json(CURRENT_CHAT_KEY, conversation_id)


def save_active_chat_conversation(messages: list[dict[str, Any]], conversation_id: str | None = None) -> str:
    """Save the current conversation to the browser-backed history store and return its id."""
    history = load_chat_history()
    if not conversation_id:
        conversation_id = f"conversation-{uuid.uuid4().hex}"

    created_at = datetime.now().isoformat(timespec="seconds")
    existing = next((item for item in history if item.get("id") == conversation_id), None)
    title = ""
    for message in messages:
        if message.get("role") == "user":
            text = str(message.get("content", "")).strip().replace("\n", " ")
            title = text[:36] + ("..." if len(text) > 36 else "")
            break
    if not title:
        title = datetime.now().strftime("New Chat %H:%M")

    if existing:
        existing["messages"] = messages
        existing["title"] = title
        existing["updated_at"] = datetime.now().isoformat(timespec="seconds")
        created_at = existing.get("created_at", created_at)
    else:
        history.append(
            {
                "id": conversation_id,
                "title": title,
                "created_at": created_at,
                "updated_at": created_at,
                "messages": messages,
            }
        )

    save_chat_history(history)
    save_current_conversation_id(conversation_id)
    return conversation_id


# ══════════════════════════════════════════════════════════════════════════════
# AUTH HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def persist_auth_state(token: str, user_info: dict[str, Any]) -> None:
    """Persist the JWT in browser query params so a refresh restores the session."""
    st.query_params[AUTH_STORAGE_KEY] = token


def clear_user_session_state() -> None:
    """Clear all in-memory state tied to the currently signed-in user."""
    for key in [
        SESSION_TOKEN_KEY,
        SESSION_USER_KEY,
        "messages",
        "uploaded_files",
        "uploaded_file_keys",
        "chat_history",
        "current_conversation_id",
        "page_uploading",
        "uploading",
        "_browser_storage_component_counter",
    ]:
        st.session_state.pop(key, None)


def clear_auth_state() -> None:
    """Remove any browser-persisted auth state."""
    browser_identity = _browser_storage_identity()
    st.query_params.pop(AUTH_STORAGE_KEY, None)
    st.query_params.pop(_query_param_key(CURRENT_CHAT_KEY), None)
    st.query_params.pop(_query_param_key(CHAT_HISTORY_KEY), None)
    st.query_params.pop(CURRENT_CHAT_KEY, None)
    st.query_params.pop(CHAT_HISTORY_KEY, None)
    for key in [SESSION_TOKEN_KEY, SESSION_USER_KEY]:
        st.session_state.pop(key, None)
    remove_browser_key(AUTH_STORAGE_KEY, browser_identity)
    remove_browser_key(CHAT_HISTORY_KEY, browser_identity)
    remove_browser_key(CURRENT_CHAT_KEY, browser_identity)


def logout_current_user() -> None:
    """Fully log out the current user and clear their session state."""
    clear_auth_state()
    clear_user_session_state()
    st.rerun()


def restore_auth_state() -> None:
    """Recover auth from browser query params, then validate the JWT before trusting it."""
    if st.session_state.get(SESSION_TOKEN_KEY):
        return

    token = st.query_params.get(AUTH_STORAGE_KEY)
    if not token:
        return

    try:
        validated_user = get_current_user_info(token)
        st.session_state[SESSION_TOKEN_KEY] = token
        st.session_state[SESSION_USER_KEY] = validated_user
    except ApiError:
        clear_auth_state()

def require_auth() -> None:
    """
    Guard helper — redirects to the login page if the user is not authenticated.
    Call at the top of any protected page.
    """
    restore_auth_state()
    if not st.session_state.get(SESSION_TOKEN_KEY):
        st.switch_page("app.py")


def toast(message: str, kind: str = "info") -> None:
    """Render a styled toast notification. kind: 'success' | 'error' | 'info'"""
    icon = {"success": "✅", "error": "❌", "info": "ℹ️"}.get(kind, "ℹ️")
    st.markdown(
        f'<div class="toast {kind}">{icon} {message}</div>',
        unsafe_allow_html=True,
    )


def render_auth_topbar(username: str, include_logout: bool = False) -> None:
    """Render the authenticated user's topbar with avatar and user info."""
    initial = username[0].upper() if username else "U"
    if include_logout:
        left_col, right_col = st.columns([9, 1])
        with left_col:
            st.markdown(
                f"""
                <div class="auth-topbar">
                  <div class="brand" style="padding:0">
                    <span class="brand-mark" style="width:32px;height:32px;font-size:1rem;border-radius:10px">O</span>
                    <span class="brand-name" style="font-size:1rem">OmniBrain</span>
                  </div>
                  <div class="user-info">
                    <div class="avatar">{initial}</div>
                    <div>
                      <div class="username">{username}</div>
                      <div class="user-role">Authenticated</div>
                    </div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with right_col:
            if st.button("Logout", use_container_width=True, key="logout_button"):
                logout_current_user()
    else:
        st.markdown(
            f"""
            <div class="auth-topbar">
              <div class="brand" style="padding:0">
                <span class="brand-mark" style="width:32px;height:32px;font-size:1rem;border-radius:10px">O</span>
                <span class="brand-name" style="font-size:1rem">OmniBrain</span>
              </div>
              <div class="user-info">
                <div class="avatar">{initial}</div>
                <div>
                  <div class="username">{username}</div>
                  <div class="user-role">Authenticated</div>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_dashboard_cards() -> None:
    """Render the quick-action card grid on the dashboard."""
    st.markdown(
        """
        <div class="dash-grid">
          <div class="dash-card">
            <div class="dash-card-icon">🧠</div>
            <div class="dash-card-title">Chat with OmniBrain</div>
            <div class="dash-card-desc">Ask questions across documents, spreadsheets, and images. The AI retrieves and synthesizes context in real time.</div>
            <div class="dash-card-badge">Multimodal RAG</div>
          </div>
          <div class="dash-card">
            <div class="dash-card-icon">📂</div>
            <div class="dash-card-title">Upload Documents</div>
            <div class="dash-card-desc">Ingest PDFs, DOCX, TXT, images, CSV, and Excel files into the knowledge base for instant retrieval.</div>
            <div class="dash-card-badge">Qdrant + PostgreSQL</div>
          </div>
          <div class="dash-card">
            <div class="dash-card-icon">🕒</div>
            <div class="dash-card-title">Previous Chats</div>
            <div class="dash-card-desc">Your conversation history will appear here in a future release.</div>
            <div class="dash-card-badge" style="background:rgba(255,213,128,.08);border-color:rgba(255,213,128,.2);color:var(--warning)">Coming Soon</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR (original — preserved exactly)
# ══════════════════════════════════════════════════════════════════════════════

def render_sidebar(token: str | None = None) -> None:
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
                        result = upload_document(item, item.name, item.type, token=token)
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
        if st.button("➕ New Chat", use_container_width=True, type="secondary"):
            current_messages = st.session_state.get("messages", [])
            current_conversation_id = st.session_state.get("current_conversation_id")
            if current_conversation_id:
                save_active_chat_conversation(current_messages, current_conversation_id)
            st.session_state["messages"] = []
            st.session_state["current_conversation_id"] = f"conversation-{uuid.uuid4().hex}"
            save_current_conversation_id(st.session_state["current_conversation_id"])
            st.rerun()
        if st.button("🕘 Chat History", use_container_width=True, type="secondary"):
            st.switch_page("pages/5_Chat_History.py")
        st.divider()
        if st.button("Clear conversation", use_container_width=True, type="secondary"):
            current_messages = st.session_state.get("messages", [])
            current_conversation_id = st.session_state.get("current_conversation_id")
            if current_conversation_id:
                save_active_chat_conversation(current_messages, current_conversation_id)
            st.session_state["messages"] = []
            st.session_state["current_conversation_id"] = f"conversation-{uuid.uuid4().hex}"
            save_current_conversation_id(st.session_state["current_conversation_id"])
            st.rerun()
        st.divider()
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            logout_current_user()


# ══════════════════════════════════════════════════════════════════════════════
# RESPONSE RENDERING (original — preserved exactly)
# ══════════════════════════════════════════════════════════════════════════════

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
    render_documents(response.get("documents"))
    render_images(response.get("images"))
