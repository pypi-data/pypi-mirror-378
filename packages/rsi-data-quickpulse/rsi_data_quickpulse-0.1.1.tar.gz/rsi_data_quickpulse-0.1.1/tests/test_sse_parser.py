import httpx

from rsi_data.quickpulse._sse import iter_sse_json_events


def build_response(text: str) -> httpx.Response:
    # Build a streaming-like response using plain content; httpx iter_lines will split
    return httpx.Response(200, content=text.encode("utf-8"), headers={"Content-Type": "text/event-stream"})


def test_sse_token_and_final():
    stream_text = (
        ": keepalive\n\n"
        "data: {\"type\": \"token\", \"data\": \"Hello \"}\n\n"
        "data: {\"type\": \"token\", \"data\": \"World\"}\n\n"
        "data: {\"type\": \"final\", \"data\": {\"response\": \"Done\"}}\n\n"
    )
    resp = build_response(stream_text)
    events = list(iter_sse_json_events(resp))
    assert len(events) == 3
    assert events[0]["type"] == "token"
    assert events[-1]["type"] == "final"


