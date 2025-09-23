"""Typed models for QuickPulse SDK."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

try:  # Python 3.8 compatibility
    from typing_extensions import Literal
except ImportError:  # pragma: no cover - runtime safety
    from typing import Literal  # type: ignore


@dataclass
class ResearchAskResponse:
    response: str
    chat_id: Optional[str]
    web_searched_data: Optional[List[Dict[str, Any]]]
    indian_data: Optional[Dict[str, Any]]
    indian_documents: Optional[Dict[str, Any]]


@dataclass
class GenerationIdEvent:
    type: Literal["generation_id"]
    data: str


@dataclass
class StatusEvent:
    type: Literal["status"]
    data: Dict[str, Any]  # {type, message, data?, timestamp}


@dataclass
class TokenEvent:
    type: Literal["token"]
    data: str


@dataclass
class FinalEvent:
    type: Literal["final"]
    data: Dict[str, Any]  # {response, chat_id, research, internal_data, internal_document}


@dataclass
class ErrorEvent:
    type: Literal["error"]
    data: Dict[str, Any]  # {message}


StreamEvent = Union[GenerationIdEvent, StatusEvent, TokenEvent, FinalEvent, ErrorEvent]


def parse_stream_event(obj: Dict[str, Any]) -> StreamEvent:
    evt_type = obj.get("type")
    if evt_type == "generation_id":
        return GenerationIdEvent(type="generation_id", data=obj.get("data"))
    if evt_type == "status":
        return StatusEvent(type="status", data=obj.get("data") or {})
    if evt_type == "token":
        return TokenEvent(type="token", data=obj.get("data") or "")
    if evt_type == "final":
        return FinalEvent(type="final", data=obj.get("data") or {})
    if evt_type == "error":
        return ErrorEvent(type="error", data=obj.get("data") or {})
    # Unknown type treated as error-like for safety
    return ErrorEvent(type="error", data={"message": f"Unknown event type: {evt_type}"})


__all__ = [
    "ResearchAskResponse",
    "GenerationIdEvent",
    "StatusEvent",
    "TokenEvent",
    "FinalEvent",
    "ErrorEvent",
    "StreamEvent",
    "parse_stream_event",
]


