"""HTTP helpers for QuickPulse SDK using httpx."""

from __future__ import annotations

import json
import logging
import inspect
from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx

from .errors import TransportError, map_api_error
from ._utils import build_user_agent, redact_headers
from . import __version__


logger = logging.getLogger("quickpulse.http")


@dataclass
class HttpConfig:
    base_url: str
    api_key: str
    connect_timeout: float = 5.0
    read_timeout: float = 300.0
    total_timeout: Optional[float] = None
    proxies: Optional[dict] = None
    verify: bool = True
    user_agent: Optional[str] = None


def _default_user_agent() -> str:
    try:
        import httpx as _httpx

        return build_user_agent(__version__, getattr(_httpx, "__version__", None))
    except Exception:  # pragma: no cover - defensive
        return build_user_agent(__version__, None)


def create_sync_client(cfg: HttpConfig) -> httpx.Client:
    ua = cfg.user_agent or _default_user_agent()
    timeout = httpx.Timeout(
        cfg.total_timeout if cfg.total_timeout is not None else None,
        connect=cfg.connect_timeout,
        read=cfg.read_timeout,
    )
    kwargs: Dict[str, Any] = {
        "base_url": cfg.base_url.rstrip("/"),
        "timeout": timeout,
        "verify": cfg.verify,
        "headers": {
            "Authorization": f"Bearer {cfg.api_key}",
            "Content-Type": "application/json",
            "User-Agent": ua,
        },
    }
    if cfg.proxies is not None:
        params = inspect.signature(httpx.Client).parameters
        if "proxies" in params:
            kwargs["proxies"] = cfg.proxies
        elif "proxy" in params:
            kwargs["proxy"] = cfg.proxies
    client = httpx.Client(**kwargs)
    return client


def create_async_client(cfg: HttpConfig) -> httpx.AsyncClient:
    ua = cfg.user_agent or _default_user_agent()
    timeout = httpx.Timeout(
        cfg.total_timeout if cfg.total_timeout is not None else None,
        connect=cfg.connect_timeout,
        read=cfg.read_timeout,
    )
    kwargs: Dict[str, Any] = {
        "base_url": cfg.base_url.rstrip("/"),
        "timeout": timeout,
        "verify": cfg.verify,
        "headers": {
            "Authorization": f"Bearer {cfg.api_key}",
            "Content-Type": "application/json",
            "User-Agent": ua,
        },
    }
    if cfg.proxies is not None:
        params = inspect.signature(httpx.AsyncClient).parameters
        if "proxies" in params:
            kwargs["proxies"] = cfg.proxies
        elif "proxy" in params:
            kwargs["proxy"] = cfg.proxies
    client = httpx.AsyncClient(**kwargs)
    return client


def request_json(
    client: httpx.Client,
    method: str,
    url: str,
    *,
    json_body: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: Optional[float] = None,
) -> Dict[str, Any]:
    req_headers = dict(headers or {})
    try:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("HTTP %s %s headers=%s", method, url, redact_headers(req_headers))
        resp = client.request(method, url, json=json_body, headers=req_headers, timeout=timeout)
    except httpx.HTTPError as exc:
        raise TransportError(f"HTTP transport error: {exc}", cause=exc)

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("HTTP %s -> %s", url, resp.status_code)

    if resp.status_code // 100 != 2:
        payload: Dict[str, Any]
        try:
            payload = resp.json()
        except json.JSONDecodeError:
            raise TransportError(f"Non-2xx response with non-JSON body: status={resp.status_code}")
        raise map_api_error(resp.status_code, payload, dict(resp.headers))

    try:
        return resp.json()
    except json.JSONDecodeError as exc:
        raise TransportError("Response JSON parse error", cause=exc)


