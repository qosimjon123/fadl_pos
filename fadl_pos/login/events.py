# Copyright (c) 2026, FadlTech team and contributors

"""Login domain events — hook points for future listeners (e.g. audit logging).

No handlers are registered yet; this only standardizes the event names and
payload shape emitted by :mod:`fadl_pos.login.controller`.
"""

from __future__ import annotations

from fadl_pos.core.events import emit

LOGIN_SUCCEEDED = "login.succeeded"
QR_GENERATED = "login.qr_generated"
SESSIONS_CLEARED = "login.sessions_cleared"


def login_succeeded(*, user: str, method: str) -> None:
	"""``method`` is ``"password"`` or ``"qr"``."""
	emit(LOGIN_SUCCEEDED, user=user, method=method)


def qr_generated(*, user: str) -> None:
	emit(QR_GENERATED, user=user)


def sessions_cleared(*, user: str) -> None:
	emit(SESSIONS_CLEARED, user=user)
