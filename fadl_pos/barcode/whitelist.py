# Copyright (c) 2026, FadlTech team and contributors

"""barcode RPC endpoints for Frappe `/api/method/...` calls."""

from __future__ import annotations

import frappe

from fadl_pos.barcode.controller import BarcodeController


def _controller() -> BarcodeController:
	return BarcodeController()


@frappe.whitelist()
def get_barcode_image(*args, **kwargs):
	"""``/api/method/fadl_pos.barcode.whitelist.get_barcode_image``"""
	return _controller().get_barcode_image(*args, **kwargs)

@frappe.whitelist()
def get_qrcode_image(*args, **kwargs):
	"""``/api/method/fadl_pos.barcode.whitelist.get_qrcode_image``"""
	return _controller().get_qrcode_image(*args, **kwargs)

@frappe.whitelist()
def get_item_barcode_labels(*args, **kwargs):
	"""``/api/method/fadl_pos.barcode.whitelist.get_item_barcode_labels``"""
	return _controller().get_item_barcode_labels(*args, **kwargs)

@frappe.whitelist()
def get_barcode_types(*args, **kwargs):
	"""``/api/method/fadl_pos.barcode.whitelist.get_barcode_types``"""
	return _controller().get_barcode_types(*args, **kwargs)

@frappe.whitelist()
def search_items_for_barcode(*args, **kwargs):
	"""``/api/method/fadl_pos.barcode.whitelist.search_items_for_barcode``"""
	return _controller().search_items_for_barcode(*args, **kwargs)
