"""Research namespace wrappers for QuickPulse clients."""

from __future__ import annotations

from typing import Any, AsyncIterator, Callable, Dict, Iterator, Optional

from .models import StreamEvent


class ResearchNamespace:
    def __init__(self, client: "QuickPulse") -> None:
        self._client = client

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
    ):
        return self._client.ask(
            query=query,
            chat_id=chat_id,
            user_id=user_id,
            source=source,
            advanced_config=advanced_config,
            idempotency_key=idempotency_key,
            timeout=timeout,
            retries=retries,
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
    ) -> Iterator[StreamEvent]:
        return self._client.stream(
            query=query,
            chat_id=chat_id,
            user_id=user_id,
            source=source,
            advanced_config=advanced_config,
            timeout=timeout,
            on_token=on_token,
            on_status=on_status,
        )


class AsyncResearchNamespace:
    def __init__(self, client: "AsyncQuickPulse") -> None:
        self._client = client

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
    ):
        return await self._client.ask(
            query=query,
            chat_id=chat_id,
            user_id=user_id,
            source=source,
            advanced_config=advanced_config,
            idempotency_key=idempotency_key,
            timeout=timeout,
            retries=retries,
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
        return self._client.stream(
            query=query,
            chat_id=chat_id,
            user_id=user_id,
            source=source,
            advanced_config=advanced_config,
            timeout=timeout,
            on_token=on_token,
            on_status=on_status,
        )


