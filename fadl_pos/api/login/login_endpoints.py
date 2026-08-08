# Copyright (c) 2026, FadlTech team and contributors

"""Deprecated: kept only so existing clients calling
``fadl_pos.api.login.login_endpoints.*`` keep working. New code and new
clients should target ``fadl_pos.login.whitelist`` directly; this module will
be removed once every consumer has moved to the new route.
"""

from __future__ import annotations

from fadl_pos.login.whitelist import clear_sessions, generate_qr, login, login_qr

__all__ = ["clear_sessions", "generate_qr", "login", "login_qr"]
