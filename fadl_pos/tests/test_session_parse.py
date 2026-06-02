# Copyright (c) 2026, FadlTech team and contributors

"""Unit tests for session RPC JSON parsing (TypeAdapter + Frappe RPC coercion)."""

from __future__ import annotations

import frappe
from frappe.tests import IntegrationTestCase
from pydantic import TypeAdapter, ValidationError

from fadl_pos.schemas import BalanceDetailItem, ClosingReconciliationItem


def _parse_list(raw: object, adapter: TypeAdapter):
	if raw is None or (isinstance(raw, str) and not raw.strip()):
		return None
	if isinstance(raw, str):
		return adapter.validate_json(raw)
	return adapter.validate_python(raw)


class TestSessionParse(IntegrationTestCase):
	def setUp(self):
		super().setUp()
		frappe.set_user("Administrator")

	def test_parse_balance_details_from_json_string(self):
		raw = '[{"mode_of_payment":"Cash","opening_amount":100.5}]'
		rows = _parse_list(raw, TypeAdapter(list[BalanceDetailItem])) or []
		self.assertEqual(len(rows), 1)
		self.assertEqual(rows[0].mode_of_payment, "Cash")
		self.assertEqual(rows[0].opening_amount, 100.5)

	def test_parse_balance_details_from_list(self):
		raw = [{"mode_of_payment": "Cash", "opening_amount": 0}]
		rows = _parse_list(raw, TypeAdapter(list[BalanceDetailItem])) or []
		self.assertEqual(len(rows), 1)

	def test_parse_balance_details_empty_string_is_empty_list(self):
		rows = _parse_list("  ", TypeAdapter(list[BalanceDetailItem])) or []
		self.assertEqual(rows, [])

	def test_parse_balance_details_invalid_json_raises(self):
		with self.assertRaises(ValidationError):
			_parse_list("not-json", TypeAdapter(list[BalanceDetailItem]))

	def test_parse_balance_details_not_array_raises(self):
		with self.assertRaises(ValidationError):
			_parse_list('{"mode_of_payment":"Cash"}', TypeAdapter(list[BalanceDetailItem]))

	def test_parse_balance_details_row_not_object_raises(self):
		with self.assertRaises(ValidationError):
			_parse_list("[1,2]", TypeAdapter(list[BalanceDetailItem]))

	def test_parse_closing_data_none(self):
		self.assertIsNone(_parse_list(None, TypeAdapter(list[ClosingReconciliationItem])))

	def test_parse_closing_data_empty_string(self):
		self.assertIsNone(_parse_list("", TypeAdapter(list[ClosingReconciliationItem])))

	def test_parse_closing_data_valid(self):
		raw = [{"mode_of_payment": "Cash", "closing_amount": 10}]
		rows = _parse_list(raw, TypeAdapter(list[ClosingReconciliationItem]))
		self.assertEqual(len(rows), 1)
		self.assertEqual(rows[0].closing_amount, 10.0)
