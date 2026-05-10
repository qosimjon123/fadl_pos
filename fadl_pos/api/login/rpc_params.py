# Copyright (c) 2026, FadlTech team and contributors
"""Normalize whitelisted RPC parameters (HTTP form/JSON can send non-string types)."""

from __future__ import annotations

import frappe
from frappe import _


def optional_str_param(field_label: str, value: object | None) -> str | None:
	"""Return stripped string, None if missing, or throw if type is not usable as text."""
	if value is None:
		return None
	if isinstance(value, str):
		return value
	frappe.throw(_("{0} must be text").format(field_label), frappe.ValidationError)
