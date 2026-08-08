# Copyright (c) 2026, FadlTech team and contributors

"""Pydantic schemas for POS role permission RPC."""

from __future__ import annotations

from pydantic import ConfigDict, Field

from fadl_pos.core.serializer import InputSchema, OutputSchema
from fadl_pos.permissions.constants import ALL_PERMISSION_KEYS


class PosProfileIn(InputSchema):
	pos_profile: str | None = None


class PosUsersIn(InputSchema):
	limit_start: int = Field(default=0, ge=0)
	limit_page_length: int = Field(default=100, ge=1, le=500)


class SetRolePermissionIn(InputSchema):
	role: str = Field(min_length=1)
	permission: str = Field(min_length=1)
	enabled: bool | int | str = 0


class RolePermissionFlagsOut(OutputSchema):
	model_config = ConfigDict(extra="allow", str_strip_whitespace=True)


class RolePermissionSetOut(OutputSchema):
	role: str
	permission: str
	enabled: int | bool


class RoleRowOut(OutputSchema):
	name: str
	role_name: str


class PermissionRowOut(OutputSchema):
	name: str
	label: str
	group: str = "Other"


class RolePermissionMatrixOut(OutputSchema):
	roles: list[dict]
	permissions: list[dict]
	matrix: dict


class PosUserOut(OutputSchema):
	model_config = ConfigDict(extra="allow", str_strip_whitespace=True)
	name: str
	username: str | None = None
	full_name: str | None = None
	enabled: int | bool = 0
	modified: str | None = None
	password_hash: str = ""
	role: str = ""
	pos_profile: str = ""
	warehouse: str = ""
	company: str = ""
	theme: str = "Default"
	discount_limit: float = 100


PERMISSION_KEY_SET = set(ALL_PERMISSION_KEYS)
