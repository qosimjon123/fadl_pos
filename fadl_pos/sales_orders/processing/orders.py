# Copyright (c) 2026, FadlTech team and contributors

"""Sales Order search, create/update, submit, and invoice-from-order."""

from __future__ import annotations

import json

import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate


def search_orders(company: str, currency: str | None = None, order_name: str | None = None):
	"""Searches for unbilled Sales Orders."""
	filters = {
		"company": company,
		"docstatus": 1,
		"status": ["not in", ["Closed", "Completed"]],
		"per_billed": ["<", 100],
	}

	if currency:
		filters["currency"] = currency
	if order_name:
		filters["name"] = ["like", f"%{order_name}%"]

	orders = frappe.get_list(
		"Sales Order",
		filters=filters,
		fields=[
			"name",
			"customer",
			"customer_name",
			"transaction_date",
			"grand_total",
			"currency",
			"status",
			"per_billed",
			"per_delivered",
			"delivery_date",
		],
		limit_page_length=50,
		order_by="transaction_date desc",
	)

	return orders


def _map_delivery_dates(data: dict):
	"""Ensure mandatory delivery_date fields are populated."""

	def parse_date(value):
		if not value:
			return None
		if isinstance(value, str):
			normalized = value.strip()
			if not normalized:
				return None
			if normalized.lower() in {"invalid date", "nan", "none", "null", "undefined"}:
				return None
			value = normalized
		try:
			return str(getdate(value))
		except Exception:
			return None

	# Map order level delivery date with robust fallback.
	order_delivery_date = (
		parse_date(data.get("delivery_date"))
		or parse_date(data.get("pos_delivery_date"))
		or parse_date(data.get("transaction_date"))
		or parse_date(data.get("posting_date"))
		or str(getdate(nowdate()))
	)
	data["delivery_date"] = order_delivery_date

	# Map item level delivery dates
	for item in data.get("items", []):
		if not isinstance(item, dict):
			continue

		item_delivery = (
			parse_date(item.get("delivery_date"))
			or parse_date(item.get("pos_delivery_date"))
			or order_delivery_date
		)
		if item_delivery:
			item["delivery_date"] = item_delivery
			item.setdefault("delivery_date", item_delivery)


def create_sales_order(data: str | dict):
	"""Creates or updates a Sales Order from POS."""
	if isinstance(data, str):
		data = json.loads(data)

	pos_profile = data.get("pos_profile")
	customer = data.get("customer")
	items = data.get("items", [])
	delivery_date = data.get("delivery_date")

	if not pos_profile or not customer or not items:
		frappe.throw(_("POS Profile, Customer, and Items are required"))

	pos = frappe.get_cached_doc("POS Profile", pos_profile)

	so_name = data.get("name")
	if so_name and frappe.db.exists("Sales Order", so_name):
		so = frappe.get_doc("Sales Order", so_name)
		if so.docstatus != 0:
			frappe.throw(_("Only draft Sales Orders can be updated"))
		so.set("items", [])
	else:
		so = frappe.new_doc("Sales Order")

	so.customer = customer
	so.company = pos.company
	so.transaction_date = nowdate()
	so.delivery_date = delivery_date or nowdate()
	so.currency = data.get("currency") or pos.currency
	so.selling_price_list = data.get("selling_price_list") or pos.selling_price_list

	for item_data in items:
		item = so.append("items", {})
		item.item_code = item_data.get("item_code")
		item.item_name = item_data.get("item_name")
		item.qty = flt(item_data.get("qty", 1))
		item.rate = flt(item_data.get("rate", 0))
		item.uom = item_data.get("uom") or item_data.get("stock_uom")
		item.warehouse = item_data.get("warehouse") or pos.warehouse
		item.delivery_date = item_data.get("delivery_date") or delivery_date or nowdate()

		if item_data.get("discount_percentage"):
			item.discount_percentage = flt(item_data["discount_percentage"])
		if item_data.get("discount_amount"):
			item.discount_amount = flt(item_data["discount_amount"])

	if data.get("additional_discount_percentage"):
		so.additional_discount_percentage = flt(data["additional_discount_percentage"])
		so.apply_discount_on = data.get("apply_discount_on") or "Grand Total"
	if data.get("discount_amount"):
		so.discount_amount = flt(data["discount_amount"])
		so.apply_discount_on = data.get("apply_discount_on") or "Grand Total"

	so.save(ignore_permissions=True)

	return {
		"name": so.name,
		"grand_total": so.grand_total,
		"customer": so.customer,
		"customer_name": so.customer_name,
		"status": "Draft",
	}


def update_sales_order(data: str | dict):
	"""Create or update a Sales Order document."""
	if isinstance(data, str):
		data = json.loads(data)
	_map_delivery_dates(data)
	if data.get("name") and frappe.db.exists("Sales Order", data.get("name")):
		so_doc = frappe.get_doc("Sales Order", data.get("name"))
		so_doc.update(data)
	else:
		so_doc = frappe.get_doc(data)

	so_doc.flags.ignore_permissions = True
	frappe.flags.ignore_account_permission = True
	so_doc.docstatus = 0
	so_doc.save()
	return so_doc


def submit_sales_order(order: str | dict):
	"""Submit sales order and create payment entries."""
	if isinstance(order, str):
		order = json.loads(order)
	_map_delivery_dates(order)
	if order.get("name") and frappe.db.exists("Sales Order", order.get("name")):
		so_doc = frappe.get_doc("Sales Order", order.get("name"))
		so_doc.update(order)
	else:
		so_doc = frappe.get_doc(order)

	payments = order.get("payments")

	so_doc.flags.ignore_permissions = True
	frappe.flags.ignore_account_permission = True
	so_doc.save()
	so_doc.submit()

	if payments:
		frappe.enqueue(
			"fadl_pos.sales_orders.processing.payments._payment_entry_job",
			queue="short",
			order_name=so_doc.name,
			payments=payments,
		)

	# Payment entries run in the background to speed up checkout

	return {"name": so_doc.name, "status": so_doc.docstatus}


def create_sales_invoice_from_order(sales_order: str):
	"""Creates a Sales Invoice from a Sales Order."""
	from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice

	si = make_sales_invoice(sales_order)
	si.is_pos = 1
	si.insert(ignore_permissions=True)

	return {
		"name": si.name,
		"grand_total": si.grand_total,
		"customer": si.customer,
	}
