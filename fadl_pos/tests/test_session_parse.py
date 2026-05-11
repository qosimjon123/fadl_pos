# Copyright (c) 2026, FadlTech team and contributors

"""Unit tests for SessionService RPC JSON parsing helpers."""

from __future__ import annotations

import frappe
from frappe.tests import IntegrationTestCase

from fadl_pos.services.session_service import SessionService


class TestSessionParse(IntegrationTestCase):
	def setUp(self):
		super().setUp()
		frappe.set_user("Administrator")

	def test_parse_balance_details_from_json_string(self):
		raw = '[{"mode_of_payment":"Cash","opening_amount":100.5}]'
		rows = SessionService().parse_balance_details_arg(raw)
		self.assertEqual(len(rows), 1)
		self.assertEqual(rows[0]["mode_of_payment"], "Cash")
		self.assertEqual(rows[0]["opening_amount"], 100.5)

	def test_parse_balance_details_from_list(self):
		raw = [{"mode_of_payment": "Cash", "opening_amount": 0}]
		rows = SessionService().parse_balance_details_arg(raw)
		self.assertEqual(len(rows), 1)

	def test_parse_balance_details_empty_string_is_empty_list(self):
		rows = SessionService().parse_balance_details_arg("  ")
		self.assertEqual(rows, [])

	def test_parse_balance_details_invalid_json_raises(self):
		with self.assertRaises(frappe.ValidationError):
			SessionService().parse_balance_details_arg("not-json")

	def test_parse_balance_details_not_array_raises(self):
		with self.assertRaises(frappe.ValidationError):
			SessionService().parse_balance_details_arg('{"mode_of_payment":"Cash"}')

	def test_parse_balance_details_row_not_object_raises(self):
		with self.assertRaises(frappe.ValidationError):
			SessionService().parse_balance_details_arg("[1,2]")

	def test_parse_closing_data_none(self):
		self.assertIsNone(SessionService().parse_closing_data_arg(None))

	def test_parse_closing_data_empty_string(self):
		self.assertIsNone(SessionService().parse_closing_data_arg(""))

	def test_parse_closing_data_valid(self):
		raw = [{"mode_of_payment": "Cash", "closing_amount": 10}]
		rows = SessionService().parse_closing_data_arg(raw)
		self.assertEqual(len(rows), 1)
		self.assertEqual(rows[0]["closing_amount"], 10.0)
