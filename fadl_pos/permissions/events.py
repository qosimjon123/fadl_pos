# Copyright (c) 2026, FadlTech team and contributors

"""Permissions domain events."""

from __future__ import annotations

from fadl_pos.core.events import emit

ROLE_PERMISSION_UPDATED = "permissions.role_permission_updated"


def role_permission_updated(*, role: str, permission: str, enabled: bool, user: str) -> None:
	emit(ROLE_PERMISSION_UPDATED, role=role, permission=permission, enabled=enabled, user=user)
