"""Internal utilities for QuickPulse SDK."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
import uuid
from typing import Any, Dict, Iterable, Optional

DEFAULT_BASE_URL = "https://api.rsi-data.com"

logger = logging.getLogger("quickpulse.utils")


def resolve_api_key(explicit: Optional[str]) -> Optional[str]:
    return explicit or os.getenv("QUICKPULSE_API_KEY")


def resolve_base_url(explicit: Optional[str]) -> str:
    return explicit or os.getenv("QUICKPULSE_BASE_URL") or DEFAULT_BASE_URL


def build_user_agent(sdk_version: str, httpx_version: Optional[str] = None) -> str:
    agent = f"quickpulse-python/{sdk_version}"
    if httpx_version:
        agent += f" (+httpx/{httpx_version})"
    else:
        agent += " (+httpx)"
    return agent


def redact_headers(headers: Dict[str, str]) -> Dict[str, str]:
    redacted = dict(headers)
    if "Authorization" in redacted:
        redacted["Authorization"] = "Bearer [REDACTED]"
    return redacted


def deterministic_idempotency_key(query: str, options: Optional[Dict[str, Any]] = None) -> str:
    # Use uuid5(namespace, canonical-json) for deterministic key
    canonical = json.dumps({"query": query, "options": options or {}}, sort_keys=True, separators=(",", ":"))
    return str(uuid.uuid5(uuid.NAMESPACE_URL, canonical))


def compact_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None}


def sleep(seconds: float) -> None:
    time.sleep(max(0.0, seconds))


async def async_sleep(seconds: float) -> None:
    await asyncio.sleep(max(0.0, seconds))


def iterify(value: Optional[Iterable[str]]) -> Iterable[str]:  # pragma: no cover - helper
    return value or []


