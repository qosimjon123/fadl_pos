# Copyright (c) 2026, FadlTech team and contributors

"""cash RPC endpoints for Frappe `/api/method/...` calls."""

from __future__ import annotations

import frappe

from fadl_pos.cash.controller import CashController


def _controller() -> CashController:
	return CashController()


@frappe.whitelist()
def get_cash_movement_context(*args, **kwargs):
	"""``/api/method/fadl_pos.cash.whitelist.get_cash_movement_context``"""
	return _controller().get_cash_movement_context(*args, **kwargs)


@frappe.whitelist()
def create_pos_expense(*args, **kwargs):
	"""``/api/method/fadl_pos.cash.whitelist.create_pos_expense``"""
	return _controller().create_pos_expense(*args, **kwargs)


@frappe.whitelist()
def create_cash_deposit(*args, **kwargs):
	"""``/api/method/fadl_pos.cash.whitelist.create_cash_deposit``"""
	return _controller().create_cash_deposit(*args, **kwargs)


@frappe.whitelist()
def get_shift_cash_movements(*args, **kwargs):
	"""``/api/method/fadl_pos.cash.whitelist.get_shift_cash_movements``"""
	return _controller().get_shift_cash_movements(*args, **kwargs)


@frappe.whitelist()
def get_submitted_expenses(*args, **kwargs):
	"""``/api/method/fadl_pos.cash.whitelist.get_submitted_expenses``"""
	return _controller().get_submitted_expenses(*args, **kwargs)


@frappe.whitelist()
def delete_cash_movement(*args, **kwargs):
	"""``/api/method/fadl_pos.cash.whitelist.delete_cash_movement``"""
	return _controller().delete_cash_movement(*args, **kwargs)


@frappe.whitelist()
def duplicate_cash_movement(*args, **kwargs):
	"""``/api/method/fadl_pos.cash.whitelist.duplicate_cash_movement``"""
	return _controller().duplicate_cash_movement(*args, **kwargs)
