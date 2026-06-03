# Copyright (c) 2026, FadlTech team and contributors

"""Unit tests for Frappe RPC boundary helpers."""

from __future__ import annotations

import unittest

from fadl_pos.api.rpc_boundary import validate_in
from fadl_pos.schemas import CouponValidateIn, PaymentUpdateIn


class TestValidateIn(unittest.TestCase):
	def test_payment_update_in(self):
		body = validate_in(
			PaymentUpdateIn,
			{
				"invoice_name": "POS-INV-1",
				"payments": [{"mode_of_payment": "Cash", "amount": 100}],
			},
		)
		self.assertEqual(body.invoice_name, "POS-INV-1")

	def test_coupon_validate_in(self):
		body = validate_in(CouponValidateIn, {"coupon_code": "SAVE10"})
		self.assertEqual(body.coupon_code, "SAVE10")
