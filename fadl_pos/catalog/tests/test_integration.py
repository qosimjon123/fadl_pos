# Copyright (c) 2026, FadlTech team and contributors

"""Integration tests for catalog item search (numeric item codes)."""

from __future__ import annotations

import json
from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from fadl_pos.catalog.processing.search import get_items


class TestNumericItemCodes(FrappeTestCase):
	def setUp(self):
		leaf_group = frappe.db.get_value("Item Group", {"is_group": 0}, "name") or "All Item Groups"
		items = [
			("ALPHA-TEST", "Alpha"),
			("BETA-TEST", "Beta"),
			("002", "Gamma"),
		]
		for code, name in items:
			if frappe.db.exists("Item", code):
				item = frappe.get_doc("Item", code)
				item.item_name = name
				item.item_group = leaf_group
				item.is_sales_item = 1
				item.is_fixed_asset = 0
				item.save(ignore_permissions=True)
			else:
				frappe.get_doc(
					{
						"doctype": "Item",
						"item_code": code,
						"item_name": name,
						"stock_uom": "Nos",
						"is_stock_item": 0,
						"item_group": leaf_group,
						"is_sales_item": 1,
						"is_fixed_asset": 0,
					}
				).insert(ignore_permissions=True, ignore_mandatory=True)

	def test_numeric_code_appears_without_search(self):
		pos_profile = json.dumps({"name": "TestProfile"})
		item_groups = json.dumps(["All Item Groups"])
		with patch(
			"fadl_pos.catalog.processing.search.get_items_details",
			return_value=[],
		):
			# search.get_items may call details through other paths; patch aggregator build
			with patch(
				"fadl_pos.catalog.processing.details.get_items_details",
				return_value=[],
			):
				seen_target = False
				start_after = None
				for _ in range(300):
					page = get_items(
						pos_profile,
						limit=100,
						start_after=start_after,
						item_groups=item_groups,
					)
					if not page:
						break
					codes = [row.get("item_code") for row in page]
					if "002" in codes:
						seen_target = True
						break
					start_after = page[-1].get("item_code")
				self.assertTrue(seen_target, "Numeric item code 002 should appear in pagination")
