# Copyright (c) 2026, FadlTech team and contributors

"""Shared session / role permission primitives.

Feature modules should put their domain-specific guards in their own
``permission.py`` and delegate the generic session/role checks here.
"""

from __future__ import annotations

import frappe

from fadl_pos.core.errors import auth_error


def is_manager(user: str | None = None) -> bool:
	user = user or frappe.session.user
	return user == "Administrator" or "System Manager" in frappe.get_roles(user)


def require_session_user(user: str | None = None) -> str:
	"""Resolve and validate the acting user; reject Guest (unauthenticated).

	This is the generic, app-wide gate (matches the original ``BaseService``).
	Feature modules that must additionally reject standard/system accounts
	(e.g. ``login`` rejecting ``Administrator`` for cashier-only actions)
	should layer their own, stricter guard in their own ``permission.py``.
	"""
	user = user or frappe.session.user
	if not user or user == "Guest":
		auth_error("Log in to continue.")
	return user


class BaseController:
	"""Shared controller base: session user gate for RPC layers."""

	def __init__(self, user: str | None = None):
		self.user = require_session_user(user)
