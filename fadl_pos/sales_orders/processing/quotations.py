# Copyright (c) 2026, FadlTech team and contributors

"""Quotation create/update/submit for POS."""

from __future__ import annotations

import json

import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate


def _map_delivery_dates(data: dict):
	"""Ensure mandatory delivery_date fields are populated."""

	def parse_date(value):
		if not value:
			return None
		try:
			return str(getdate(value))
		except Exception:
			return None

	if not data.get("delivery_date") and data.get("pos_delivery_date"):
		parsed = parse_date(data.get("pos_delivery_date"))
		if parsed:
			data["delivery_date"] = parsed

	for item in data.get("items", []):
		if not item.get("delivery_date"):
			delivery = item.get("delivery_date") or item.get("pos_delivery_date") or data.get("delivery_date")
			parsed = parse_date(delivery)
			if parsed:
				item["delivery_date"] = parsed


def _ensure_customer_fields(data):
	if not isinstance(data, dict):
		return

	if data.get("doctype") != "Quotation":
		return

	customer = data.get("customer") or data.get("party_name")
	if customer:
		data["customer"] = customer
		data["party_name"] = customer
		data.setdefault("customer_name", customer)

	data.setdefault("quotation_to", "Customer")


def create_quotation(data: str | dict):
	"""Creates or updates a Quotation from POS."""
	if isinstance(data, str):
		data = json.loads(data)

	pos_profile = data.get("pos_profile")
	customer = data.get("customer")
	items = data.get("items", [])

	if not pos_profile or not customer or not items:
		frappe.throw(_("POS Profile, Customer, and Items are required"))

	pos = frappe.get_cached_doc("POS Profile", pos_profile)

	qt_name = data.get("name")
	if qt_name and frappe.db.exists("Quotation", qt_name):
		qt = frappe.get_doc("Quotation", qt_name)
		if qt.docstatus != 0:
			frappe.throw(_("Only draft Quotations can be updated"))
		qt.set("items", [])
	else:
		qt = frappe.new_doc("Quotation")

	qt.quotation_to = "Customer"
	qt.party_name = customer
	qt.company = pos.company
	qt.transaction_date = nowdate()
	qt.currency = data.get("currency") or pos.currency
	qt.selling_price_list = data.get("selling_price_list") or pos.selling_price_list

	for item_data in items:
		item = qt.append("items", {})
		item.item_code = item_data.get("item_code")
		item.item_name = item_data.get("item_name")
		item.qty = flt(item_data.get("qty", 1))
		item.rate = flt(item_data.get("rate", 0))
		item.uom = item_data.get("uom") or item_data.get("stock_uom")

	if data.get("additional_discount_percentage"):
		qt.additional_discount_percentage = flt(data["additional_discount_percentage"])
		qt.apply_discount_on = data.get("apply_discount_on") or "Grand Total"

	qt.save(ignore_permissions=True)

	return {
		"name": qt.name,
		"grand_total": qt.grand_total,
		"customer": qt.party_name,
		"status": "Draft",
	}


def update_quotation(data: str | dict):
	"""Create or update a Quotation document."""
	if isinstance(data, str):
		data = json.loads(data)
	_map_delivery_dates(data)
	_ensure_customer_fields(data)
	if data.get("name") and frappe.db.exists("Quotation", data.get("name")):
		doc = frappe.get_doc("Quotation", data.get("name"))
		doc.update(data)
	else:
		doc = frappe.get_doc(data)

	doc.flags.ignore_permissions = True
	frappe.flags.ignore_account_permission = True
	doc.docstatus = 0
	doc.save()
	return doc


def submit_quotation(order: str | dict):
	"""Submit quotation document."""
	if isinstance(order, str):
		order = json.loads(order)
	_map_delivery_dates(order)
	_ensure_customer_fields(order)
	if order.get("name") and frappe.db.exists("Quotation", order.get("name")):
		doc = frappe.get_doc("Quotation", order.get("name"))
		doc.update(order)
	else:
		doc = frappe.get_doc(order)

	doc.flags.ignore_permissions = True
	frappe.flags.ignore_account_permission = True
	doc.save()
	doc.submit()

	return {"name": doc.name, "status": doc.docstatus}
