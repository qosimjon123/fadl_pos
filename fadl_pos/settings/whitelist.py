# Copyright (c) 2026, FadlTech team and contributors

"""settings RPC endpoints for Frappe `/api/method/...` calls."""

from __future__ import annotations

import frappe

from fadl_pos.settings.controller import SettingsController


def _controller() -> SettingsController:
	return SettingsController()


@frappe.whitelist()
def get_erp_settings(*args, **kwargs):
	"""``/api/method/fadl_pos.settings.whitelist.get_erp_settings``"""
	return _controller().get_erp_settings(*args, **kwargs)

@frappe.whitelist()
def get_xpos_branding(*args, **kwargs):
	"""``/api/method/fadl_pos.settings.whitelist.get_xpos_branding``"""
	return _controller().get_xpos_branding(*args, **kwargs)

@frappe.whitelist()
def get_currencies(*args, **kwargs):
	"""``/api/method/fadl_pos.settings.whitelist.get_currencies``"""
	return _controller().get_currencies(*args, **kwargs)

@frappe.whitelist()
def get_languages(*args, **kwargs):
	"""``/api/method/fadl_pos.settings.whitelist.get_languages``"""
	return _controller().get_languages(*args, **kwargs)
