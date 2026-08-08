# Copyright (c) 2026, FadlTech team and contributors

"""sync RPC endpoints for Frappe `/api/method/...` calls."""

from __future__ import annotations

import frappe

from fadl_pos.sync.controller import SyncController


def _controller() -> SyncController:
	return SyncController()


@frappe.whitelist()
def get_child_table_data(*args, **kwargs):
	"""``/api/method/fadl_pos.sync.whitelist.get_child_table_data``"""
	return _controller().get_child_table_data(*args, **kwargs)

@frappe.whitelist()
def get_item_prices(*args, **kwargs):
	"""``/api/method/fadl_pos.sync.whitelist.get_item_prices``"""
	return _controller().get_item_prices(*args, **kwargs)
