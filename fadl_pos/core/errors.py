# Copyright (c) 2026, FadlTech team and contributors

"""Unified `frappe.throw` wrappers shared by every feature module."""

from __future__ import annotations

import frappe
from frappe import _
from pydantic import ValidationError


def auth_error(message: str) -> None:
	frappe.throw(_(message), frappe.AuthenticationError)


def permission_error(message: str) -> None:
	frappe.throw(_(message), frappe.PermissionError)


def validation_error(exc: ValidationError) -> None:
	frappe.throw(str(exc.errors()), frappe.ValidationError)
