# Copyright (c) 2026, FadlTech team and contributors

"""POS shift status machine: ``Open -> Closed`` (via POS Closing Entry submission).

There is no "cancelled" transition modeled here: POS Opening/Closing Entry
cancellation follows the standard Frappe document lifecycle, not this RPC layer.
"""

from __future__ import annotations

import frappe
from frappe import _

from fadl_pos.core.workflow import Workflow

SHIFT_TRANSITIONS: dict[str, list[str]] = {
	"Open": ["Closed"],
	"Closed": [],
}

shift_workflow = Workflow(SHIFT_TRANSITIONS)


def assert_can_close(status: str) -> None:
	"""Guard before closing: the opening entry must currently be ``Open``."""
	if not shift_workflow.can_transition(status, "Closed"):
		frappe.throw(_("This POS Opening Entry is already closed or cancelled."))
