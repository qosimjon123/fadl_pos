# Copyright (c) 2026, FadlTech team and contributors

"""catalog RPC endpoints for Frappe `/api/method/...` calls."""

from __future__ import annotations

import frappe

from fadl_pos.catalog.controller import CatalogController


def _controller() -> CatalogController:
	return CatalogController()


@frappe.whitelist()
def get_pos_items(*args, **kwargs):
	"""``/api/method/fadl_pos.catalog.whitelist.get_pos_items``"""
	return _controller().get_pos_items(*args, **kwargs)

@frappe.whitelist()
def get_items_count(*args, **kwargs):
	"""``/api/method/fadl_pos.catalog.whitelist.get_items_count``"""
	return _controller().get_items_count(*args, **kwargs)

@frappe.whitelist()
def get_item_groups(*args, **kwargs):
	"""``/api/method/fadl_pos.catalog.whitelist.get_item_groups``"""
	return _controller().get_item_groups(*args, **kwargs)

@frappe.whitelist()
def search_barcode(*args, **kwargs):
	"""``/api/method/fadl_pos.catalog.whitelist.search_barcode``"""
	return _controller().search_barcode(*args, **kwargs)

@frappe.whitelist()
def get_item_detail(*args, **kwargs):
	"""``/api/method/fadl_pos.catalog.whitelist.get_item_detail``"""
	return _controller().get_item_detail(*args, **kwargs)

@frappe.whitelist()
def get_item_variants(*args, **kwargs):
	"""``/api/method/fadl_pos.catalog.whitelist.get_item_variants``"""
	return _controller().get_item_variants(*args, **kwargs)

@frappe.whitelist()
def get_item_attributes(*args, **kwargs):
	"""``/api/method/fadl_pos.catalog.whitelist.get_item_attributes``"""
	return _controller().get_item_attributes(*args, **kwargs)

@frappe.whitelist()
def update_price_list_rate(*args, **kwargs):
	"""``/api/method/fadl_pos.catalog.whitelist.update_price_list_rate``"""
	return _controller().update_price_list_rate(*args, **kwargs)

@frappe.whitelist()
def get_price_for_uom(*args, **kwargs):
	"""``/api/method/fadl_pos.catalog.whitelist.get_price_for_uom``"""
	return _controller().get_price_for_uom(*args, **kwargs)

@frappe.whitelist()
def get_bundle_components(*args, **kwargs):
	"""``/api/method/fadl_pos.catalog.whitelist.get_bundle_components``"""
	return _controller().get_bundle_components(*args, **kwargs)

@frappe.whitelist()
def lookup(*args, **kwargs):
	"""``/api/method/fadl_pos.catalog.whitelist.lookup``"""
	return _controller().lookup(*args, **kwargs)

@frappe.whitelist()
def get_terminal_context(*args, **kwargs):
	"""``/api/method/fadl_pos.catalog.whitelist.get_terminal_context``"""
	return _controller().get_terminal_context(*args, **kwargs)
