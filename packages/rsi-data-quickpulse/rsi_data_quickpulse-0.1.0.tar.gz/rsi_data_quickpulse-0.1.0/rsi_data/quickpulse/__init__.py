"""QuickPulse Python SDK.

Public exports:
- QuickPulse (sync client)
- AsyncQuickPulse (async client)
- models (typed dataclasses for responses & events)
- errors (exception hierarchy)
"""

from __future__ import annotations

from . import models, errors  # re-export namespaces

__all__ = [
    "QuickPulse",
    "AsyncQuickPulse",
    "models",
    "errors",
    "__version__",
]

__version__ = "0.1.0"

# Lazy imports to avoid import cycles during package initialization
def __getattr__(name: str):  # pragma: no cover - thin shim
    if name == "QuickPulse":
        from .client import QuickPulse

        return QuickPulse
    if name == "AsyncQuickPulse":
        from .async_client import AsyncQuickPulse

        return AsyncQuickPulse
    raise AttributeError(name)


