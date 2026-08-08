# Copyright (c) 2026, FadlTech team and contributors

"""Unit tests for session opening/closing balance normalization."""

from __future__ import annotations

import unittest
from types import SimpleNamespace

import frappe

from fadl_pos.session.controller import SessionController


def _pm(
	name: str,
	*,
	required: int = 0,
	pos_profile: str = "POS-1",
) -> dict:
	return {
		"pos_profile": pos_profile,
		"mode_of_payment": name,
		"default": 0,
		"custom_required_opening_balance": required,
		"idx": 0,
	}


class TestNormalizeOpeningBalances(unittest.TestCase):
	def setUp(self):
		self.svc = SessionController.__new__(SessionController)

	def test_all_profile_mops_with_zero_for_non_required(self):
		profile_mops = [_pm("Cash AED", required=1), _pm("Card", required=0)]
		balance = [{"name": "Cash AED", "opening_amount": 500}]
		result = self.svc._normalize_opening_balances(profile_mops, balance)
		self.assertEqual(len(result), 2)
		by_mop = {r["mode_of_payment"]: r["opening_amount"] for r in result}
		self.assertEqual(by_mop["Cash AED"], 500.0)
		self.assertEqual(by_mop["Card"], 0.0)

	def test_extra_client_row_ignored(self):
		profile_mops = [_pm("Cash AED", required=1)]
		balance = [
			{"name": "Cash AED", "opening_amount": 100},
			{"name": "Hacker MOP", "opening_amount": 999},
		]
		result = self.svc._normalize_opening_balances(profile_mops, balance)
		self.assertEqual(result[0]["opening_amount"], 100.0)

	def test_non_required_client_amount_ignored(self):
		profile_mops = [_pm("Cash AED", required=1), _pm("Card", required=0)]
		balance = [
			{"name": "Cash AED", "opening_amount": 100},
			{"name": "Card", "opening_amount": 999},
		]
		result = self.svc._normalize_opening_balances(profile_mops, balance)
		by_mop = {r["mode_of_payment"]: r["opening_amount"] for r in result}
		self.assertEqual(by_mop["Card"], 0.0)

	def test_missing_required_raises(self):
		profile_mops = [_pm("Cash AED", required=1)]
		with self.assertRaises(frappe.ValidationError):
			self.svc._normalize_opening_balances(profile_mops, [])

	def test_no_required_configured_raises(self):
		profile_mops = [_pm("Card", required=0)]
		with self.assertRaises(frappe.ValidationError):
			self.svc._normalize_opening_balances(profile_mops, [{"name": "Card", "opening_amount": 0}])


class TestRequiredMopNames(unittest.TestCase):
	def test_only_flagged_mops(self):
		profile_mops = [_pm("Cash AED", required=1), _pm("Card", required=0)]
		self.assertEqual(
			SessionController._required_mop_names(profile_mops),
			{"Cash AED"},
		)


class TestPrepareClosingReconciliation(unittest.TestCase):
	def setUp(self):
		self.svc = SessionController.__new__(SessionController)

	def _recon_row(self, mop: str, *, expected: float = 100.0):
		return SimpleNamespace(
			mode_of_payment=mop,
			opening_amount=0.0,
			expected_amount=expected,
			closing_amount=0.0,
			difference=0.0,
		)

	def test_required_uses_client_amount_non_required_uses_expected(self):
		profile_mops = [_pm("Cash AED", required=1), _pm("Card", required=0)]
		opening = SimpleNamespace(
			balance_details=[
				SimpleNamespace(mode_of_payment="Cash AED", opening_amount=500),
				SimpleNamespace(mode_of_payment="Card", opening_amount=0),
			]
		)
		cash_row = self._recon_row("Cash AED", expected=50.0)
		card_row = self._recon_row("Card", expected=20.0)
		closing_entry = SimpleNamespace(
			payment_reconciliation=[cash_row, card_row], append=lambda *a, **k: None
		)
		closing_data = [{"name": "Cash AED", "closing_amount": 480}]

		self.svc._prepare_closing_reconciliation(closing_entry, opening, closing_data, profile_mops)
		self.assertEqual(cash_row.closing_amount, 480.0)
		self.assertEqual(card_row.closing_amount, card_row.expected_amount)

	def test_missing_required_closing_raises(self):
		profile_mops = [_pm("Cash AED", required=1)]
		opening = SimpleNamespace(
			balance_details=[SimpleNamespace(mode_of_payment="Cash AED", opening_amount=500)]
		)
		cash_row = self._recon_row("Cash AED")
		closing_entry = SimpleNamespace(payment_reconciliation=[cash_row], append=lambda *a, **k: None)

		with self.assertRaises(frappe.ValidationError):
			self.svc._prepare_closing_reconciliation(closing_entry, opening, [], profile_mops)
