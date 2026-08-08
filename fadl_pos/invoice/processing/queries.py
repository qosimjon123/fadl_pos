# Copyright (c) 2026, FadlTech team and contributors

"""Invoice list / get / search queries."""

from __future__ import annotations

import json

import frappe
from frappe import _
from frappe.utils import cint, flt, getdate, nowdate

from fadl_pos.utilities import get_invoice_type, is_pos_cashier


def _detect_invoice_doctype(invoice_name: str):
	"""Detect whether an invoice name belongs to Sales Invoice or POS Invoice."""
	if frappe.db.exists("Sales Invoice", invoice_name):
		return "Sales Invoice"
	if frappe.db.exists("POS Invoice", invoice_name):
		return "POS Invoice"
	frappe.throw(_("Invoice {0} not found").format(invoice_name))


def get_draft_invoices(pos_opening_entry: str):
	"""Get draft invoices for the current shift."""
	filters = {"docstatus": 0, "is_pos": 1}

	if pos_opening_entry:
		filters["pos_opening_entry"] = pos_opening_entry

	doctype = get_invoice_type()

	invoices = frappe.get_list(
		doctype,
		filters=filters,
		fields=[
			"name",
			"customer",
			"customer_name",
			"posting_date",
			"grand_total",
			"total_qty",
			"currency",
			"creation",
			"modified",
		],
		limit_page_length=50,
		order_by="modified desc",
	)

	return invoices


def get_unsettled_invoices(pos_profile: str | None = None):
	"""Get draft invoices awaiting cashier settlement for a POS profile.

	These are unsubmitted invoices created by a terminal in cashier-settlement
	mode (``pos_awaiting_settlement = 1``). They are listed on the Cashier screen
	regardless of which terminal, operator or shift created them. Once settled
	(submitted), they drop out of this list via the ``docstatus = 0`` filter.
	"""
	doctype = get_invoice_type()

	if not frappe.db.has_column(doctype, "pos_awaiting_settlement"):
		return []

	if not is_pos_cashier(frappe.session.user, pos_profile):
		frappe.throw(_("You are not permitted to settle invoices."), frappe.PermissionError)

	filters = {"docstatus": 0, "is_pos": 1, "pos_awaiting_settlement": 1}
	if pos_profile:
		filters["pos_profile"] = pos_profile

	return frappe.get_list(
		doctype,
		filters=filters,
		fields=[
			"name",
			"customer",
			"customer_name",
			"posting_date",
			"posting_time",
			"grand_total",
			"total_qty",
			"currency",
			"creation",
			"modified",
		],
		limit_page_length=0,
		order_by="modified desc",
	)


def get_past_orders(
	pos_profile: str = "",
	from_date: str = "",
	to_date: str = "",
	search_term: str = "",
	page: int = 0,
	limit: int = 20,
	filters: str | None = None,
	order_by: str = "posting_date desc, posting_time desc",
):
	"""Get past submitted invoices with advanced filtering and pagination.

	Args:
	        pos_profile: POS Profile name
	        from_date: Start date for filter
	        to_date: End date for filter
	        search_term: Search in invoice name, customer name, customer
	        page: Page number (0-indexed)
	        limit: Number of records per page
	        filters: JSON array of filter conditions like Frappe's query builder
	                Format: [["fieldname", "operator", "value"], ...]
	                Operators: =, !=, >, <, >=, <=, like, not like, in, not in, between, is, is not
	        order_by: Order by clause (default: posting_date desc, posting_time desc)

	Returns:
	        dict with 'data' (list of orders) and 'total' (total count)
	"""
	conditions = "si.docstatus = 1 AND si.is_pos = 1"
	values = {"offset": cint(page) * cint(limit), "limit": cint(limit)}

	if pos_profile:
		conditions += " AND si.pos_profile = %(pos_profile)s"
		values["pos_profile"] = pos_profile

	if from_date:
		conditions += " AND si.posting_date >= %(from_date)s"
		values["from_date"] = getdate(from_date)

	if to_date:
		conditions += " AND si.posting_date <= %(to_date)s"
		values["to_date"] = getdate(to_date)

	if search_term:
		search_term = search_term.strip()
		conditions += """ AND (
			si.name LIKE %(search)s
			OR si.customer_name LIKE %(search)s
			OR si.customer LIKE %(search)s
		)"""
		values["search"] = f"%{search_term}%"

	if filters:
		if isinstance(filters, str):
			filters = json.loads(filters)

		valid_fields = {
			"status",
			"customer",
			"customer_name",
			"is_return",
			"return_against",
			"grand_total",
			"net_total",
			"paid_amount",
			"outstanding_amount",
			"posting_date",
			"posting_time",
			"currency",
			"owner",
			"modified_by",
		}

		for idx, f in enumerate(filters):
			if len(f) < 3:
				continue

			fieldname, operator, value = f[0], f[1].lower(), f[2]

			if fieldname not in valid_fields:
				continue

			param_name = f"filter_{idx}"
			operator = operator.strip()

			if operator == "=":
				conditions += f" AND si.{fieldname} = %({param_name})s"
				values[param_name] = value
			elif operator == "!=":
				conditions += f" AND si.{fieldname} != %({param_name})s"
				values[param_name] = value
			elif operator == ">":
				conditions += f" AND si.{fieldname} > %({param_name})s"
				values[param_name] = value
			elif operator == "<":
				conditions += f" AND si.{fieldname} < %({param_name})s"
				values[param_name] = value
			elif operator == ">=":
				conditions += f" AND si.{fieldname} >= %({param_name})s"
				values[param_name] = value
			elif operator == "<=":
				conditions += f" AND si.{fieldname} <= %({param_name})s"
				values[param_name] = value
			elif operator == "like":
				conditions += f" AND si.{fieldname} LIKE %({param_name})s"
				values[param_name] = f"%{value}%"
			elif operator == "not like":
				conditions += f" AND si.{fieldname} NOT LIKE %({param_name})s"
				values[param_name] = f"%{value}%"
			elif operator == "in":
				if isinstance(value, list) and value:
					placeholders = ", ".join([f"%({param_name}_{i})s" for i in range(len(value))])
					conditions += f" AND si.{fieldname} IN ({placeholders})"
					for i, v in enumerate(value):
						values[f"{param_name}_{i}"] = v
			elif operator == "not in":
				if isinstance(value, list) and value:
					placeholders = ", ".join([f"%({param_name}_{i})s" for i in range(len(value))])
					conditions += f" AND si.{fieldname} NOT IN ({placeholders})"
					for i, v in enumerate(value):
						values[f"{param_name}_{i}"] = v
			elif operator == "between":
				if isinstance(value, list) and len(value) == 2:
					conditions += f" AND si.{fieldname} BETWEEN %({param_name}_0)s AND %({param_name}_1)s"
					values[f"{param_name}_0"] = value[0]
					values[f"{param_name}_1"] = value[1]
			elif operator in ("is", "is not"):
				if value is None or str(value).lower() in (
					"null",
					"none",
					"set",
					"not set",
				):
					null_check = (
						"IS NULL"
						if operator == "is" or str(value).lower() in ("null", "none", "not set")
						else "IS NOT NULL"
					)
					if str(value).lower() == "set":
						null_check = "IS NOT NULL"
					elif str(value).lower() == "not set":
						null_check = "IS NULL"
					conditions += f" AND si.{fieldname} {null_check}"

	allowed_order_fields = {
		"posting_date",
		"posting_time",
		"grand_total",
		"name",
		"customer_name",
		"status",
		"modified",
	}
	order_parts = []
	for part in order_by.split(","):
		part = part.strip()
		if not part:
			continue
		tokens = part.split()
		field = tokens[0].lower()
		direction = tokens[1].upper() if len(tokens) > 1 else "DESC"
		if field in allowed_order_fields and direction in ("ASC", "DESC"):
			order_parts.append(f"si.{field} {direction}")

	order_clause = ", ".join(order_parts) if order_parts else "si.posting_date DESC, si.posting_time DESC"

	doctype = get_invoice_type()
	table = f"`tab{doctype}`"

	total = frappe.db.sql(
		f"""SELECT COUNT(*) FROM {table} si WHERE """ + conditions,
		values,
		as_list=True,
	)[0][0]

	orders = frappe.db.sql(
		f"""SELECT
			si.name,
			si.customer,
			si.customer_name,
			si.posting_date,
			si.posting_time,
			si.grand_total,
			si.net_total,
			si.total_taxes_and_charges,
			si.paid_amount,
			si.currency,
			si.status,
			si.is_return,
			si.return_against,
			si.owner,
			si.modified
		FROM {table} si
		WHERE """
		+ conditions
		+ """
		ORDER BY """
		+ order_clause
		+ """
		LIMIT %(offset)s, %(limit)s
		""",
		values,
		as_dict=True,
	)

	return {"data": orders, "total": total}


def get_invoices(
	pos_opening_entry: str | None = None,
	is_return: int | None = None,
	limit: int = 50,
	pos_profile: str = "",
):
	"""Return POS invoices filtered by opening shift and optional return flag."""
	doctype = get_invoice_type()
	filters = {"docstatus": 1, "is_pos": 1}
	if pos_opening_entry:
		filters["pos_opening_entry"] = pos_opening_entry
	if is_return is not None:
		filters["is_return"] = cint(is_return)

	return frappe.get_all(
		doctype,
		filters=filters,
		fields=[
			"name",
			"customer",
			"customer_name",
			"posting_date",
			"posting_time",
			"grand_total",
			"net_total",
			"paid_amount",
			"status",
			"is_return",
			"return_against",
		],
		order_by="posting_date desc, posting_time desc, modified desc",
		limit_page_length=cint(limit) if limit else 50,
	)


def get_invoice_details(invoice_name: str, doctype: str = ""):
	"""Get full invoice details including items and payments."""
	if not doctype:
		doctype = _detect_invoice_doctype(invoice_name)
	doc = frappe.get_doc(doctype, invoice_name)

	return {
		"name": doc.name,
		"customer": doc.customer,
		"customer_name": doc.customer_name,
		"posting_date": str(doc.posting_date),
		"posting_time": str(doc.posting_time),
		"grand_total": doc.grand_total,
		"net_total": doc.net_total,
		"total_taxes_and_charges": doc.total_taxes_and_charges,
		"paid_amount": doc.paid_amount,
		"change_amount": doc.change_amount,
		"outstanding_amount": getattr(doc, "outstanding_amount", 0),
		"currency": doc.currency,
		"status": doc.status,
		"is_return": doc.is_return,
		"return_against": getattr(doc, "return_against", None),
		"discount_amount": getattr(doc, "discount_amount", 0),
		"additional_discount_percentage": getattr(doc, "additional_discount_percentage", 0),
		"base_discount_amount": getattr(doc, "base_discount_amount", 0),
		"total_qty": getattr(doc, "total_qty", 0),
		"total": getattr(doc, "total", 0),
		"sales_partner": getattr(doc, "sales_partner", None),
		"commission_rate": getattr(doc, "commission_rate", 0),
		"total_commission": getattr(doc, "total_commission", 0),
		"loyalty_program": getattr(doc, "loyalty_program", None),
		"loyalty_points": getattr(doc, "loyalty_points", 0),
		"loyalty_amount": getattr(doc, "loyalty_amount", 0),
		"redeem_loyalty_points": getattr(doc, "redeem_loyalty_points", 0),
		"loyalty_redemption_account": getattr(doc, "loyalty_redemption_account", None),
		"owner": doc.owner,
		"pos_profile": getattr(doc, "pos_profile", None),
		"coupon_code": getattr(doc, "coupon_code", None),
		"remarks": getattr(doc, "remarks", None),
		"pos_delivery_charges": getattr(doc, "pos_delivery_charges", None),
		"pos_delivery_charges_rate": getattr(doc, "pos_delivery_charges_rate", 0),
		"pos_delivery_charges_label": (
			frappe.get_cached_value("Delivery Charges", doc.pos_delivery_charges, "label")
			if getattr(doc, "pos_delivery_charges", None)
			else None
		),
		"items": [
			{
				"item_code": i.item_code,
				"item_name": i.item_name,
				"qty": i.qty,
				"rate": i.rate,
				"amount": i.amount,
				"uom": i.uom,
				"discount_percentage": i.discount_percentage,
				"discount_amount": i.discount_amount,
				"serial_no": getattr(i, "serial_no", None),
				"batch_no": getattr(i, "batch_no", None),
			}
			for i in doc.items
		],
		"payments": [
			{
				"mode_of_payment": p.mode_of_payment,
				"amount": p.amount,
			}
			for p in doc.payments
		],
		"taxes": [
			{
				"description": t.description,
				"rate": t.rate,
				"tax_amount": t.tax_amount,
			}
			for t in doc.taxes
		],
	}


def delete_draft_invoice(name: str, doctype: str = ""):
	"""Delete a draft invoice."""
	if not doctype:
		doctype = _detect_invoice_doctype(name)
	doc = frappe.get_doc(doctype, name)
	if doc.docstatus != 0:
		frappe.throw(_("Only draft invoices can be deleted"))
	doc.delete(ignore_permissions=True)
	return {"success": True}


def search_invoices_for_return(
	company: str,
	invoice_name: str = "",
	customer_name: str = "",
	customer_id: str = "",
	mobile_no: str = "",
	from_date: str = "",
	to_date: str = "",
	min_amount: float | None = None,
	max_amount: float | None = None,
	page: int = 1,
	pos_profile: str = "",
	doctype: str = "Sales Invoice",
):
	"""Search for invoices that can be returned.

	Supports multi-field customer search, date/amount filtering, and pagination.
	"""
	page = max(cint(page), 1)
	page_length = 50
	start = (page - 1) * page_length

	if doctype not in ("Sales Invoice", "POS Invoice"):
		frappe.throw(_("Invalid doctype for return search"))

	table = f"`tab{doctype}`"

	conditions = [
		f"{table}.company = %(company)s",
		f"{table}.docstatus = 1",
		f"{table}.is_return = 0",
	]
	params: dict = {"company": company}

	if from_date and to_date:
		conditions.append(f"{table}.posting_date BETWEEN %(from_date)s AND %(to_date)s")
		params["from_date"] = from_date
		params["to_date"] = to_date
	elif from_date:
		conditions.append(f"{table}.posting_date >= %(from_date)s")
		params["from_date"] = from_date
	elif to_date:
		conditions.append(f"{table}.posting_date <= %(to_date)s")
		params["to_date"] = to_date

	if min_amount and max_amount:
		conditions.append(f"{table}.grand_total BETWEEN %(min_amount)s AND %(max_amount)s")
		params["min_amount"] = flt(min_amount)
		params["max_amount"] = flt(max_amount)
	elif min_amount:
		conditions.append(f"{table}.grand_total >= %(min_amount)s")
		params["min_amount"] = flt(min_amount)
	elif max_amount:
		conditions.append(f"{table}.grand_total <= %(max_amount)s")
		params["max_amount"] = flt(max_amount)

	or_parts = []
	if invoice_name:
		or_parts.append(f"{table}.name LIKE %(inv_name)s")
		params["inv_name"] = f"%{invoice_name}%"

	if customer_name:
		or_parts.append(f"{table}.customer_name LIKE %(cust_name)s")
		params["cust_name"] = f"%{customer_name}%"

	if customer_id:
		or_parts.append(f"{table}.customer LIKE %(cust_id)s")
		params["cust_id"] = f"%{customer_id}%"

	if mobile_no:
		cust_by_mobile = frappe.db.sql(
			"SELECT name FROM `tabCustomer` WHERE mobile_no LIKE %(mob)s LIMIT 100",
			{"mob": f"%{mobile_no}%"},
			as_dict=True,
		)
		if cust_by_mobile:
			mob_ids = [c.name for c in cust_by_mobile]
			mob_placeholders = ", ".join([f"%(mob_{i})s" for i in range(len(mob_ids))])
			or_parts.append(f"{table}.customer IN ({mob_placeholders})")
			for i, mid in enumerate(mob_ids):
				params[f"mob_{i}"] = mid

	if or_parts:
		conditions.append(f"({' OR '.join(or_parts)})")

	where_clause = " AND ".join(conditions)
	# nosemgrep: frappe-sql-format-injection — table/column from validated doctype allowlist, all values parameterized
	sql = f"""
		SELECT
			{table}.name, {table}.company, {table}.customer, {table}.customer_name,
			{table}.posting_date, {table}.posting_time, {table}.grand_total, {table}.currency,
			{table}.discount_amount, {table}.additional_discount_percentage,
			{table}.is_return
		FROM {table}
		WHERE {where_clause}
		ORDER BY {table}.posting_date DESC, {table}.name DESC
		LIMIT %(limit)s OFFSET %(offset)s
		"""
	invoices = frappe.db.sql(
		sql,
		{**params, "limit": page_length + 1, "offset": start},
		as_dict=True,
	)

	has_more = len(invoices) > page_length
	if has_more:
		invoices = invoices[:page_length]

	if pos_profile:
		pos = frappe.get_cached_doc("POS Profile", pos_profile)
		enforce_return_validity = cint(pos.get("enable_return_validity"))
		if enforce_return_validity:
			for inv in invoices:
				validity_date = inv.get("return_valid_upto")
				inv["return_expired"] = (
					1 if (validity_date and getdate(nowdate()) > getdate(validity_date)) else 0
				)

	total_count = start + len(invoices) + (1 if has_more else 0)

	return {"invoices": invoices, "has_more": has_more, "total_count": total_count}


def get_invoice_for_return(invoice_name: str, pos_profile: str = "", doctype: str = "Sales Invoice"):
	"""Fetch a single invoice with remaining returnable item quantities.

	Accounts for past returns to show only what can still be returned.
	"""
	doc = frappe.get_doc(doctype, invoice_name)

	return_invoices = frappe.get_all(
		doctype,
		filters={
			"return_against": invoice_name,
			"docstatus": 1,
			"is_return": 1,
		},
		pluck="name",
	)

	returned_qty_map = {}
	for ret_name in return_invoices:
		ret_doc = frappe.get_doc(doctype, ret_name)
		for item in ret_doc.items:
			key = (item.item_code, getattr(item, "batch_no", None) or "")
			returned_qty_map[key] = returned_qty_map.get(key, 0) + abs(item.qty)

	items = []
	is_fully_returned = True
	for item in doc.items:
		key = (item.item_code, getattr(item, "batch_no", None) or "")
		already_returned = returned_qty_map.get(key, 0)
		remaining_qty = flt(item.qty) - already_returned

		if remaining_qty > 0:
			is_fully_returned = False

		items.append(
			{
				"item_code": item.item_code,
				"item_name": item.item_name,
				"qty": item.qty,
				"rate": item.rate,
				"amount": item.amount,
				"uom": item.uom,
				"serial_no": getattr(item, "serial_no", None),
				"batch_no": getattr(item, "batch_no", None),
				"already_returned_qty": already_returned,
				"remaining_returnable_qty": max(remaining_qty, 0),
			}
		)

	return_expired = False
	if pos_profile:
		pos = frappe.get_cached_doc("POS Profile", pos_profile)
		if cint(pos.get("enable_return_validity")):
			validity_date = getattr(doc, "return_valid_upto", None)
			if validity_date and getdate(nowdate()) > getdate(validity_date):
				return_expired = True

	return {
		"name": doc.name,
		"customer": doc.customer,
		"customer_name": doc.customer_name,
		"posting_date": str(doc.posting_date),
		"grand_total": doc.grand_total,
		"currency": doc.currency,
		"items": items,
		"is_fully_returned": is_fully_returned,
		"return_expired": return_expired,
		"payments": [{"mode_of_payment": p.mode_of_payment, "amount": p.amount} for p in doc.payments],
	}


def search_invoices_for_repeat(
	company: str,
	search_term: str = "",
	customer: str = "",
	from_date: str = "",
	to_date: str = "",
	pos_profile: str = "",
	page: int = 1,
	doctype: str = "Sales Invoice",
):
	"""Search submitted invoices to repeat/duplicate.

	Returns a paginated list of submitted invoices matching the filters.
	"""
	page = max(cint(page), 1)
	page_length = 20
	start = (page - 1) * page_length

	filters = {
		"company": company,
		"docstatus": 1,
		"is_return": 0,
	}

	if search_term:
		filters["name"] = ["like", f"%{search_term}%"]
	if customer:
		filters["customer"] = ["like", f"%{customer}%"]
	if from_date and to_date:
		filters["posting_date"] = ["between", [from_date, to_date]]
	elif from_date:
		filters["posting_date"] = [">=", from_date]
	elif to_date:
		filters["posting_date"] = ["<=", to_date]

	invoices = frappe.get_list(
		doctype,
		filters=filters,
		fields=[
			"name",
			"customer",
			"customer_name",
			"posting_date",
			"grand_total",
			"currency",
			"total_qty",
		],
		limit_start=start,
		limit_page_length=page_length + 1,
		order_by="posting_date desc, name desc",
	)

	has_more = len(invoices) > page_length
	if has_more:
		invoices = invoices[:page_length]

	return {"invoices": invoices, "has_more": has_more}


def get_invoice_for_repeat(invoice_name: str, pos_profile: str = "", doctype: str = "Sales Invoice"):
	"""Fetch invoice details for repeating/duplicating into a new cart.

	Returns item details with current stock prices so the repeated
	invoice uses up-to-date pricing.
	"""
	if not frappe.db.exists(doctype, invoice_name):
		alt = "POS Invoice" if doctype == "Sales Invoice" else "Sales Invoice"
		if frappe.db.exists(alt, invoice_name):
			doctype = alt
		else:
			frappe.throw(_("Invoice {0} not found").format(invoice_name))

	doc = frappe.get_doc(doctype, invoice_name)

	price_list = None
	if pos_profile:
		price_list = frappe.db.get_value("POS Profile", pos_profile, "selling_price_list")

	items = []
	for item in doc.items:
		if getattr(item, "is_offer", False):
			continue

		item_data = {
			"item_code": item.item_code,
			"item_name": item.item_name,
			"qty": abs(item.qty),
			"rate": item.rate,
			"uom": item.uom,
			"stock_uom": item.stock_uom or item.uom,
			"discount_percentage": flt(item.discount_percentage),
			"discount_amount": flt(item.discount_amount),
			"serial_no": getattr(item, "serial_no", None),
			"batch_no": getattr(item, "batch_no", None),
		}

		if price_list:
			current_rate = frappe.db.get_value(
				"Item Price",
				{"item_code": item.item_code, "price_list": price_list, "selling": 1},
				"price_list_rate",
			)
			if current_rate is not None:
				item_data["rate"] = flt(current_rate)
				item_data["discount_percentage"] = 0
				item_data["discount_amount"] = 0

		items.append(item_data)

	return {
		"name": doc.name,
		"customer": doc.customer,
		"customer_name": doc.customer_name,
		"posting_date": str(doc.posting_date),
		"grand_total": doc.grand_total,
		"currency": doc.currency,
		"items": items,
	}

