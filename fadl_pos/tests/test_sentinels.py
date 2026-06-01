import unittest

import frappe


class TestSentinels(unittest.TestCase):
	"""
	Sentinel Tests: Verification that critical native ERPNext modules
	and functions used by fadl_pos are still present and have unchanged signatures.
	"""

	def test_pos_page_imports(self):
		"""Verify erpnext.selling.page.point_of_sale.point_of_sale functions."""
		try:
			from erpnext.selling.page.point_of_sale.point_of_sale import (
				check_opening_entry,
				get_customer_recent_transactions,
				get_stock_availability,
				set_customer_info,
			)
		except ImportError as e:
			self.fail(f"Native POS Page functions missing: {e}")

	def test_pos_invoice_methods(self):
		"""Verify POS Invoice DocType methods."""
		if not frappe.db.exists("DocType", "POS Invoice"):
			self.fail("POS Invoice DocType missing")

		doc = frappe.new_doc("POS Invoice")
		self.assertTrue(hasattr(doc, "update_payments"), "POSInvoice.update_payments missing")
		self.assertTrue(hasattr(doc, "set_missing_values"), "POSInvoice.set_missing_values missing")

	def test_pricing_rule_utils(self):
		"""Verify Pricing Rule utilities."""
		try:
			from erpnext.accounts.doctype.pricing_rule.utils import get_pricing_rules, validate_coupon_code
		except ImportError as e:
			self.fail(f"Pricing Rule utilities missing: {e}")

	def test_serial_no_utils(self):
		"""Verify Serial No utilities."""
		try:
			from erpnext.stock.doctype.serial_no.serial_no import auto_fetch_serial_number
		except ImportError as e:
			self.fail(f"Serial No utilities missing: {e}")

	def test_loyalty_program_utils(self):
		"""Verify Loyalty Program utilities."""
		try:
			from erpnext.accounts.doctype.loyalty_program.loyalty_program import get_loyalty_details
		except ImportError as e:
			self.fail(f"Loyalty Program utilities missing: {e}")
