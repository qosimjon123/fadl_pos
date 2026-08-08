# Copyright (c) 2026, FadlTech team and contributors

"""Canonical POS permission catalog (ported from xpos.install / xpos.api.auth)."""

from __future__ import annotations

POS_PERMISSIONS = (
	# Billing & Invoicing
	("close_shift", "Close Shift", "Billing & Invoicing"),
	("allow_reprint_invoice", "Reprint Invoice", "Billing & Invoicing"),
	("print_draft_invoice", "Print Draft Invoice", "Billing & Invoicing"),
	("shift_report", "Shift Report", "Billing & Invoicing"),
	# Discounts & Pricing
	("apply_additional_discount", "Apply Additional Discount", "Discounts & Pricing"),
	("show_edit_discount_field", "Edit Discount Field", "Discounts & Pricing"),
	("allow_change_price", "Change Price", "Discounts & Pricing"),
	# Sales Operations
	("sale_return", "Sale Return", "Sales Operations"),
	# Cash Management
	("expense", "Expense", "Cash Management"),
	("bank_drop", "Bank Drop", "Cash Management"),
	# Reports
	("current_stock_by_brand", "Current Stock by Brand", "Reports"),
	("current_stock_report", "Current Stock Report", "Reports"),
	# Administration
	("manage_role_permissions", "Manage Role Permissions", "Administration"),
)

ALL_PERMISSION_KEYS = tuple(name for name, _label, _group in POS_PERMISSIONS)
ALL_PERMISSION_NAMES = ALL_PERMISSION_KEYS

DEFAULT_ROLE = "Cashier"
DEFAULT_DISCOUNT_LIMIT = 100.0
_ROLE_CACHE_KEY = "fadl_pos_role_permissions"

_CASHIER_ENABLED: set[str] = set()
_MANAGER_DISABLED = {"manage_role_permissions"}

DEFAULT_ROLES = (
	("Cashier", _CASHIER_ENABLED),
	("Manager", set(ALL_PERMISSION_NAMES) - _MANAGER_DISABLED),
	("Administrator", set(ALL_PERMISSION_NAMES)),
)
