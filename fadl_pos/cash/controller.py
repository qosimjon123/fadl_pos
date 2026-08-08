# Copyright (c) 2026, FadlTech team and contributors

"""cash controller — wraps ported xpos cash-movement processing service."""

from __future__ import annotations

from fadl_pos.cash.processing import service as cash_service
from fadl_pos.core.permission import BaseController


class CashController(BaseController):
	def get_cash_movement_context(self, *args, **kwargs):
		return cash_service.get_cash_movement_context(*args, **kwargs)

	def create_pos_expense(self, *args, **kwargs):
		return cash_service.create_pos_expense(*args, **kwargs)

	def create_cash_deposit(self, *args, **kwargs):
		return cash_service.create_cash_deposit(*args, **kwargs)

	def get_shift_cash_movements(self, *args, **kwargs):
		return cash_service.get_shift_cash_movements(*args, **kwargs)

	def get_submitted_expenses(self, *args, **kwargs):
		return cash_service.get_submitted_expenses(*args, **kwargs)

	def delete_cash_movement(self, *args, **kwargs):
		return cash_service.delete_cash_movement(*args, **kwargs)

	def duplicate_cash_movement(self, *args, **kwargs):
		return cash_service.duplicate_cash_movement(*args, **kwargs)
