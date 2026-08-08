# Copyright (c) 2026, FadlTech team and contributors

"""Install / migrate hooks: custom fields, POS Permission catalog, default roles."""

from __future__ import annotations

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from fadl_pos.permissions.constants import ALL_PERMISSION_NAMES, DEFAULT_ROLES, POS_PERMISSIONS


def after_install():
	seed_pos_permissions()
	seed_default_roles()


def after_migrate():
	# update=True — при изменении label/description в коде запись Custom Field в БД обновится
	# (одиночный create_custom_field не трогает уже существующее поле).
	create_custom_fields(
		{
			"User": [
				{
					"fieldname": "qr_encrypted_data",
					"label": "QR Encrypted Data",
					"fieldtype": "Long Text",
					"insert_after": "api_secret",
					"module": "Fadl Pos",
					"description": "Current encrypted Fadl POS QR payload. Regenerated QR keys replace this value.",
					"print_hide": 1,
					"is_system_generated": 0,
				}
			]
		},
		update=True,
	)
	# Idempotent seed so existing sites pick up new permission keys.
	seed_pos_permissions()
	seed_default_roles()
	_cleanup_shift_leftovers()


def _cleanup_shift_leftovers() -> None:
	"""Remove stale POS Profile shift CF after all apps sync customizations."""
	from fadl_pos.patches.remove_pos_coupon_referral import execute as cleanup

	cleanup()


def seed_pos_permissions():
	"""Upsert the static POS Permission catalog. Idempotent."""
	if not frappe.db.exists("DocType", "POS Permission"):
		return
	for permission_name, permission_label, _group in POS_PERMISSIONS:
		if frappe.db.exists("POS Permission", permission_name):
			continue
		frappe.get_doc(
			{
				"doctype": "POS Permission",
				"permission_name": permission_name,
				"permission_label": permission_label,
			}
		).insert(ignore_permissions=True)


def seed_default_roles():
	"""Create the default POS Role records with their child permission rows."""
	if not frappe.db.exists("DocType", "POS Role"):
		return
	for role_name, enabled_set in DEFAULT_ROLES:
		if frappe.db.exists("POS Role", role_name):
			continue
		role = frappe.get_doc({"doctype": "POS Role", "role_name": role_name})
		for permission_name in ALL_PERMISSION_NAMES:
			role.append(
				"permissions",
				{
					"permission": permission_name,
					"enabled": 1 if permission_name in enabled_set else 0,
				},
			)
		role.insert(ignore_permissions=True)
