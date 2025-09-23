import json
from typing import Any, Dict

import httpx
import pytest

from rsi_data.quickpulse import QuickPulse
from rsi_data.quickpulse.errors import AuthError, RateLimitError, ServerError


class MockTransport(httpx.BaseTransport):
    def __init__(self, responder):
        self._responder = responder

    def handle_request(self, request: httpx.Request) -> httpx.Response:  # type: ignore[override]
        return self._responder(request)


def make_client(responder):
    # Build a QuickPulse client with injected transport
    qp = QuickPulse(api_key="test")
    qp._client._transport = MockTransport(responder)
    return qp


def test_ask_success(monkeypatch):
    def responder(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/research/ask"
        payload = {"response": "hello", "chat_id": None}
        return httpx.Response(200, json=payload)

    client = make_client(responder)
    resp = client.ask(query="hi")
    assert resp.response == "hello"


def test_error_mapping_auth():
    def responder(request: httpx.Request) -> httpx.Response:
        payload = {"error": {"type": "auth", "message": "bad token"}}
        return httpx.Response(401, json=payload)

    client = make_client(responder)
    with pytest.raises(AuthError):
        client.ask(query="hi")


def test_retry_on_rate_limit_with_idempotency(monkeypatch):
    calls = {"n": 0}

    def responder(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] < 2:
            payload = {"error": {"type": "rate_limit", "message": "slow down"}}
            return httpx.Response(429, json=payload, headers={"Retry-After": "0"})
        return httpx.Response(200, json={"response": "ok"})

    client = make_client(responder)
    out = client.ask(query="q", idempotency_key="abc")
    assert out.response == "ok"
    assert calls["n"] >= 2


def test_server_error_no_retry_without_idempotency():
    def responder(request: httpx.Request) -> httpx.Response:
        payload = {"error": {"type": "server_error", "message": "boom"}}
        return httpx.Response(500, json=payload)

    client = make_client(responder)
    with pytest.raises(ServerError):
        client.ask(query="x")


