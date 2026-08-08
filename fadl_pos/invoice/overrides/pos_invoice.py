# Copyright (c) 2026, FadlTech team and contributors

"""POS Invoice mixin — validate against ERPNext POS Opening Entry."""

from __future__ import annotations

from fadl_pos.invoice.events import validate_shift


class CustomPOSInvoice:
	"""Mixin that augments ERPNext POS Invoice for Fadl POS opening entries."""

	def validate_pos_opening_entry(self):
		"""Validate ``pos_opening_entry`` with Fadl POS rules when present.

		Uses the same Opening Entry document ERPNext expects. When the field
		is set, apply Fadl POS profile/company/status checks; otherwise fall
		back to the default ERPNext behaviour.
		"""
		if getattr(self, "pos_opening_entry", None):
			validate_shift(self)
			return

		super().validate_pos_opening_entry()
