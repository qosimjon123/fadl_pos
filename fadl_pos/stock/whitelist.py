# Copyright (c) 2026, FadlTech team and contributors

"""stock RPC endpoints for Frappe `/api/method/...` calls."""

from __future__ import annotations

import frappe

from fadl_pos.stock.controller import StockController


def _controller() -> StockController:
	return StockController()


@frappe.whitelist()
def get_bulk_stock_availability(*args, **kwargs):
	"""``/api/method/fadl_pos.stock.whitelist.get_bulk_stock_availability``"""
	return _controller().get_bulk_stock_availability(*args, **kwargs)

@frappe.whitelist()
def get_available_qty(*args, **kwargs):
	"""``/api/method/fadl_pos.stock.whitelist.get_available_qty``"""
	return _controller().get_available_qty(*args, **kwargs)

@frappe.whitelist()
def get_in_transit_transfers(*args, **kwargs):
	"""``/api/method/fadl_pos.stock.whitelist.get_in_transit_transfers``"""
	return _controller().get_in_transit_transfers(*args, **kwargs)

@frappe.whitelist()
def get_transfer_detail(*args, **kwargs):
	"""``/api/method/fadl_pos.stock.whitelist.get_transfer_detail``"""
	return _controller().get_transfer_detail(*args, **kwargs)

@frappe.whitelist()
def receive_transit_stock(*args, **kwargs):
	"""``/api/method/fadl_pos.stock.whitelist.receive_transit_stock``"""
	return _controller().receive_transit_stock(*args, **kwargs)

@frappe.whitelist()
def return_shortage_to_source(*args, **kwargs):
	"""``/api/method/fadl_pos.stock.whitelist.return_shortage_to_source``"""
	return _controller().return_shortage_to_source(*args, **kwargs)

@frappe.whitelist()
def get_stock_availability(*args, **kwargs):
	"""``/api/method/fadl_pos.stock.whitelist.get_stock_availability``"""
	return _controller().get_stock_availability(*args, **kwargs)

@frappe.whitelist()
def validate_cart_items(*args, **kwargs):
	"""``/api/method/fadl_pos.stock.whitelist.validate_cart_items``"""
	return _controller().validate_cart_items(*args, **kwargs)
