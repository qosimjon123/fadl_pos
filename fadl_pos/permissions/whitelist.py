# Copyright (c) 2026, FadlTech team and contributors

"""POS permissions RPC endpoints."""

from __future__ import annotations

import frappe

from fadl_pos.core.serializer import dump_out, dump_out_list, validate_in
from fadl_pos.permissions.controller import PermissionsController
from fadl_pos.permissions.serializer import (
	PosProfileIn,
	PosUserOut,
	PosUsersIn,
	RolePermissionFlagsOut,
	RolePermissionMatrixOut,
	RolePermissionSetOut,
	SetRolePermissionIn,
)


def _controller() -> PermissionsController:
	return PermissionsController()


@frappe.whitelist(methods=["GET", "POST"])
def get_my_pos_permissions(pos_profile: str | None = None):
	"""``/api/method/fadl_pos.permissions.whitelist.get_my_pos_permissions``"""
	body = validate_in(PosProfileIn, {"pos_profile": pos_profile})
	return dump_out(RolePermissionFlagsOut, _controller().get_my_pos_permissions(body.pos_profile))


@frappe.whitelist(methods=["GET", "POST"])
def get_pos_users(limit_start: int = 0, limit_page_length: int = 100):
	"""``/api/method/fadl_pos.permissions.whitelist.get_pos_users``"""
	body = validate_in(
		PosUsersIn,
		{"limit_start": limit_start, "limit_page_length": limit_page_length},
	)
	return dump_out_list(
		PosUserOut,
		_controller().get_pos_users(body.limit_start, body.limit_page_length),
	)


@frappe.whitelist(methods=["GET", "POST"])
def get_role_permission_matrix():
	"""``/api/method/fadl_pos.permissions.whitelist.get_role_permission_matrix``"""
	return dump_out(RolePermissionMatrixOut, _controller().get_role_permission_matrix())


@frappe.whitelist(methods=["POST"])
def set_role_permission(role: str | None = None, permission: str | None = None, enabled=0):
	"""``/api/method/fadl_pos.permissions.whitelist.set_role_permission``"""
	body = validate_in(
		SetRolePermissionIn,
		{"role": role or "", "permission": permission or "", "enabled": enabled},
	)
	return dump_out(
		RolePermissionSetOut,
		_controller().set_role_permission(body.role, body.permission, body.enabled),
	)
