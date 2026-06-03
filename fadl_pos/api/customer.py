# Copyright (c) 2026, FadlTech team and contributors

"""Customer RPC — one whitelist per operation."""

from __future__ import annotations

import frappe
from frappe import _
from pydantic import ValidationError

from fadl_pos.api.rpc_boundary import dump_out, raise_validation_error, validate_in
from fadl_pos.schemas import (
	CustomerCreateIn,
	CustomerDetailsIn,
	CustomerDetailsOut,
	CustomerListIn,
	CustomerListOut,
	CustomerManageOut,
	CustomerRecentTransactionsIn,
	CustomerSetInfoIn,
	CustomerTransactionsOut,
	CustomerUpdateIn,
)
from fadl_pos.services.customer_service import CustomerService


@frappe.whitelist()
def list_customers(search_term: str | None = None, limit: int | None = None):
	"""``/api/method/fadl_pos.api.customer.list_customers``"""
	body = validate_in(
		CustomerListIn,
		{"search_term": search_term or "", "limit": limit if limit is not None else 10},
	)
	return dump_out(CustomerListOut, CustomerService().get_list(search_term=body.search_term, limit=body.limit))


@frappe.whitelist()
def details(customer: str | None = None):
	"""``/api/method/fadl_pos.api.customer.details``"""
	body = validate_in(CustomerDetailsIn, {"customer": customer or ""})
	return dump_out(CustomerDetailsOut, CustomerService().get_details(customer=body.customer))


@frappe.whitelist()
def recent_transactions(customer: str | None = None):
	"""``/api/method/fadl_pos.api.customer.recent_transactions``"""
	body = validate_in(CustomerRecentTransactionsIn, {"customer": customer or ""})
	return dump_out(
		CustomerTransactionsOut,
		CustomerService().get_recent_transactions(customer=body.customer),
	)


@frappe.whitelist(methods=["POST"])
def create(data: str | None = None):
	"""``/api/method/fadl_pos.api.customer.create``"""
	try:
		payload = CustomerCreateIn.model_validate_json(data or "{}")
	except ValidationError as exc:
		raise_validation_error(exc)
	return dump_out(CustomerManageOut, CustomerService().create(payload.model_dump()))


@frappe.whitelist(methods=["POST"])
def update(data: str | None = None):
	"""``/api/method/fadl_pos.api.customer.update``"""
	try:
		payload = CustomerUpdateIn.model_validate_json(data or "{}")
	except ValidationError as exc:
		raise_validation_error(exc)
	return dump_out(CustomerManageOut, CustomerService().update(payload.model_dump()))


@frappe.whitelist(methods=["POST"])
def set_info(
	fieldname: str | None = None,
	customer: str | None = None,
	value: str | None = None,
):
	"""``/api/method/fadl_pos.api.customer.set_info`` — native ``set_customer_info``."""
	from erpnext.selling.page.point_of_sale.point_of_sale import set_customer_info

	body = validate_in(
		CustomerSetInfoIn,
		{"fieldname": fieldname or "", "customer": customer or "", "value": value or ""},
	)
	set_customer_info(body.fieldname, body.customer, body.value)
	return CustomerManageOut.dump(
		{"status": "success", "message": _("Customer information updated")}
	)
