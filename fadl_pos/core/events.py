# Copyright (c) 2026, FadlTech team and contributors

"""Minimal in-process pub/sub so a feature module's ``events.py`` can publish
domain events without coupling to whoever eventually listens for them.

Usage in a feature module's own ``events.py``::

        from fadl_pos.core.events import emit


        def login_succeeded(*, user: str) -> None:
            emit("login.succeeded", user=user)

Handlers are registered with :func:`on` (e.g. from ``hooks.py`` wiring, or from
tests) and run synchronously, in registration order, in the current request.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from typing import Any

_HANDLERS: dict[str, list[Callable[..., None]]] = defaultdict(list)


def on(event: str) -> Callable[[Callable[..., None]], Callable[..., None]]:
	"""Decorator: register ``fn`` as a handler for ``event``."""

	def decorator(fn: Callable[..., None]) -> Callable[..., None]:
		_HANDLERS[event].append(fn)
		return fn

	return decorator


def off(event: str, fn: Callable[..., None]) -> None:
	"""Unregister ``fn`` from ``event`` (no-op if not registered); mainly for tests."""
	handlers = _HANDLERS.get(event)
	if handlers and fn in handlers:
		handlers.remove(fn)


def emit(event: str, **payload: Any) -> None:
	"""Synchronously call every handler registered for ``event`` with ``payload``."""
	for handler in list(_HANDLERS.get(event, ())):
		handler(**payload)
