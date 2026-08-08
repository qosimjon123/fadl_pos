# Copyright (c) 2026, FadlTech team and contributors

"""printing RPC endpoints for Frappe `/api/method/...` calls."""

from __future__ import annotations

import frappe

from fadl_pos.printing.controller import PrintingController


def _controller() -> PrintingController:
	return PrintingController()


@frappe.whitelist()
def get_print_formats(*args, **kwargs):
	"""``/api/method/fadl_pos.printing.whitelist.get_print_formats``"""
	return _controller().get_print_formats(*args, **kwargs)


@frappe.whitelist()
def get_receipt_context(*args, **kwargs):
	"""``/api/method/fadl_pos.printing.whitelist.get_receipt_context``"""
	return _controller().get_receipt_context(*args, **kwargs)


@frappe.whitelist()
def mark_invoice_printed(*args, **kwargs):
	"""``/api/method/fadl_pos.printing.whitelist.mark_invoice_printed``"""
	return _controller().mark_invoice_printed(*args, **kwargs)


@frappe.whitelist()
def get_certificate(*args, **kwargs):
	"""``/api/method/fadl_pos.printing.whitelist.get_certificate``"""
	return _controller().get_certificate(*args, **kwargs)


@frappe.whitelist()
def get_certificate_download(*args, **kwargs):
	"""``/api/method/fadl_pos.printing.whitelist.get_certificate_download``"""
	return _controller().get_certificate_download(*args, **kwargs)


@frappe.whitelist()
def sign_message(*args, **kwargs):
	"""``/api/method/fadl_pos.printing.whitelist.sign_message``"""
	return _controller().sign_message(*args, **kwargs)


@frappe.whitelist()
def setup_qz_certificate(*args, **kwargs):
	"""``/api/method/fadl_pos.printing.whitelist.setup_qz_certificate``"""
	return _controller().setup_qz_certificate(*args, **kwargs)
