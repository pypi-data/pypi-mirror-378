# QuickPulse Python SDK

QuickPulse SDK for the Research API (sync + async), with robust error handling, retries (idempotent), and SSE streaming.

## Install

```bash
pip install rsi-data-quickpulse
```

## Usage

See examples in docstrings and below minimal snippet.

```python
from rsi_data.quickpulse import QuickPulse

with QuickPulse(api_key="sk_live_...") as client:
    resp = client.ask(query="Hello", idempotency_key="example-1")
    print(resp.response)
```
