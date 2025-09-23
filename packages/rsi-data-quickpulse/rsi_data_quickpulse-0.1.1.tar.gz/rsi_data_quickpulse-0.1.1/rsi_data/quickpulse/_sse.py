"""Robust SSE parsing for QuickPulse SDK."""

from __future__ import annotations

import json
import logging
from typing import Any, AsyncIterator, Dict, Iterator, Optional

import httpx

from .errors import TransportError, StreamConnectionError

logger = logging.getLogger("quickpulse.sse")


def _dispatch_event(accumulated: Optional[str]) -> Optional[Dict[str, Any]]:
    if accumulated is None:
        return None
    text = accumulated.strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise TransportError(f"Malformed SSE data JSON: {text}", cause=exc)


def iter_sse_json_events(resp: httpx.Response) -> Iterator[Dict[str, Any]]:
    """Yield parsed JSON objects from an SSE httpx.Response (sync)."""

    event_data: Optional[str] = None
    try:
        for line in resp.iter_lines():
            if line is None:
                continue
            if line == "":
                evt = _dispatch_event(event_data)
                event_data = None
                if evt is not None:
                    yield evt
                continue
            if line.startswith(":"):
                # Heartbeat/comment
                continue
            if line.startswith("data:"):
                payload = line[5:].lstrip()
                if event_data is None:
                    event_data = payload
                else:
                    event_data += "\n" + payload
            # Ignore other SSE fields (event, id, retry) for now

        # Stream ended
        evt = _dispatch_event(event_data)
        if evt is not None:
            yield evt
    except httpx.ReadTimeout as exc:
        raise StreamConnectionError("SSE read timed out", cause=exc)
    except httpx.HTTPError as exc:
        raise StreamConnectionError(f"SSE connection error: {exc}", cause=exc)


async def aiter_sse_json_events(resp: httpx.Response) -> AsyncIterator[Dict[str, Any]]:
    """Yield parsed JSON objects from an SSE httpx.Response (async)."""

    event_data: Optional[str] = None
    try:
        async for line in resp.aiter_lines():
            if line is None:
                continue
            if line == "":
                evt = _dispatch_event(event_data)
                event_data = None
                if evt is not None:
                    yield evt
                continue
            if line.startswith(":"):
                continue
            if line.startswith("data:"):
                payload = line[5:].lstrip()
                if event_data is None:
                    event_data = payload
                else:
                    event_data += "\n" + payload
        evt = _dispatch_event(event_data)
        if evt is not None:
            yield evt
    except httpx.ReadTimeout as exc:
        raise StreamConnectionError("SSE read timed out", cause=exc)
    except httpx.HTTPError as exc:
        raise StreamConnectionError(f"SSE connection error: {exc}", cause=exc)


