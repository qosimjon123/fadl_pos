# Copyright (c) 2026, FadlTech team and contributors

"""POS Role / Permission matrix business logic (ported from xpos.api.auth)."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import cint, flt

from fadl_pos.core.permission import BaseController
from fadl_pos.permissions import events
from fadl_pos.permissions.constants import (
	ALL_PERMISSION_KEYS,
	DEFAULT_DISCOUNT_LIMIT,
	DEFAULT_ROLE,
	POS_PERMISSIONS,
)
from fadl_pos.permissions.permission import (
	all_enabled,
	clear_role_permission_cache,
	get_role_permissions,
	get_user_pos_role,
	is_superuser,
	require_manage_permissions,
	resolve_role_permissions,
)


class PermissionsController(BaseController):
	def get_my_pos_permissions(self, pos_profile: str | None = None) -> dict:
		user = self.user
		if is_superuser(user):
			return all_enabled()
		role_name = get_user_pos_role(user, pos_profile)
		return get_role_permissions(role_name)

	def get_current_user_permissions(self) -> dict:
		user = self.user
		role_name = get_user_pos_role(user)
		if is_superuser(user):
			permissions = all_enabled()
		else:
			permissions = get_role_permissions(role_name)
		return {"role": role_name, "permissions": permissions}

	def get_pos_users(self, limit_start: int = 0, limit_page_length: int = 100) -> list[dict]:
		limit_start = cint(limit_start)
		limit_page_length = cint(limit_page_length)
		profile_users = frappe.db.sql(
			"""
			SELECT user, pos_profile, pos_role, discount_limit, warehouse, company
			FROM (
				SELECT pu.user, pu.parent AS pos_profile, pu.pos_role, pu.discount_limit,
					pp.warehouse, pp.company,
					ROW_NUMBER() OVER (
						PARTITION BY pu.user ORDER BY pu.parent ASC, pu.idx ASC
					) AS rn
				FROM `tabPOS Profile User` pu
				INNER JOIN `tabPOS Profile` pp ON pp.name = pu.parent
				WHERE pp.disabled = 0
			) ranked
			WHERE rn = 1
			ORDER BY user
			LIMIT %(limit)s OFFSET %(offset)s
			""",
			{"limit": limit_page_length, "offset": limit_start},
			as_dict=True,
		)
		if not profile_users:
			return []

		user_meta = {
			u.name: u
			for u in frappe.get_all(
				"User",
				filters={"name": ["in", [r.user for r in profile_users]]},
				fields=["name", "username", "full_name", "enabled", "modified"],
				ignore_permissions=True,
			)
		}

		results = []
		for pu in profile_users:
			user = user_meta.get(pu.user)
			if not user:
				continue
			role_name = pu.pos_role or DEFAULT_ROLE
			perms = get_role_permissions(role_name)
			discount_limit = (
				flt(pu.discount_limit) if pu.discount_limit not in (None, "") else DEFAULT_DISCOUNT_LIMIT
			)
			results.append(
				{
					"name": user.name,
					"username": user.username or user.name,
					"full_name": user.full_name or user.name,
					"enabled": cint(user.enabled),
					"modified": str(user.modified) if user.modified else None,
					"password_hash": "",
					"role": role_name,
					"pos_profile": pu.pos_profile or "",
					"warehouse": pu.warehouse or "",
					"company": pu.company or "",
					"theme": "Default",
					"discount_limit": discount_limit,
					**{key: cint(perms.get(key, False)) for key in ALL_PERMISSION_KEYS},
				}
			)
		return results

	def get_role_permission_matrix(self) -> dict:
		require_manage_permissions()
		roles = frappe.get_all(
			"POS Role",
			fields=["name", "role_name"],
			order_by="role_name asc",
			ignore_permissions=True,
		)
		permissions = frappe.get_all(
			"POS Permission",
			fields=["name", "permission_label as label"],
			ignore_permissions=True,
		)
		group_of = {name: group for name, _label, group in POS_PERMISSIONS}
		order = {name: idx for idx, (name, _l, _g) in enumerate(POS_PERMISSIONS)}
		for perm in permissions:
			perm["group"] = group_of.get(perm.name, "Other")
		permissions.sort(key=lambda p: order.get(p["name"], len(order)))

		matrix: dict[str, dict[str, bool]] = {}
		for role in roles:
			matrix[role.name] = resolve_role_permissions(role.name)

		return {"roles": roles, "permissions": permissions, "matrix": matrix}

	def set_role_permission(self, role: str, permission: str, enabled: bool | int | str) -> dict:
		require_manage_permissions()
		if not frappe.db.exists("POS Role", role):
			frappe.throw(_("POS Role {0} not found").format(role))

		enabled_flag = 1 if cint(enabled) else 0
		doc = frappe.get_doc("POS Role", role)
		target = next((row for row in doc.permissions if row.permission == permission), None)
		if target:
			target.enabled = enabled_flag
		else:
			doc.append("permissions", {"permission": permission, "enabled": enabled_flag})
		doc.save(ignore_permissions=True)
		clear_role_permission_cache(role)
		events.role_permission_updated(
			role=role, permission=permission, enabled=bool(enabled_flag), user=self.user
		)
		return {"role": role, "permission": permission, "enabled": enabled_flag}

	@staticmethod
	def get_user_discount_limit(user_name: str, pos_profile: str | None) -> float:
		if not pos_profile:
			return DEFAULT_DISCOUNT_LIMIT
		value = frappe.db.get_value(
			"POS Profile User",
			{"parent": pos_profile, "parenttype": "POS Profile", "user": user_name},
			"discount_limit",
		)
		return flt(value) if value not in (None, "") else DEFAULT_DISCOUNT_LIMIT
