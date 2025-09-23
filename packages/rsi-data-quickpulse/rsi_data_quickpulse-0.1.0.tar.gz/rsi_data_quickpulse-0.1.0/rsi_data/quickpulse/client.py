"""Synchronous QuickPulse client."""

from __future__ import annotations

import logging
import random
from typing import Any, Callable, Dict, Iterator, Optional

import httpx

from ._http import HttpConfig, create_sync_client, request_json
from ._sse import iter_sse_json_events
from ._utils import compact_dict, resolve_api_key, resolve_base_url, sleep
from .errors import (
    ApiError,
    RateLimitError,
    StreamConnectionError,
    StreamError,
    TransportError,
)
from .models import ResearchAskResponse, StreamEvent, parse_stream_event
from .research import ResearchNamespace

logger = logging.getLogger("quickpulse.client")


class QuickPulse:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.rsi-data.com",
        timeout: Optional[float] = None,
        connect_timeout: float = 5.0,
        read_timeout: float = 60.0,
        proxies: Optional[dict] = None,
        verify: bool = True,
        user_agent: Optional[str] = None,
    ) -> None:
        key = resolve_api_key(api_key)
        if not key:
            raise TransportError("API key is required. Provide api_key or set QUICKPULSE_API_KEY.")
        base = resolve_base_url(base_url)

        cfg = HttpConfig(
            base_url=base,
            api_key=key,
            connect_timeout=connect_timeout,
            read_timeout=read_timeout,
            total_timeout=timeout,
            proxies=proxies,
            verify=verify,
            user_agent=user_agent,
        )
        self._client: httpx.Client = create_sync_client(cfg)
        self.research = ResearchNamespace(self)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "QuickPulse":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    # -------------------------- Public API --------------------------
    def ask(
        self,
        *,
        query: str,
        chat_id: Optional[str] = None,
        user_id: Optional[str] = None,
        source: Optional[str] = None,
        advanced_config: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
        timeout: Optional[float] = None,
        retries: Optional[int] = None,
    ) -> ResearchAskResponse:
        body: Dict[str, Any] = compact_dict(
            {
                "query": query,
                "chat_id": chat_id,
                "user_id": user_id,
                "source": source,
                "advanced_config": advanced_config,
            }
        )

        headers: Dict[str, str] = {}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key

        # Retry policy per PRD: only if idempotency_key provided
        max_retries = 0
        if idempotency_key:
            max_retries = 3 if retries is None else max(0, retries)

        attempt = 0
        while True:
            try:
                data = request_json(
                    self._client,
                    "POST",
                    "/v1/research/ask",
                    json_body=body,
                    headers=headers,
                    timeout=timeout,
                )
                return ResearchAskResponse(
                    response=data.get("response", ""),
                    chat_id=data.get("chat_id"),
                    web_searched_data=data.get("web_searched_data"),
                    indian_data=data.get("indian_data"),
                    indian_documents=data.get("indian_documents"),
                )
            except (RateLimitError, ApiError, TransportError) as exc:
                # Decide retry
                should_retry = False
                delay_seconds: Optional[float] = None
                if idempotency_key and attempt < max_retries:
                    if isinstance(exc, RateLimitError):
                        should_retry = True
                        delay_seconds = exc.retry_after if exc.retry_after is not None else None
                    elif isinstance(exc, ApiError):
                        # retry on 408, 5xx
                        if exc.status_code == 408 or exc.status_code >= 500:
                            should_retry = True
                    else:  # TransportError
                        should_retry = True

                if not should_retry:
                    raise

                attempt += 1
                # Exponential backoff with jitter
                base = 0.5
                factor = 2.0
                max_delay = 8.0
                computed = min(max_delay, base * (factor ** (attempt - 1)))
                jitter = random.uniform(0, 0.25)
                delay = delay_seconds if delay_seconds is not None else computed + jitter
                if isinstance(exc, RateLimitError) and delay_seconds is not None:
                    delay = min(delay_seconds, 30.0)
                logger.debug("Retrying ask after %.2fs (attempt %s)", delay, attempt)
                sleep(delay)

    def stream(
        self,
        *,
        query: str,
        chat_id: Optional[str] = None,
        user_id: Optional[str] = None,
        source: Optional[str] = None,
        advanced_config: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        on_token: Optional[Callable[[str], None]] = None,
        on_status: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> Iterator[StreamEvent]:
        body: Dict[str, Any] = compact_dict(
            {
                "query": query,
                "chat_id": chat_id,
                "user_id": user_id,
                "source": source,
                "advanced_config": advanced_config,
            }
        )

        headers = {"Accept": "text/event-stream"}
        saw_final = False

        try:
            with self._client.stream("POST", "/v1/research/stream", json=body, headers=headers, timeout=timeout) as resp:
                if resp.status_code // 100 != 2:
                    # Try to map error
                    try:
                        payload = resp.json()
                    except Exception:
                        raise TransportError(f"Non-2xx SSE start: status={resp.status_code}")
                    raise map_api_error(resp.status_code, payload, dict(resp.headers))

                for obj in iter_sse_json_events(resp):
                    evt = parse_stream_event(obj)
                    if evt.type == "token" and on_token:
                        on_token(evt.data)  # type: ignore[arg-type]
                    elif evt.type == "status" and on_status:
                        on_status(evt.data)  # type: ignore[arg-type]
                    elif evt.type == "error":
                        # Stop iteration on error event
                        raise StreamError(status_code=200, error_type="error", message=evt.data.get("message", "stream error"), raw=obj)
                    elif evt.type == "final":
                        saw_final = True
                        yield evt
                        return
                    yield evt
        except httpx.HTTPError as exc:
            raise StreamConnectionError(f"SSE connection error: {exc}", cause=exc)

        if not saw_final:
            raise StreamConnectionError("Connection closed before final event")


