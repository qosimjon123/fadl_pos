# Copyright (c) 2026, FadlTech team and contributors

"""utilities RPC endpoints — sole @frappe.whitelist surface."""

from __future__ import annotations

import frappe

from fadl_pos.utilities.controller import UtilitiesController


def _controller() -> UtilitiesController:
	return UtilitiesController()


@frappe.whitelist()
def get_version_info(*args, **kwargs):
	return _controller().get_version_info(*args, **kwargs)


@frappe.whitelist()
def get_selling_price_lists(*args, **kwargs):
	return _controller().get_selling_price_lists(*args, **kwargs)


@frappe.whitelist()
def get_pos_profile_tax_inclusive(*args, **kwargs):
	return _controller().get_pos_profile_tax_inclusive(*args, **kwargs)


@frappe.whitelist()
def get_active_pos_profile(*args, **kwargs):
	return _controller().get_active_pos_profile(*args, **kwargs)


@frappe.whitelist()
def get_default_warehouse(*args, **kwargs):
	return _controller().get_default_warehouse(*args, **kwargs)


@frappe.whitelist()
def get_sales_person_names(*args, **kwargs):
	return _controller().get_sales_person_names(*args, **kwargs)


@frappe.whitelist()
def get_language_options(*args, **kwargs):
	return _controller().get_language_options(*args, **kwargs)


@frappe.whitelist()
def get_translation_dict(*args, **kwargs):
	return _controller().get_translation_dict(*args, **kwargs)


@frappe.whitelist()
def get_database_usage(*args, **kwargs):
	return _controller().get_database_usage(*args, **kwargs)


@frappe.whitelist()
def get_server_usage(*args, **kwargs):
	return _controller().get_server_usage(*args, **kwargs)


@frappe.whitelist()
def get_available_languages(*args, **kwargs):
	return _controller().get_available_languages(*args, **kwargs)


@frappe.whitelist()
def get_current_user_language(*args, **kwargs):
	return _controller().get_current_user_language(*args, **kwargs)


@frappe.whitelist()
def set_current_user_language(*args, **kwargs):
	return _controller().set_current_user_language(*args, **kwargs)


@frappe.whitelist()
def get_language_info(*args, **kwargs):
	return _controller().get_language_info(*args, **kwargs)


@frappe.whitelist()
def log_client_error(*args, **kwargs):
	return _controller().log_client_error(*args, **kwargs)
