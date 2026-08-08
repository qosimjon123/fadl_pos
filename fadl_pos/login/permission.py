# Copyright (c) 2026, FadlTech team and contributors

"""Login-specific permission guards.

Login has no document-status workflow (guest -> authenticated is a session
concept, not a persisted state machine), so there is deliberately no
``workflow.py`` here — the only gates are these session/account checks.
"""

from __future__ import annotations

import frappe
from frappe.utils import cint

from fadl_pos.core.errors import auth_error
from fadl_pos.core.permission import require_session_user


def require_authenticated_session(user: str | None = None) -> str:
	"""Login/QR self-service actions (clear_sessions, generate_qr) additionally
	reject standard accounts (``Administrator``) on top of the generic
	Guest-rejecting ``core.permission.require_session_user`` — matches the
	original ``TokenAuthService._require_session_user`` behaviour."""
	user = require_session_user(user)
	if user in frappe.STANDARD_USERS:
		auth_error("Log in to continue.")
	return user


def require_enabled_login_user(user: str | None, *, enabled: object) -> str:
	"""Reject standard/disabled accounts right after credential lookup."""
	if not user or user in frappe.STANDARD_USERS or not cint(enabled):
		auth_error("Invalid login credentials")
	return user


def require_qr_bound_user(user: str | None) -> str:
	"""Reject QR logins that resolve to a missing or standard/disabled account."""
	if not user or user in frappe.STANDARD_USERS:
		auth_error("Invalid PIN or encrypted QR payload")
	return user
