# Copyright (c) 2026, FadlTech team and contributors

"""offers RPC endpoints for Frappe `/api/method/...` calls."""

from __future__ import annotations

import frappe

from fadl_pos.offers.controller import OffersController


def _controller() -> OffersController:
	return OffersController()


@frappe.whitelist()
def get_offers(*args, **kwargs):
	"""``/api/method/fadl_pos.offers.whitelist.get_offers``"""
	return _controller().get_offers(*args, **kwargs)


@frappe.whitelist()
def get_pos_coupon(*args, **kwargs):
	"""``/api/method/fadl_pos.offers.whitelist.get_pos_coupon``"""
	return _controller().get_pos_coupon(*args, **kwargs)


@frappe.whitelist()
def get_active_gift_coupons(*args, **kwargs):
	"""``/api/method/fadl_pos.offers.whitelist.get_active_gift_coupons``"""
	return _controller().get_active_gift_coupons(*args, **kwargs)
