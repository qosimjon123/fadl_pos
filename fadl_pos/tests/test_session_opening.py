# Copyright (c) 2026, FadlTech team and contributors

"""Unit tests for session opening/closing balance normalization."""

from __future__ import annotations

import unittest
from types import SimpleNamespace

import frappe
from frappe.tests import IntegrationTestCase

from fadl_pos.schemas import BalanceDetailItem, ClosingReconciliationItem, InternalPaymentMethod
from fadl_pos.services.session_service import SessionService


def _pm(
	name: str,
	*,
	required: int = 0,
	pos_profile: str = "POS-1",
) -> InternalPaymentMethod:
	return InternalPaymentMethod.model_validate(
		{
			"pos_profile": pos_profile,
			"mode_of_payment": name,
			"default": 0,
			"custom_required_opening_balance": required,
			"idx": 0,
		}
	)


class TestNormalizeOpeningBalances(unittest.TestCase):
	def setUp(self):
		self.svc = SessionService.__new__(SessionService)

	def test_all_profile_mops_with_zero_for_non_required(self):
		profile_mops = [_pm("Cash AED", required=1), _pm("Card", required=0)]
		balance = [BalanceDetailItem(name="Cash AED", opening_amount=500)]
		result = self.svc._normalize_opening_balances(profile_mops, balance)
		self.assertEqual(len(result), 2)
		by_mop = {r["mode_of_payment"]: r["opening_amount"] for r in result}
		self.assertEqual(by_mop["Cash AED"], 500.0)
		self.assertEqual(by_mop["Card"], 0.0)

	def test_extra_client_row_ignored(self):
		profile_mops = [_pm("Cash AED", required=1)]
		balance = [
			BalanceDetailItem(name="Cash AED", opening_amount=100),
			BalanceDetailItem(name="Hacker MOP", opening_amount=999),
		]
		result = self.svc._normalize_opening_balances(profile_mops, balance)
		self.assertEqual(result[0]["opening_amount"], 100.0)

	def test_non_required_client_amount_ignored(self):
		profile_mops = [_pm("Cash AED", required=1), _pm("Card", required=0)]
		balance = [
			BalanceDetailItem(name="Cash AED", opening_amount=100),
			BalanceDetailItem(name="Card", opening_amount=999),
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
			self.svc._normalize_opening_balances(
				profile_mops, [BalanceDetailItem(name="Card", opening_amount=0)]
			)


class TestClosingActualMap(unittest.TestCase):
	def setUp(self):
		self.svc = SessionService.__new__(SessionService)

	def test_only_required_names_in_map(self):
		profile_mops = [_pm("Cash AED", required=1), _pm("Card", required=0)]
		closing = [
			ClosingReconciliationItem(name="Cash AED", closing_amount=480),
			ClosingReconciliationItem(name="Ignored", closing_amount=1),
		]
		actual = self.svc._build_closing_actual_map(profile_mops, closing)
		self.assertEqual(actual, {"Cash AED": 480.0})


class TestPrepareClosingReconciliation(unittest.TestCase):
	def setUp(self):
		self.svc = SessionService.__new__(SessionService)

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
		closing_entry = SimpleNamespace(payment_reconciliation=[cash_row, card_row], append=lambda *a, **k: None)
		closing_data = [ClosingReconciliationItem(name="Cash AED", closing_amount=480)]

		self.svc._prepare_closing_reconciliation(
			closing_entry, opening, closing_data, profile_mops
		)
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


class TestPaymentMethodsForClient(IntegrationTestCase):
	def test_requires_opening_balance_helper(self):
		self.assertTrue(SessionService._requires_opening_balance(_pm("Cash", required=1)))
		self.assertFalse(SessionService._requires_opening_balance(_pm("Card", required=0)))
