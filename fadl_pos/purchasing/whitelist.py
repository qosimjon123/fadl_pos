# Copyright (c) 2026, FadlTech team and contributors

"""purchasing RPC endpoints for Frappe `/api/method/...` calls."""

from __future__ import annotations

import frappe

from fadl_pos.purchasing.controller import PurchasingController


def _controller() -> PurchasingController:
	return PurchasingController()


@frappe.whitelist()
def create_supplier(*args, **kwargs):
	"""``/api/method/fadl_pos.purchasing.whitelist.create_supplier``"""
	return _controller().create_supplier(*args, **kwargs)

@frappe.whitelist()
def search_suppliers(*args, **kwargs):
	"""``/api/method/fadl_pos.purchasing.whitelist.search_suppliers``"""
	return _controller().search_suppliers(*args, **kwargs)

@frappe.whitelist()
def create_purchase_item(*args, **kwargs):
	"""``/api/method/fadl_pos.purchasing.whitelist.create_purchase_item``"""
	return _controller().create_purchase_item(*args, **kwargs)

@frappe.whitelist()
def create_purchase_order(*args, **kwargs):
	"""``/api/method/fadl_pos.purchasing.whitelist.create_purchase_order``"""
	return _controller().create_purchase_order(*args, **kwargs)

@frappe.whitelist()
def create_purchase_invoice_direct(*args, **kwargs):
	"""``/api/method/fadl_pos.purchasing.whitelist.create_purchase_invoice_direct``"""
	return _controller().create_purchase_invoice_direct(*args, **kwargs)

@frappe.whitelist()
def search_items(*args, **kwargs):
	"""``/api/method/fadl_pos.purchasing.whitelist.search_items``"""
	return _controller().search_items(*args, **kwargs)

@frappe.whitelist()
def search_item_by_barcode(*args, **kwargs):
	"""``/api/method/fadl_pos.purchasing.whitelist.search_item_by_barcode``"""
	return _controller().search_item_by_barcode(*args, **kwargs)

@frappe.whitelist()
def get_pending_receipts(*args, **kwargs):
	"""``/api/method/fadl_pos.purchasing.whitelist.get_pending_receipts``"""
	return _controller().get_pending_receipts(*args, **kwargs)

@frappe.whitelist()
def get_purchase_order_detail(*args, **kwargs):
	"""``/api/method/fadl_pos.purchasing.whitelist.get_purchase_order_detail``"""
	return _controller().get_purchase_order_detail(*args, **kwargs)

@frappe.whitelist()
def receive_stock(*args, **kwargs):
	"""``/api/method/fadl_pos.purchasing.whitelist.receive_stock``"""
	return _controller().receive_stock(*args, **kwargs)

@frappe.whitelist()
def get_stock_and_transit(*args, **kwargs):
	"""``/api/method/fadl_pos.purchasing.whitelist.get_stock_and_transit``"""
	return _controller().get_stock_and_transit(*args, **kwargs)

@frappe.whitelist()
def get_category_items(*args, **kwargs):
	"""``/api/method/fadl_pos.purchasing.whitelist.get_category_items``"""
	return _controller().get_category_items(*args, **kwargs)

@frappe.whitelist()
def save_po_draft(*args, **kwargs):
	"""``/api/method/fadl_pos.purchasing.whitelist.save_po_draft``"""
	return _controller().save_po_draft(*args, **kwargs)

@frappe.whitelist()
def load_po_draft(*args, **kwargs):
	"""``/api/method/fadl_pos.purchasing.whitelist.load_po_draft``"""
	return _controller().load_po_draft(*args, **kwargs)

@frappe.whitelist()
def delete_po_draft(*args, **kwargs):
	"""``/api/method/fadl_pos.purchasing.whitelist.delete_po_draft``"""
	return _controller().delete_po_draft(*args, **kwargs)

@frappe.whitelist()
def list_po_drafts(*args, **kwargs):
	"""``/api/method/fadl_pos.purchasing.whitelist.list_po_drafts``"""
	return _controller().list_po_drafts(*args, **kwargs)

@frappe.whitelist()
def save_pi_draft(*args, **kwargs):
	"""``/api/method/fadl_pos.purchasing.whitelist.save_pi_draft``"""
	return _controller().save_pi_draft(*args, **kwargs)

@frappe.whitelist()
def load_pi_draft(*args, **kwargs):
	"""``/api/method/fadl_pos.purchasing.whitelist.load_pi_draft``"""
	return _controller().load_pi_draft(*args, **kwargs)

@frappe.whitelist()
def delete_pi_draft(*args, **kwargs):
	"""``/api/method/fadl_pos.purchasing.whitelist.delete_pi_draft``"""
	return _controller().delete_pi_draft(*args, **kwargs)

@frappe.whitelist()
def list_pi_drafts(*args, **kwargs):
	"""``/api/method/fadl_pos.purchasing.whitelist.list_pi_drafts``"""
	return _controller().list_pi_drafts(*args, **kwargs)

@frappe.whitelist()
def submit_pi_draft(*args, **kwargs):
	"""``/api/method/fadl_pos.purchasing.whitelist.submit_pi_draft``"""
	return _controller().submit_pi_draft(*args, **kwargs)

@frappe.whitelist()
def get_purchase_orders_for_invoice(*args, **kwargs):
	"""``/api/method/fadl_pos.purchasing.whitelist.get_purchase_orders_for_invoice``"""
	return _controller().get_purchase_orders_for_invoice(*args, **kwargs)

@frappe.whitelist()
def get_item_purchase_details(*args, **kwargs):
	"""``/api/method/fadl_pos.purchasing.whitelist.get_item_purchase_details``"""
	return _controller().get_item_purchase_details(*args, **kwargs)

@frappe.whitelist()
def get_purchase_tax_template(*args, **kwargs):
	"""``/api/method/fadl_pos.purchasing.whitelist.get_purchase_tax_template``"""
	return _controller().get_purchase_tax_template(*args, **kwargs)
