# Copyright (c) 2026, FadlTech team and contributors

"""Unit tests for session RPC JSON parsing via validate_in + OpenShiftIn/CloseShiftIn."""

from __future__ import annotations

import frappe
from frappe.tests import IntegrationTestCase

from fadl_pos.core.serializer import validate_in
from fadl_pos.session.serializer import CloseShiftIn, OpenShiftIn


class TestSessionParse(IntegrationTestCase):
	def setUp(self):
		super().setUp()
		frappe.set_user("Administrator")

	def test_parse_balance_details_from_json_string(self):
		raw = '[{"name":"Cash","opening_amount":100.5}]'
		body = validate_in(
			OpenShiftIn,
			{
				"pos_profile": "Test POS",
				"company": "Test Co",
				"balance_details": raw,
			},
		)
		self.assertEqual(len(body.balance_details), 1)
		self.assertEqual(body.balance_details[0].name, "Cash")
		self.assertEqual(body.balance_details[0].opening_amount, 100.5)

	def test_parse_balance_details_from_list(self):
		raw = [{"name": "Cash", "opening_amount": 0}]
		body = validate_in(
			OpenShiftIn,
			{
				"pos_profile": "Test POS",
				"company": "Test Co",
				"balance_details": raw,
			},
		)
		self.assertEqual(len(body.balance_details), 1)

	def test_parse_balance_details_empty_string_is_empty_list(self):
		body = validate_in(
			OpenShiftIn,
			{
				"pos_profile": "Test POS",
				"company": "Test Co",
				"balance_details": "  ",
			},
		)
		self.assertEqual(body.balance_details, [])

	def test_parse_balance_details_invalid_json_raises(self):
		with self.assertRaises(frappe.ValidationError):
			validate_in(
				OpenShiftIn,
				{
					"pos_profile": "Test POS",
					"company": "Test Co",
					"balance_details": "not-json",
				},
			)

	def test_parse_balance_details_not_array_raises(self):
		with self.assertRaises(frappe.ValidationError):
			validate_in(
				OpenShiftIn,
				{
					"pos_profile": "Test POS",
					"company": "Test Co",
					"balance_details": '{"name":"Cash"}',
				},
			)

	def test_parse_balance_details_row_not_object_raises(self):
		with self.assertRaises(frappe.ValidationError):
			validate_in(
				OpenShiftIn,
				{
					"pos_profile": "Test POS",
					"company": "Test Co",
					"balance_details": "[1,2]",
				},
			)

	def test_parse_closing_data_none(self):
		body = validate_in(
			CloseShiftIn,
			{"opening_entry_name": "POS-OPE-1", "closing_data": None},
		)
		self.assertIsNone(body.closing_data)

	def test_parse_closing_data_empty_string(self):
		body = validate_in(
			CloseShiftIn,
			{"opening_entry_name": "POS-OPE-1", "closing_data": ""},
		)
		self.assertIsNone(body.closing_data)

	def test_parse_closing_data_valid(self):
		raw = [{"name": "Cash", "closing_amount": 10}]
		body = validate_in(
			CloseShiftIn,
			{"opening_entry_name": "POS-OPE-1", "closing_data": raw},
		)
		self.assertEqual(len(body.closing_data), 1)
		self.assertEqual(body.closing_data[0].closing_amount, 10.0)
