"""Asynchronous QuickPulse client."""

from __future__ import annotations

import logging
import random
from typing import Any, AsyncIterator, Callable, Dict, Optional

import httpx

from ._http import HttpConfig, create_async_client
from ._sse import aiter_sse_json_events
from ._utils import compact_dict, resolve_api_key, resolve_base_url, async_sleep
from .errors import (
    ApiError,
    RateLimitError,
    StreamConnectionError,
    StreamError,
    TransportError,
    map_api_error,
)
from .models import StreamEvent, parse_stream_event, ResearchAskResponse
from .research import AsyncResearchNamespace

logger = logging.getLogger("quickpulse.async_client")


class AsyncQuickPulse:
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
        self._client: httpx.AsyncClient = create_async_client(cfg)
        self.research = AsyncResearchNamespace(self)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncQuickPulse":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    # -------------------------- Public API --------------------------
    async def ask(
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

        max_retries = 0
        if idempotency_key:
            max_retries = 3 if retries is None else max(0, retries)

        attempt = 0
        while True:
            try:
                resp = await self._client.post("/v1/research/ask", json=body, headers=headers, timeout=timeout)
            except httpx.HTTPError as exc:
                if idempotency_key and attempt < max_retries:
                    attempt += 1
                    base = 0.5
                    factor = 2.0
                    max_delay = 8.0
                    computed = min(max_delay, base * (factor ** (attempt - 1)))
                    jitter = random.uniform(0, 0.25)
                    delay = computed + jitter
                    logger.debug("Retrying ask after %.2fs (attempt %s)", delay, attempt)
                    await async_sleep(delay)
                    continue
                raise TransportError(f"HTTP transport error: {exc}", cause=exc)

            if resp.status_code // 100 != 2:
                # Map error
                try:
                    payload = resp.json()
                except Exception:
                    raise TransportError(f"Non-2xx response with non-JSON body: status={resp.status_code}")
                err = map_api_error(resp.status_code, payload, dict(resp.headers))
                if idempotency_key and attempt < max_retries and (
                    isinstance(err, RateLimitError)
                    or err.status_code == 408
                    or err.status_code >= 500
                ):
                    attempt += 1
                    delay = err.retry_after if isinstance(err, RateLimitError) and err.retry_after is not None else None
                    base = 0.5
                    factor = 2.0
                    max_delay = 8.0
                    computed = min(max_delay, base * (factor ** (attempt - 1)))
                    jitter = random.uniform(0, 0.25)
                    delay = (min(delay, 30.0) if delay is not None else computed + jitter)
                    logger.debug("Retrying ask after %.2fs (attempt %s)", delay, attempt)
                    await async_sleep(delay)
                    continue
                raise err

            try:
                data = resp.json()
            except Exception as exc:
                raise TransportError("Response JSON parse error", cause=exc)

            return ResearchAskResponse(
                response=data.get("response", ""),
                chat_id=data.get("chat_id"),
                web_searched_data=data.get("web_searched_data"),
                indian_data=data.get("indian_data"),
                indian_documents=data.get("indian_documents"),
            )

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
    ) -> AsyncIterator[StreamEvent]:
        async def gen() -> AsyncIterator[StreamEvent]:
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
                async with self._client.stream("POST", "/v1/research/stream", json=body, headers=headers, timeout=timeout) as resp:
                    if resp.status_code // 100 != 2:
                        try:
                            payload = await resp.aread()
                            try:
                                payload_json = resp.json()
                            except Exception:
                                raise TransportError(f"Non-2xx SSE start: status={resp.status_code}")
                        except Exception:
                            raise TransportError(f"Non-2xx SSE start: status={resp.status_code}")
                        raise map_api_error(resp.status_code, payload_json, dict(resp.headers))

                    async for obj in aiter_sse_json_events(resp):
                        evt = parse_stream_event(obj)
                        if evt.type == "token" and on_token:
                            on_token(evt.data)  # type: ignore[arg-type]
                        elif evt.type == "status" and on_status:
                            on_status(evt.data)  # type: ignore[arg-type]
                        elif evt.type == "error":
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

        return gen()


