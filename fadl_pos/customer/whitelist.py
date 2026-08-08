# Copyright (c) 2026, FadlTech team and contributors

"""Customer RPC endpoints for Frappe `/api/method/...` calls.

New routes (no back-compat shim, per established convention): every endpoint
lives at ``fadl_pos.customer.whitelist.<name>``.
"""

from __future__ import annotations

import json
from typing import Any

import frappe

from fadl_pos.core.serializer import dump_out, dump_out_list, validate_in
from fadl_pos.customer.controller import CustomerController
from fadl_pos.customer.serializer import (
	AddressCreateIn,
	AddressCreateOut,
	AddressOut,
	CustomerCreateIn,
	CustomerCreateOut,
	CustomerCreditIn,
	CustomerCreditRowOut,
	CustomerDetailsIn,
	CustomerDetailsOut,
	CustomerListIn,
	CustomerRef,
	CustomerRowOut,
	CustomerUpdateIn,
	CustomerUpdateOut,
	LoyaltyInfoOut,
	LoyaltyProgramOut,
	LoyaltyProgramsIn,
	LoyaltyRegisterIn,
	LoyaltyRegisterOut,
	LoyaltyUnenrollOut,
	SalesPersonOut,
)


def _controller() -> CustomerController:
	return CustomerController()


def _parse_object(value: object | None) -> dict[str, Any]:
	if value is None:
		return {}
	if isinstance(value, str):
		return json.loads(value) if value.strip() else {}
	return dict(value)


@frappe.whitelist(methods=["GET", "POST"])
def get_customers(search_term: str = "", limit: int = 20, pos_profile: str | None = None):
	"""``/api/method/fadl_pos.customer.whitelist.get_customers``"""
	body = validate_in(
		CustomerListIn,
		{"search_term": search_term, "limit": limit, "pos_profile": pos_profile},
	)
	rows = _controller().search(body.search_term, body.limit, body.pos_profile)
	return dump_out_list(CustomerRowOut, rows)


@frappe.whitelist(methods=["GET", "POST"])
def get_customer_info(customer: str | None = None):
	"""``/api/method/fadl_pos.customer.whitelist.get_customer_info``"""
	body = validate_in(CustomerDetailsIn, {"customer": customer or ""})
	result = _controller().get_details(body.customer)
	return dump_out(CustomerDetailsOut, result)


@frappe.whitelist(methods=["POST"])
def create_customer(
	customer_name: str | None = None,
	mobile_no: str = "",
	email_id: str = "",
	customer_group: str | None = None,
	territory: str | None = None,
	customer_type: str = "Individual",
	gender: str | None = None,
	tax_id: str | None = None,
	birthday: str | None = None,
	company: str | None = None,
	pos_profile: str | None = None,
	address_line1: str | None = None,
	city: str | None = None,
	country: str | None = None,
):
	"""``/api/method/fadl_pos.customer.whitelist.create_customer``"""
	body = validate_in(
		CustomerCreateIn,
		{
			"customer_name": customer_name or "",
			"mobile_no": mobile_no,
			"email_id": email_id,
			"customer_group": customer_group,
			"territory": territory,
			"customer_type": customer_type,
			"gender": gender,
			"tax_id": tax_id,
			"birthday": birthday,
			"company": company,
			"pos_profile": pos_profile,
			"address_line1": address_line1,
			"city": city,
			"country": country,
		},
	)
	result = _controller().create(
		body.customer_name,
		mobile_no=body.mobile_no,
		email_id=body.email_id,
		customer_group=body.customer_group,
		territory=body.territory,
		customer_type=body.customer_type,
		gender=body.gender,
		tax_id=body.tax_id,
		birthday=body.birthday,
		company=body.company,
		address_line1=body.address_line1,
		city=body.city,
		country=body.country,
	)
	return dump_out(CustomerCreateOut, result)


@frappe.whitelist(methods=["POST"])
def update_customer(customer: str | None = None, data: object | None = None):
	"""``/api/method/fadl_pos.customer.whitelist.update_customer``"""
	raw = _parse_object(data)
	raw["customer"] = customer or ""
	body = validate_in(CustomerUpdateIn, raw)
	patch = body.model_dump(exclude={"customer"}, exclude_unset=True)
	result = _controller().update(body.customer, patch)
	return dump_out(CustomerUpdateOut, result)


@frappe.whitelist(methods=["GET", "POST"])
def get_customer_addresses(customer: str | None = None):
	"""``/api/method/fadl_pos.customer.whitelist.get_customer_addresses``"""
	body = validate_in(CustomerRef, {"customer": customer or ""})
	rows = _controller().get_addresses(body.customer)
	return dump_out_list(AddressOut, rows)


@frappe.whitelist(methods=["POST"])  # nosemgrep: overusing-args — args is a JSON-encoded dict from the client
def make_address(args: object | None = None):
	"""``/api/method/fadl_pos.customer.whitelist.make_address``"""
	body = validate_in(AddressCreateIn, _parse_object(args))
	result = _controller().create_address(body.model_dump())
	return dump_out(AddressCreateOut, result)


@frappe.whitelist(methods=["GET", "POST"])
def get_customer_credit(customer: str | None = None, company: str | None = None):
	"""``/api/method/fadl_pos.customer.whitelist.get_customer_credit``"""
	body = validate_in(CustomerCreditIn, {"customer": customer or "", "company": company or ""})
	rows = _controller().get_credit(body.customer, body.company)
	return dump_out_list(CustomerCreditRowOut, rows)


@frappe.whitelist(methods=["GET", "POST"])
def get_sales_person_names():
	"""``/api/method/fadl_pos.customer.whitelist.get_sales_person_names``"""
	rows = _controller().get_sales_persons()
	return dump_out_list(SalesPersonOut, rows)


@frappe.whitelist(methods=["GET", "POST"])
def get_loyalty_programs(company: str | None = None):
	"""``/api/method/fadl_pos.customer.whitelist.get_loyalty_programs``"""
	body = validate_in(LoyaltyProgramsIn, {"company": company})
	rows = _controller().get_loyalty_programs(body.company)
	return dump_out_list(LoyaltyProgramOut, rows)


@frappe.whitelist(methods=["POST"])
def register_customer_loyalty(customer: str | None = None, loyalty_program: str | None = None):
	"""``/api/method/fadl_pos.customer.whitelist.register_customer_loyalty``"""
	body = validate_in(
		LoyaltyRegisterIn, {"customer": customer or "", "loyalty_program": loyalty_program or ""}
	)
	result = _controller().register_loyalty(body.customer, body.loyalty_program)
	return dump_out(LoyaltyRegisterOut, result)


@frappe.whitelist(methods=["POST"])
def unenroll_customer_loyalty(customer: str | None = None):
	"""``/api/method/fadl_pos.customer.whitelist.unenroll_customer_loyalty``"""
	body = validate_in(CustomerRef, {"customer": customer or ""})
	result = _controller().unenroll_loyalty(body.customer)
	return dump_out(LoyaltyUnenrollOut, result)


@frappe.whitelist(methods=["GET", "POST"])
def get_customer_loyalty_info(customer: str | None = None):
	"""``/api/method/fadl_pos.customer.whitelist.get_customer_loyalty_info``"""
	body = validate_in(CustomerRef, {"customer": customer or ""})
	result = _controller().get_loyalty_info(body.customer)
	return dump_out(LoyaltyInfoOut, result)


@frappe.whitelist(methods=["GET", "POST"])
def get_customer_groups():
	"""``/api/method/fadl_pos.customer.whitelist.get_customer_groups``"""
	return _controller().get_groups()
