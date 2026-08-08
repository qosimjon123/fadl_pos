# Copyright (c) 2026, FadlTech team and contributors

"""pricing RPC endpoints for Frappe `/api/method/...` calls."""

from __future__ import annotations

import frappe

from fadl_pos.pricing.controller import PricingController


def _controller() -> PricingController:
	return PricingController()


@frappe.whitelist()
def get_active_pricing_rules(*args, **kwargs):
	"""``/api/method/fadl_pos.pricing.whitelist.get_active_pricing_rules``"""
	return _controller().get_active_pricing_rules(*args, **kwargs)

@frappe.whitelist()
def reconcile_line_prices(*args, **kwargs):
	"""``/api/method/fadl_pos.pricing.whitelist.reconcile_line_prices``"""
	return _controller().reconcile_line_prices(*args, **kwargs)
