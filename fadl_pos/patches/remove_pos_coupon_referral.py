# Copyright (c) 2026, FadlTech team and contributors

"""Cleanup stale POS Profile shift field after rename to hide_closing_entry.

Referral Code / POS Coupon referral linkage is part of customer parity and
must NOT be removed here.
"""

from __future__ import annotations


def execute() -> None:
	import frappe

	# Renamed hide_closing_shift → hide_closing_entry in fixtures; drop stale CF.
	if frappe.db.exists("Custom Field", "POS Profile-hide_closing_shift"):
		frappe.delete_doc("Custom Field", "POS Profile-hide_closing_shift", force=1)
		frappe.clear_cache(doctype="POS Profile")
