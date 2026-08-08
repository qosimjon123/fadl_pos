# Copyright (c) 2026, FadlTech team and contributors

"""Session domain events — hook points for future listeners (e.g. audit logging).

No handlers are registered yet; this only standardizes the event names and
payload shape emitted by :mod:`fadl_pos.session.controller`.
"""

from __future__ import annotations

from fadl_pos.core.events import emit

SHIFT_OPENED = "session.shift_opened"
SHIFT_CLOSED = "session.shift_closed"


def shift_opened(*, user: str, pos_profile: str, opening_entry: str) -> None:
	emit(SHIFT_OPENED, user=user, pos_profile=pos_profile, opening_entry=opening_entry)


def shift_closed(*, user: str, opening_entry: str, closing_entry: str) -> None:
	emit(SHIFT_CLOSED, user=user, opening_entry=opening_entry, closing_entry=closing_entry)
