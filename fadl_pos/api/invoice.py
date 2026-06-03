# Copyright (c) 2026, FadlTech team and contributors

"""Invoice sync RPC — one whitelist per operation."""

from __future__ import annotations

import frappe
from pydantic import ValidationError

from fadl_pos.api.rpc_boundary import dump_out, raise_validation_error, validate_in
from fadl_pos.schemas import (
	CartValidateIn,
	CartValidateOut,
	InvoiceReturnIn,
	InvoiceReturnOut,
	InvoiceSaveIn,
	InvoiceSaveOut,
	InvoiceSubmitIn,
	InvoiceSubmitOut,
	InvoiceSyncBody,
	InvoiceValidateCartIn,
	InvoiceVoidIn,
	InvoiceVoidOut,
)
from fadl_pos.services.invoice_service import InvoiceService
from fadl_pos.services.validation_service import ValidationService


def _parse_invoice_data(data: str) -> dict:
	try:
		return InvoiceSyncBody.model_validate_json(data).model_dump()
	except ValidationError as exc:
		raise_validation_error(exc)
		raise AssertionError("unreachable")


@frappe.whitelist(methods=["POST"])
def save(data: str | None = None):
	body = validate_in(InvoiceSaveIn, {"data": data or ""})
	return dump_out(InvoiceSaveOut, InvoiceService().save(_parse_invoice_data(body.data)))


@frappe.whitelist(methods=["POST"])
def submit(data: str | None = None):
	body = validate_in(InvoiceSubmitIn, {"data": data or ""})
	return dump_out(InvoiceSubmitOut, InvoiceService().submit(_parse_invoice_data(body.data)))


@frappe.whitelist(methods=["POST"])
def return_invoice(data: str | None = None):
	body = validate_in(InvoiceReturnIn, {"data": data or ""})
	return dump_out(InvoiceReturnOut, InvoiceService().make_return(_parse_invoice_data(body.data)))


@frappe.whitelist(methods=["POST"])
def void(data: str | None = None):
	body = validate_in(InvoiceVoidIn, {"data": data or ""})
	return dump_out(InvoiceVoidOut, InvoiceService().void(_parse_invoice_data(body.data)))


@frappe.whitelist(methods=["POST"])
def validate_cart(data: str | None = None):
	body = validate_in(InvoiceValidateCartIn, {"data": data or ""})
	payload = _parse_invoice_data(body.data)
	cart = validate_in(
		CartValidateIn,
		{"items": payload.get("items", []), "warehouse": payload.get("warehouse") or ""},
	)
	return dump_out(CartValidateOut, ValidationService.validate_cart_items(cart.model_dump()))
