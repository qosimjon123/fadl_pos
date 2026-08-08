# Copyright (c) 2026, FadlTech team and contributors

"""Session-specific permission guards.

Opening/closing a shift has no extra account restrictions beyond the generic
Guest-rejecting gate (unlike ``login``'s self-service actions), so this module
re-exports the core gate for symmetry with other feature modules and adds the
one session-specific authorization rule: a cashier may only close their own
shift.
"""

from __future__ import annotations

import frappe
from frappe import _

from fadl_pos.core.permission import require_session_user

__all__ = ["require_session_user", "require_shift_owner"]


def require_shift_owner(entry_user: str, acting_user: str) -> None:
	if entry_user != acting_user:
		frappe.throw(_("You can only close your own shift."))
