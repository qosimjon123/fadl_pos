# Copyright (c) 2026, FadlTech team and contributors

"""Re-seed POS Permission catalog and default POS Roles on existing sites."""

from __future__ import annotations


def execute() -> None:
	from fadl_pos.install import seed_default_roles, seed_pos_permissions

	seed_pos_permissions()
	seed_default_roles()
