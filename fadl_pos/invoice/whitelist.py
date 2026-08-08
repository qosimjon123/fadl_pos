# Copyright (c) 2026, FadlTech team and contributors

"""invoice RPC endpoints for Frappe `/api/method/...` calls."""

from __future__ import annotations

import frappe

from fadl_pos.invoice.controller import InvoiceController


def _controller() -> InvoiceController:
	return InvoiceController()


@frappe.whitelist()
def create_invoice(*args, **kwargs):
	"""``/api/method/fadl_pos.invoice.whitelist.create_invoice``"""
	return _controller().create_invoice(*args, **kwargs)

@frappe.whitelist()
def finalize_fiscal_invoice(*args, **kwargs):
	"""``/api/method/fadl_pos.invoice.whitelist.finalize_fiscal_invoice``"""
	return _controller().finalize_fiscal_invoice(*args, **kwargs)

@frappe.whitelist()
def discard_draft_invoice(*args, **kwargs):
	"""``/api/method/fadl_pos.invoice.whitelist.discard_draft_invoice``"""
	return _controller().discard_draft_invoice(*args, **kwargs)

@frappe.whitelist()
def save_draft_invoice(*args, **kwargs):
	"""``/api/method/fadl_pos.invoice.whitelist.save_draft_invoice``"""
	return _controller().save_draft_invoice(*args, **kwargs)

@frappe.whitelist()
def get_draft_invoices(*args, **kwargs):
	"""``/api/method/fadl_pos.invoice.whitelist.get_draft_invoices``"""
	return _controller().get_draft_invoices(*args, **kwargs)

@frappe.whitelist()
def get_unsettled_invoices(*args, **kwargs):
	"""``/api/method/fadl_pos.invoice.whitelist.get_unsettled_invoices``"""
	return _controller().get_unsettled_invoices(*args, **kwargs)

@frappe.whitelist()
def get_past_orders(*args, **kwargs):
	"""``/api/method/fadl_pos.invoice.whitelist.get_past_orders``"""
	return _controller().get_past_orders(*args, **kwargs)

@frappe.whitelist()
def get_invoices(*args, **kwargs):
	"""``/api/method/fadl_pos.invoice.whitelist.get_invoices``"""
	return _controller().get_invoices(*args, **kwargs)

@frappe.whitelist()
def get_invoice_details(*args, **kwargs):
	"""``/api/method/fadl_pos.invoice.whitelist.get_invoice_details``"""
	return _controller().get_invoice_details(*args, **kwargs)

@frappe.whitelist()
def delete_draft_invoice(*args, **kwargs):
	"""``/api/method/fadl_pos.invoice.whitelist.delete_draft_invoice``"""
	return _controller().delete_draft_invoice(*args, **kwargs)

@frappe.whitelist()
def search_invoices_for_return(*args, **kwargs):
	"""``/api/method/fadl_pos.invoice.whitelist.search_invoices_for_return``"""
	return _controller().search_invoices_for_return(*args, **kwargs)

@frappe.whitelist()
def get_invoice_for_return(*args, **kwargs):
	"""``/api/method/fadl_pos.invoice.whitelist.get_invoice_for_return``"""
	return _controller().get_invoice_for_return(*args, **kwargs)

@frappe.whitelist()
def fetch_exchange_rate(*args, **kwargs):
	"""``/api/method/fadl_pos.invoice.whitelist.fetch_exchange_rate``"""
	return _controller().fetch_exchange_rate(*args, **kwargs)

@frappe.whitelist()
def get_last_invoice_rates(*args, **kwargs):
	"""``/api/method/fadl_pos.invoice.whitelist.get_last_invoice_rates``"""
	return _controller().get_last_invoice_rates(*args, **kwargs)

@frappe.whitelist()
def search_invoices_for_repeat(*args, **kwargs):
	"""``/api/method/fadl_pos.invoice.whitelist.search_invoices_for_repeat``"""
	return _controller().search_invoices_for_repeat(*args, **kwargs)

@frappe.whitelist()
def get_invoice_for_repeat(*args, **kwargs):
	"""``/api/method/fadl_pos.invoice.whitelist.get_invoice_for_repeat``"""
	return _controller().get_invoice_for_repeat(*args, **kwargs)

@frappe.whitelist()
def update_invoice(*args, **kwargs):
	"""``/api/method/fadl_pos.invoice.whitelist.update_invoice``"""
	return _controller().update_invoice(*args, **kwargs)

@frappe.whitelist()
def submit_invoice(*args, **kwargs):
	"""``/api/method/fadl_pos.invoice.whitelist.submit_invoice``"""
	return _controller().submit_invoice(*args, **kwargs)

@frappe.whitelist()
def validate_cart_items(*args, **kwargs):
	"""``/api/method/fadl_pos.invoice.whitelist.validate_cart_items``"""
	return _controller().validate_cart_items(*args, **kwargs)
