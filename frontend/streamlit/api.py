"""HTTP client for the OmniBrain FastAPI backend."""

from typing import Any, BinaryIO

import requests

from config import FASTAPI_BASE_URL

API_TIMEOUT_SECONDS=360

class ApiError(RuntimeError):
    """A user-facing error raised when the backend cannot complete a request."""


def check_api_status() -> bool:
    """Return whether the FastAPI root endpoint is reachable."""
    try:
        response = requests.get(f"{FASTAPI_BASE_URL}/", timeout=3)
        response.raise_for_status()
        return response.json().get("message") == "OmniBrain API Running"
    except (requests.exceptions.RequestException, ValueError):
        return False


def _error_message(response: requests.Response) -> str:
    """Extract a useful detail from a FastAPI error response."""
    try:
        detail = response.json().get("detail")
        if detail:
            return str(detail)
    except (ValueError, requests.exceptions.JSONDecodeError):
        pass
    return f"The API returned HTTP {response.status_code}."


def upload_document(file: BinaryIO, filename: str, content_type: str | None = None) -> dict[str, Any]:
    """Upload one document to the backend ingestion endpoint."""
    try:
        response = requests.post(
            f"{FASTAPI_BASE_URL}/upload",
            files={"file": (filename, file, content_type or "application/octet-stream")},
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


def query_agent(query: str) -> dict[str, Any]:
    """Send a natural-language query to the backend RAG graph."""
    try:
        response = requests.post(
            f"{FASTAPI_BASE_URL}/query",
            json={"query": query},
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