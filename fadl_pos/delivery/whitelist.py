# Copyright (c) 2026, FadlTech team and contributors

"""Delivery charges RPC endpoints."""

from __future__ import annotations

import frappe

from fadl_pos.delivery.controller import DeliveryController


def _controller() -> DeliveryController:
	return DeliveryController()


@frappe.whitelist()
def get_delivery_charges(*args, **kwargs):
	"""``/api/method/fadl_pos.delivery.whitelist.get_delivery_charges``"""
	return _controller().get_delivery_charges(*args, **kwargs)


@frappe.whitelist()
def get_applicable_delivery_charges(*args, **kwargs):
	"""``/api/method/fadl_pos.delivery.whitelist.get_applicable_delivery_charges``"""
	return _controller().get_applicable_delivery_charges(*args, **kwargs)
