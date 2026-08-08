# Copyright (c) 2026, FadlTech team and contributors

"""Bootinfo extension for desk/session clients (ported from xpos.startup.boot)."""

from __future__ import annotations

import frappe

from fadl_pos.permissions.controller import PermissionsController
from fadl_pos.permissions.permission import can_manage_role_permissions
from fadl_pos.settings.processing.settings import get_branding_payload


def extend_bootinfo(bootinfo):
	"""Extend Frappe boot session with POS reference data and rights."""
	if frappe.session.user == "Guest":
		return

	bootinfo.countries = frappe.get_all("Country", fields=["name"], order_by="name asc")
	bootinfo.currencies = frappe.get_all(
		"Currency",
		filters={"enabled": 1},
		fields=["name", "currency_name", "symbol"],
		order_by="name asc",
	)
	bootinfo.territories = frappe.get_all(
		"Territory",
		filters={"is_group": 0},
		fields=["name", "territory_name"],
		order_by="territory_name asc",
	)
	bootinfo.selling_settings = frappe.get_single("Selling Settings")
	bootinfo.accounts_setting = frappe.get_single("Accounts Settings")
	bootinfo.buying_settings = frappe.get_single("Buying Settings")
	bootinfo.stock_settings = frappe.get_single("Stock Settings")
	bootinfo.pos_settings = frappe.get_single("POS Settings")

	user_rights = PermissionsController().get_current_user_permissions()
	# fadl_pos_* keys are canonical; xpos_* kept as aliases for any leftover clients.
	bootinfo.fadl_pos_role = user_rights.get("role")
	bootinfo.fadl_pos_permissions = user_rights.get("permissions")
	bootinfo.fadl_pos_is_system_manager = (
		frappe.session.user == "Administrator" or "System Manager" in frappe.get_roles(frappe.session.user)
	)
	bootinfo.fadl_pos_can_manage_permissions = can_manage_role_permissions()
	bootinfo.fadl_pos_branding = get_branding_payload()

	bootinfo.xpos_role = bootinfo.fadl_pos_role
	bootinfo.xpos_permissions = bootinfo.fadl_pos_permissions
	bootinfo.xpos_is_system_manager = bootinfo.fadl_pos_is_system_manager
	bootinfo.xpos_can_manage_permissions = bootinfo.fadl_pos_can_manage_permissions
	bootinfo.xpos_branding = bootinfo.fadl_pos_branding
