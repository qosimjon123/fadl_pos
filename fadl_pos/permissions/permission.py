# Copyright (c) 2026, FadlTech team and contributors

"""Guards for POS role permission management."""

from __future__ import annotations

import frappe
from frappe import _

from fadl_pos.core.permission import require_session_user
from fadl_pos.permissions.constants import ALL_PERMISSION_KEYS, DEFAULT_ROLE, _ROLE_CACHE_KEY


def is_superuser(user: str | None = None) -> bool:
	user = user or frappe.session.user
	return user == "Administrator" or "System Manager" in frappe.get_roles(user)


def resolve_role_permissions(role_name: str) -> dict[str, bool]:
	perms = {key: False for key in ALL_PERMISSION_KEYS}
	if not role_name or not frappe.db.exists("POS Role", role_name):
		return perms
	rows = frappe.get_all(
		"POS Role Permission",
		filters={"parent": role_name, "parenttype": "POS Role"},
		fields=["permission", "enabled"],
		ignore_permissions=True,
	)
	for row in rows:
		if row.permission in perms:
			perms[row.permission] = bool(row.enabled)
	return perms


def get_user_pos_role(user: str, pos_profile: str | None = None) -> str:
	filters: dict = {"user": user, "parenttype": "POS Profile"}
	if pos_profile:
		filters["parent"] = pos_profile
	rows = frappe.get_all(
		"POS Profile User",
		filters=filters,
		fields=["pos_role"],
		order_by="parent asc, idx asc",
		ignore_permissions=True,
	)
	for row in rows:
		if row.pos_role:
			return row.pos_role
	return DEFAULT_ROLE


def get_role_permissions(role_name: str) -> dict[str, bool]:
	role_name = role_name or DEFAULT_ROLE
	return frappe.cache().hget(
		_ROLE_CACHE_KEY,
		role_name,
		generator=lambda: resolve_role_permissions(role_name),
	)


def clear_role_permission_cache(role_name: str | None = None) -> None:
	if role_name:
		frappe.cache().hdel(_ROLE_CACHE_KEY, role_name)
	else:
		frappe.cache().delete_key(_ROLE_CACHE_KEY)


def clear_role_permission_cache_on_update(doc, method: str | None = None) -> None:
	"""Doc event hook for POS Role — bust cached permission maps."""
	clear_role_permission_cache(getattr(doc, "name", None))


def all_enabled() -> dict[str, bool]:
	return {key: True for key in ALL_PERMISSION_KEYS}


def user_has_pos_permission(key: str, user: str | None = None, pos_profile: str | None = None) -> bool:
	user = user or frappe.session.user
	if user == "Guest":
		return False
	if is_superuser(user):
		return True
	role_name = get_user_pos_role(user, pos_profile)
	return bool(get_role_permissions(role_name).get(key))


def can_manage_role_permissions(user: str | None = None) -> bool:
	return user_has_pos_permission("manage_role_permissions", user)


def require_manage_permissions() -> str:
	user = require_session_user()
	if not can_manage_role_permissions(user):
		frappe.throw(
			_("You are not permitted to manage POS role permissions."),
			frappe.PermissionError,
		)
	return user


def require_pos_permission(key: str, pos_profile: str | None = None, user: str | None = None) -> str:
	user = require_session_user(user)
	if not user_has_pos_permission(key, user=user, pos_profile=pos_profile):
		frappe.throw(
			_("You are not permitted to perform this POS action ({0}).").format(key),
			frappe.PermissionError,
		)
	return user
