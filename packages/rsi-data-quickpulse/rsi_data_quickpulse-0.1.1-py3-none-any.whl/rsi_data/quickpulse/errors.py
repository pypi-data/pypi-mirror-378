"""Exception hierarchy and error mapping for QuickPulse SDK.

Exposes typed exceptions with normalized error types and helpful context.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ApiError(Exception):
    """Base class for API errors returned by the QuickPulse service.

    Attributes:
        status_code: HTTP status code from the response.
        error_type: One of {"auth","quota","rate_limit","bad_request","server_error"}.
        message: Human-readable error message.
        request_id: Optional request identifier from response headers, if provided.
        raw: Raw error payload (parsed JSON) when available.
    """

    status_code: int
    error_type: str
    message: str
    request_id: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None

    def __str__(self) -> str:  # pragma: no cover - trivial
        rid = f" request_id={self.request_id}" if self.request_id else ""
        return f"ApiError(type={self.error_type}, status={self.status_code}, message={self.message}{rid})"


class AuthError(ApiError):
    pass


class QuotaError(ApiError):
    pass


class RateLimitError(ApiError):
    def __init__(
        self,
        status_code: int,
        error_type: str,
        message: str,
        request_id: Optional[str] = None,
        raw: Optional[Dict[str, Any]] = None,
        retry_after: Optional[float] = None,
    ) -> None:
        super().__init__(status_code=status_code, error_type=error_type, message=message, request_id=request_id, raw=raw)
        self.retry_after = retry_after


class BadRequestError(ApiError):
    pass


class ServerError(ApiError):
    pass


class TransportError(Exception):
    """Networking or parsing error unrelated to a well-formed API error response."""

    def __init__(self, message: str, *, cause: Optional[BaseException] = None) -> None:
        super().__init__(message)
        self.cause = cause


class StreamError(ApiError):
    pass


class StreamConnectionError(TransportError):
    pass


def _extract_request_id(headers: Dict[str, str]) -> Optional[str]:
    # Try common header names for request correlation
    for key in (
        "X-Request-Id",
        "X-Request-ID",
        "X-Correlation-Id",
        "X-Trace-Id",
        "X-Quickpulse-Job-Id",
        "X-Job-Id",
        "X-Generation-Id",
    ):
        if key in headers:
            return headers.get(key)
    return None


def map_api_error(status_code: int, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> ApiError:
    """Map a normalized error payload to a specific ApiError subclass.

    The payload is expected to be of shape: {"error": {"type": str, "message": str, ...}}
    """

    headers = headers or {}
    request_id = _extract_request_id(headers)
    error = payload.get("error") if isinstance(payload, dict) else None
    error_type = (error or {}).get("type") or _infer_error_type(status_code)
    message = (error or {}).get("message") or "Unknown error"

    # Rate limit retry-after handling
    retry_after_value: Optional[float] = None
    if error_type == "rate_limit":
        retry_header = headers.get("Retry-After") if headers else None
        if retry_header:
            try:
                # Prefer seconds value; if HTTP-date, we ignore for simplicity here
                retry_after_value = float(retry_header)
            except ValueError:
                retry_after_value = None

    cls_map = {
        "auth": AuthError,
        "quota": QuotaError,
        "rate_limit": RateLimitError,
        "bad_request": BadRequestError,
        "server_error": ServerError,
    }
    cls = cls_map.get(error_type, ApiError)

    if cls is RateLimitError:
        return RateLimitError(
            status_code=status_code,
            error_type=error_type,
            message=message,
            request_id=request_id,
            raw=payload,
            retry_after=retry_after_value,
        )

    return cls(status_code=status_code, error_type=error_type, message=message, request_id=request_id, raw=payload)


def _infer_error_type(status_code: int) -> str:
    if status_code in (401, 403):
        return "auth"
    if status_code == 429:
        return "rate_limit"
    if 400 <= status_code < 500:
        return "bad_request"
    if status_code >= 500:
        return "server_error"
    return "server_error"


