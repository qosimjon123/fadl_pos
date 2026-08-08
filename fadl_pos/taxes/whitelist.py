# Copyright (c) 2026, FadlTech team and contributors

"""taxes RPC endpoints for Frappe `/api/method/...` calls."""

from __future__ import annotations

import frappe

from fadl_pos.taxes.controller import TaxesController


def _controller() -> TaxesController:
	return TaxesController()


@frappe.whitelist()
def get_item_tax_template(*args, **kwargs):
	"""``/api/method/fadl_pos.taxes.whitelist.get_item_tax_template``"""
	return _controller().get_item_tax_template(*args, **kwargs)

@frappe.whitelist()
def get_item_tax_templates_bulk(*args, **kwargs):
	"""``/api/method/fadl_pos.taxes.whitelist.get_item_tax_templates_bulk``"""
	return _controller().get_item_tax_templates_bulk(*args, **kwargs)
