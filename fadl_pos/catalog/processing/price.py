# Copyright (c) 2026, FadlTech team and contributors

from __future__ import annotations

import frappe
from frappe.utils import flt


def update_price_list_rate(item_code: str, price_list: str, rate: float, uom: str | None = None):
	"""Create or update an Item Price record."""
	filters = {"item_code": item_code, "price_list": price_list, "selling": 1}
	if uom:
		filters["uom"] = uom

	existing = frappe.db.get_value("Item Price", filters, "name")
	if existing:
		frappe.db.set_value("Item Price", existing, "price_list_rate", flt(rate))
	else:
		doc = frappe.get_doc(
			{
				"doctype": "Item Price",
				"item_code": item_code,
				"price_list": price_list,
				"selling": 1,
				"price_list_rate": flt(rate),
				"uom": uom,
			}
		)
		doc.insert(ignore_permissions=True)

	return {"success": True, "rate": flt(rate)}

def get_price_for_uom(
	item_code: str, uom: str, pos_profile: str | None = None, price_list: str | None = None
):
	"""Return Item Price for a specific UOM, falling back to base rate × conversion factor."""
	if not price_list and pos_profile:
		price_list = frappe.db.get_value("POS Profile", pos_profile, "selling_price_list")
	if not price_list:
		price_list = frappe.db.get_single_value("Selling Settings", "selling_price_list")

	rate = frappe.db.get_value(
		"Item Price",
		{"item_code": item_code, "price_list": price_list, "selling": 1, "uom": uom},
		"price_list_rate",
	)
	if rate:
		return {"rate": flt(rate)}

	base_rate = frappe.db.get_value(
		"Item Price",
		{"item_code": item_code, "price_list": price_list, "selling": 1},
		"price_list_rate",
	)
	conversion_factor = (
		frappe.db.get_value(
			"UOM Conversion Detail",
			{"parent": item_code, "uom": uom},
			"conversion_factor",
		)
		or 1.0
	)
	return {"rate": flt(base_rate) * flt(conversion_factor)}

