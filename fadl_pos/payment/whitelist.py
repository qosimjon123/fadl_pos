# Copyright (c) 2026, FadlTech team and contributors

"""payment RPC endpoints for Frappe `/api/method/...` calls."""

from __future__ import annotations

import frappe

from fadl_pos.payment.controller import PaymentController


def _controller() -> PaymentController:
	return PaymentController()


@frappe.whitelist()
def get_available_credit(*args, **kwargs):
	"""``/api/method/fadl_pos.payment.whitelist.get_available_credit``"""
	return _controller().get_available_credit(*args, **kwargs)

@frappe.whitelist()
def get_outstanding_invoices(*args, **kwargs):
	"""``/api/method/fadl_pos.payment.whitelist.get_outstanding_invoices``"""
	return _controller().get_outstanding_invoices(*args, **kwargs)

@frappe.whitelist()
def get_unallocated_payments(*args, **kwargs):
	"""``/api/method/fadl_pos.payment.whitelist.get_unallocated_payments``"""
	return _controller().get_unallocated_payments(*args, **kwargs)

@frappe.whitelist()
def create_payment_entry(*args, **kwargs):
	"""``/api/method/fadl_pos.payment.whitelist.create_payment_entry``"""
	return _controller().create_payment_entry(*args, **kwargs)

@frappe.whitelist()
def create_payment_request(*args, **kwargs):
	"""``/api/method/fadl_pos.payment.whitelist.create_payment_request``"""
	return _controller().create_payment_request(*args, **kwargs)

@frappe.whitelist()
def process_pos_payment(*args, **kwargs):
	"""``/api/method/fadl_pos.payment.whitelist.process_pos_payment``"""
	return _controller().process_pos_payment(*args, **kwargs)
