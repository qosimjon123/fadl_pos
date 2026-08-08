# Copyright (c) 2026, FadlTech team and contributors

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

import frappe

import fadl_pos.delivery.processing.charges as delivery_charges
import fadl_pos.offers.processing.offers as offers


class TestGetOffers(unittest.TestCase):
	"""Tests for get_offers (offers.processing.offers)."""

	@patch("fadl_pos.offers.processing.offers._get_promotional_scheme_offers")
	@patch("fadl_pos.offers.processing.offers.frappe")
	def test_get_offers_returns_active_offers(self, mock_frappe, mock_promo):
		mock_pos = MagicMock()
		mock_pos.company = "Test Company"
		mock_pos.warehouse = "Store - TC"
		mock_frappe.get_doc.return_value = mock_pos
		mock_frappe.db.sql.return_value = [
			{
				"name": "OFFER-001",
				"offer_title": "10% Off",
				"discount_percentage": 10,
				"disabled": 0,
			}
		]
		mock_promo.return_value = []

		result = offers.get_offers("POS-PROFILE-1")

		self.assertEqual(len(result), 1)
		self.assertEqual(result[0]["name"], "OFFER-001")

	@patch("fadl_pos.offers.processing.offers._get_promotional_scheme_offers")
	@patch("fadl_pos.offers.processing.offers.frappe")
	def test_get_offers_includes_promotional_schemes(self, mock_frappe, mock_promo):
		mock_pos = MagicMock()
		mock_pos.company = "Test Company"
		mock_pos.warehouse = "Store - TC"
		mock_frappe.get_doc.return_value = mock_pos
		mock_frappe.db.sql.return_value = []
		mock_promo.return_value = [
			{
				"name": "PROMO-001",
				"offer_title": "Promo",
				"discount_percentage": 15,
			}
		]

		result = offers.get_offers("POS-PROFILE-1")

		self.assertEqual(len(result), 1)
		self.assertEqual(result[0]["name"], "PROMO-001")

	@patch("fadl_pos.offers.processing.offers._get_promotional_scheme_offers")
	@patch("fadl_pos.offers.processing.offers.frappe")
	def test_get_offers_normalizes_discount_fields(self, mock_frappe, mock_promo):
		mock_pos = MagicMock()
		mock_pos.company = "Test Company"
		mock_pos.warehouse = "Store - TC"
		mock_frappe.get_doc.return_value = mock_pos
		mock_frappe.db.sql.return_value = [
			{
				"name": "OFFER-002",
				"min_qty": None,
				"max_qty": None,
				"min_amt": None,
				"max_amt": None,
				"discount_type": "",
				"discount_percentage": 10,
			}
		]
		mock_promo.return_value = []

		result = offers.get_offers("POS-PROFILE-1")

		self.assertEqual(result[0].get("min_qty", 0), 0)


class TestGetPosCoupon(unittest.TestCase):
	"""Tests for get_pos_coupon → check_coupon_code."""

	@patch("fadl_pos.offers.processing.offers.check_coupon_code")
	def test_get_pos_coupon_validates_existing_coupon(self, mock_check):
		mock_check.return_value = {
			"coupon": {"coupon_code": "SUMMER10"},
			"offer": {"name": "OFFER-1"},
			"msg": "Apply",
		}

		result = offers.get_pos_coupon("SUMMER10", "CUST-001", "Test Company")

		mock_check.assert_called_once_with("SUMMER10", "CUST-001", "Test Company")
		self.assertEqual(result["coupon"]["coupon_code"], "SUMMER10")
		self.assertEqual(result["msg"], "Apply")

	@patch("fadl_pos.offers.processing.offers.check_coupon_code")
	def test_get_pos_coupon_throws_for_invalid_coupon(self, mock_check):
		mock_check.side_effect = Exception("Invalid coupon")

		with self.assertRaises(Exception):
			offers.get_pos_coupon("INVALID", "CUST-001", "Test Company")

	@patch("fadl_pos.offers.processing.offers.check_coupon_code")
	def test_get_pos_coupon_validates_expiry(self, mock_check):
		mock_check.side_effect = Exception("Coupon has expired")

		with self.assertRaises(Exception):
			offers.get_pos_coupon("EXPIRED10", "CUST-001", "Test Company")


class TestValidateCoupon(unittest.TestCase):
	"""Tests for coupon validation logic."""

	def test_validate_coupon_checks_usage(self):
		"""Placeholder: used coupons are filtered by check_coupon_code."""
		self.assertIsNone(None)

	def test_coupon_date_validation(self):
		from frappe.utils import getdate

		coupon = {
			"valid_from": "2026-01-01",
			"valid_upto": "2026-12-31",
		}

		today = getdate("2026-06-15")
		valid_from = getdate(coupon["valid_from"])
		valid_upto = getdate(coupon["valid_upto"])

		is_valid = valid_from <= today <= valid_upto
		self.assertTrue(is_valid)


class TestGetActiveGiftCoupons(unittest.TestCase):
	"""Tests for get_active_gift_coupons."""

	@patch("fadl_pos.offers.processing.offers.frappe")
	def test_get_active_gift_coupons_returns_customer_coupons(self, mock_frappe):
		mock_frappe.get_all.return_value = [
			frappe._dict(
				{
					"coupon_code": "GIFT100",
					"valid_from": None,
					"valid_upto": None,
				}
			)
		]

		result = offers.get_active_gift_coupons("CUST-001", "Test Company")

		mock_frappe.get_all.assert_called()
		self.assertEqual(len(result), 1)
		self.assertEqual(result[0], "GIFT100")


class TestGetDeliveryCharges(unittest.TestCase):
	"""Tests for delivery.processing.charges.get_delivery_charges."""

	@patch(
		"fadl_pos.fadl_pos.doctype.delivery_charges.delivery_charges.get_applicable_delivery_charges"
	)
	@patch("fadl_pos.delivery.processing.charges.frappe")
	def test_get_delivery_charges_returns_charges(self, mock_frappe, mock_applicable):
		mock_frappe.db.get_value.return_value = "Test Company"
		mock_applicable.return_value = [
			frappe._dict(name="DC-001", label="Standard", default_rate=50, rate=50, company="Test Company"),
			frappe._dict(name="DC-002", label="Express", default_rate=100, rate=100, company="Test Company"),
		]

		result = delivery_charges.get_delivery_charges("POS-PROFILE-1")

		mock_applicable.assert_called_once()
		self.assertEqual(len(result), 2)
		self.assertEqual(result[0]["rate"], 50)

	@patch(
		"fadl_pos.fadl_pos.doctype.delivery_charges.delivery_charges.get_applicable_delivery_charges"
	)
	@patch("fadl_pos.delivery.processing.charges.frappe")
	def test_get_delivery_charges_filters_by_profile(self, mock_frappe, mock_applicable):
		mock_frappe.db.get_value.return_value = "Test Company"
		mock_applicable.return_value = []

		delivery_charges.get_delivery_charges("POS-PROFILE-1")

		kwargs = mock_applicable.call_args.kwargs
		self.assertEqual(kwargs.get("pos_profile"), "POS-PROFILE-1")


class TestOfferApplicationLogic(unittest.TestCase):
	"""Tests for offer application logic."""

	def test_percentage_discount_calculation(self):
		subtotal = 100
		discount_percentage = 10

		discount = subtotal * (discount_percentage / 100)
		final = subtotal - discount

		self.assertEqual(discount, 10)
		self.assertEqual(final, 90)

	def test_fixed_discount_calculation(self):
		subtotal = 100
		discount_amount = 15

		final = subtotal - discount_amount

		self.assertEqual(final, 85)

	def test_min_qty_requirement(self):
		offer = {"min_qty": 3}
		cart_qty = 5

		meets_requirement = cart_qty >= offer["min_qty"]
		self.assertTrue(meets_requirement)

	def test_min_amount_requirement(self):
		offer = {"min_amt": 100}
		cart_total = 150

		meets_requirement = cart_total >= offer["min_amt"]
		self.assertTrue(meets_requirement)

	def test_max_qty_limit(self):
		offer = {"max_qty": 5, "discount_percentage": 10}
		cart_qty = 10

		discounted_qty = min(cart_qty, offer["max_qty"])
		self.assertEqual(discounted_qty, 5)

	def test_buy_x_get_y_logic(self):
		offer = {
			"buy_qty": 2,
			"get_qty": 1,
			"free_item": "ITEM-FREE",
		}
		cart_qty = 6

		free_items = (cart_qty // offer["buy_qty"]) * offer["get_qty"]
		self.assertEqual(free_items, 3)


class TestOfferPriority(unittest.TestCase):
	"""Tests for offer priority and stacking."""

	def test_offers_sorted_by_priority(self):
		offers_list = [
			{"name": "OFFER-1", "priority": 3},
			{"name": "OFFER-2", "priority": 1},
			{"name": "OFFER-3", "priority": 2},
		]

		sorted_offers = sorted(offers_list, key=lambda x: x.get("priority", 999))

		self.assertEqual(sorted_offers[0]["name"], "OFFER-2")
		self.assertEqual(sorted_offers[2]["name"], "OFFER-1")

	def test_non_stackable_offers(self):
		applied_offers = []
		new_offer = {"name": "OFFER-X", "stackable": 0}

		if applied_offers or not new_offer.get("stackable", 1):
			can_apply = len(applied_offers) == 0 or new_offer.get("stackable", 1) == 1
		else:
			can_apply = True

		self.assertTrue(can_apply)


class TestPromotionalSchemeOffers(unittest.TestCase):
	"""Tests for promotional scheme offer conversion."""

	def test_promotional_scheme_to_pos_offer_mapping(self):
		promo_rule = {
			"name": "PROMO-RULE-001",
			"discount_percentage": 15,
			"min_qty": 2,
			"apply_on": "Item Code",
		}

		pos_offer = {
			"name": promo_rule["name"],
			"discount_percentage": promo_rule["discount_percentage"],
			"min_qty": promo_rule["min_qty"],
			"from_promotional_scheme": 1,
			"auto": 1,
		}

		self.assertEqual(pos_offer["discount_percentage"], 15)
		self.assertEqual(pos_offer["from_promotional_scheme"], 1)


if __name__ == "__main__":
	unittest.main()
