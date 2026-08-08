# Copyright (c) 2026, FadlTech team and contributors

"""Generic state-transition engine.

Feature modules that have a real document status machine (invoice, session, ...)
declare their own ``workflow.py`` with a transitions dict and a module-level
:class:`Workflow` instance, e.g.::

        INVOICE_TRANSITIONS = {
            "draft": ["submitted", "voided"],
            "submitted": ["paid", "canceled"],
            "paid": [],
            "canceled": [],
        }
        invoice_workflow = Workflow(INVOICE_TRANSITIONS)

Modules without a real state machine (e.g. ``login``, where "guest -> authenticated"
is a session concept, not a document status) do not need a ``workflow.py`` at all;
fold the single guard into their ``permission.py`` instead.
"""

from __future__ import annotations

from dataclasses import dataclass

import frappe
from frappe import _


@dataclass(frozen=True)
class Workflow:
	"""Declarative state machine: ``{state: [allowed_next_states]}``."""

	transitions: dict[str, list[str]]

	def allowed_targets(self, current: str) -> list[str]:
		return list(self.transitions.get(current, []))

	def can_transition(self, current: str, target: str) -> bool:
		return target in self.transitions.get(current, [])

	def assert_transition(self, current: str, target: str, *, label: str = "state") -> None:
		if not self.can_transition(current, target):
			frappe.throw(
				_("Cannot transition {0} from {1} to {2}.").format(label, current, target),
				frappe.ValidationError,
			)
