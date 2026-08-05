"""HTTP client for the OmniBrain FastAPI backend.

All original functions (check_api_status, upload_document, query_agent) are
preserved exactly. New auth functions are additive only.
"""

from typing import Any, BinaryIO
import requests
from config import FASTAPI_BASE_URL, API_TIMEOUT_SECONDS

# ── Error class ────────────────────────────────────────────────────────────────

class ApiError(RuntimeError):
    """A user-facing error raised when the backend cannot complete a request."""


# ── Helpers ────────────────────────────────────────────────────────────────────

def _auth_headers(token: str | None) -> dict:
    """Build Authorization header dict when a JWT token is available."""
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def _error_message(response: requests.Response) -> str:
    """Extract a useful detail from a FastAPI error response."""
    try:
        detail = response.json().get("detail")
        if detail:
            return str(detail)
    except (ValueError, requests.exceptions.JSONDecodeError):
        pass
    return f"The API returned HTTP {response.status_code}."


# ── Health check (unchanged) ───────────────────────────────────────────────────

def check_api_status() -> bool:
    """Return whether the FastAPI root endpoint is reachable."""
    try:
        response = requests.get(f"{FASTAPI_BASE_URL}/", timeout=3)
        response.raise_for_status()
        return response.json().get("message") == "OmniBrain API Running"
    except (requests.exceptions.RequestException, ValueError):
        return False


# ── Auth API calls (NEW) ───────────────────────────────────────────────────────

def register_user(username: str, email: str, password: str) -> dict[str, Any]:
    """Register a new user account. Returns the created user info dict."""
    try:
        response = requests.post(
            f"{FASTAPI_BASE_URL}/auth/register",
            json={"username": username, "email": email, "password": password},
            timeout=15,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError as exc:
        raise ApiError("The OmniBrain API is offline. Start the FastAPI server and try again.") from exc
    except requests.exceptions.RequestException as exc:
        resp = getattr(exc, "response", None)
        raise ApiError(_error_message(resp) if resp is not None else "Registration failed.") from exc


def login_user(username: str, password: str) -> dict[str, Any]:
    """
    Authenticate and return the JWT token dict: {"access_token": ..., "token_type": "bearer"}.
    Raises ApiError on failure.
    """
    try:
        response = requests.post(
            f"{FASTAPI_BASE_URL}/auth/login",
            json={"username": username, "password": password},
            timeout=15,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError as exc:
        raise ApiError("The OmniBrain API is offline. Start the FastAPI server and try again.") from exc
    except requests.exceptions.RequestException as exc:
        resp = getattr(exc, "response", None)
        raise ApiError(_error_message(resp) if resp is not None else "Login failed.") from exc


def get_current_user_info(token: str) -> dict[str, Any]:
    """Fetch the authenticated user's profile using the JWT token."""
    try:
        response = requests.get(
            f"{FASTAPI_BASE_URL}/auth/me",
            headers=_auth_headers(token),
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as exc:
        resp = getattr(exc, "response", None)
        raise ApiError(_error_message(resp) if resp is not None else "Failed to fetch user info.") from exc


# ── Document upload (original logic preserved, token added) ───────────────────

def upload_document(
    file: BinaryIO,
    filename: str,
    content_type: str | None = None,
    token: str | None = None,
) -> dict[str, Any]:
    """Upload one document to the backend ingestion endpoint."""
    try:
        response = requests.post(
            f"{FASTAPI_BASE_URL}/upload",
            files={"file": (filename, file, content_type or "application/octet-stream")},
            headers=_auth_headers(token),
            timeout=API_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.exceptions.Timeout as exc:
        raise ApiError("The upload timed out. Please try again.") from exc
    except requests.exceptions.ConnectionError as exc:
        raise ApiError("The OmniBrain API is offline. Start the FastAPI server and try again.") from exc
    except requests.exceptions.RequestException as exc:
        response = getattr(exc, "response", None)
        message = _error_message(response) if response is not None else "The upload could not be completed."
        raise ApiError(message) from exc

    try:
        return response.json()
    except ValueError as exc:
        raise ApiError("The API returned an invalid upload response.") from exc


# ── Query agent (original logic preserved, token added) ───────────────────────

def query_agent(query: str, token: str | None = None) -> dict[str, Any]:
    """Send a natural-language query to the backend RAG graph."""
    try:
        response = requests.post(
            f"{FASTAPI_BASE_URL}/query",
            json={"query": query},
            headers=_auth_headers(token),
            timeout=API_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.exceptions.Timeout as exc:
        raise ApiError("The query timed out. Please try a shorter question or try again.") from exc
    except requests.exceptions.ConnectionError as exc:
        raise ApiError("The OmniBrain API is offline. Start the FastAPI server and try again.") from exc
    except requests.exceptions.RequestException as exc:
        response = getattr(exc, "response", None)
        message = _error_message(response) if response is not None else "The query could not be completed."
        raise ApiError(message) from exc

    try:
        return response.json()
    except ValueError as exc:
        raise ApiError("The API returned an invalid query response.") from exc