# Copyright (c) 2026, FadlTech team and contributors

"""Printing domain guards / has_permission hooks."""

from __future__ import annotations

from frappe.utils import cint

from fadl_pos.core.permission import require_session_user

__all__ = ["require_session_user", "invoice_has_permission", "_can_reprint"]


def _can_reprint(user: str | None = None) -> bool:
	"""Whether ``user`` may reprint a posted POS invoice (the ``allow_reprint_invoice`` right).

	Resolved from the user's POS Role permission map so it stays in sync with
	the Role Permissions admin screen. Administrators / System Managers always
	qualify.
	"""
	from fadl_pos.permissions.permission import user_has_pos_permission

	return user_has_pos_permission("allow_reprint_invoice", user)


def invoice_has_permission(doc, ptype: str, user: str) -> bool:
	"""``has_permission`` hook restricting reprinting of POS invoices.

	The first receipt (``print_count`` == 0) is always allowed so cashiers
	can print at the point of sale; every subsequent print is a reprint and
	requires the ``allow_reprint_invoice`` right. Non-print actions and
	non-POS invoices defer to Frappe's normal role permissions.
	"""
	if ptype != "print":
		return True
	if not getattr(doc, "is_pos", 0):
		return True
	if cint(getattr(doc, "print_count", 0)) < 1:
		return True
	return _can_reprint(user)
