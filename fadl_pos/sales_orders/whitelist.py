# Copyright (c) 2026, FadlTech team and contributors

"""sales_orders RPC endpoints for Frappe `/api/method/...` calls."""

from __future__ import annotations

import frappe

from fadl_pos.sales_orders.controller import SalesOrdersController


def _controller() -> SalesOrdersController:
	return SalesOrdersController()


@frappe.whitelist()
def search_orders(*args, **kwargs):
	"""``/api/method/fadl_pos.sales_orders.whitelist.search_orders``"""
	return _controller().search_orders(*args, **kwargs)

@frappe.whitelist()
def create_sales_order(*args, **kwargs):
	"""``/api/method/fadl_pos.sales_orders.whitelist.create_sales_order``"""
	return _controller().create_sales_order(*args, **kwargs)

@frappe.whitelist()
def submit_sales_order(*args, **kwargs):
	"""``/api/method/fadl_pos.sales_orders.whitelist.submit_sales_order``"""
	return _controller().submit_sales_order(*args, **kwargs)

@frappe.whitelist()
def create_sales_invoice_from_order(*args, **kwargs):
	"""``/api/method/fadl_pos.sales_orders.whitelist.create_sales_invoice_from_order``"""
	return _controller().create_sales_invoice_from_order(*args, **kwargs)

@frappe.whitelist()
def create_quotation(*args, **kwargs):
	"""``/api/method/fadl_pos.sales_orders.whitelist.create_quotation``"""
	return _controller().create_quotation(*args, **kwargs)

@frappe.whitelist()
def submit_quotation(*args, **kwargs):
	"""``/api/method/fadl_pos.sales_orders.whitelist.submit_quotation``"""
	return _controller().submit_quotation(*args, **kwargs)
