# Copyright (c) 2026, FadlTech team and contributors

"""Invoice sync RPC — one whitelist per operation."""

from __future__ import annotations

import json

import frappe

from fadl_pos.api.rpc_boundary import dump_out, validate_in
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


@frappe.whitelist(methods=["POST"])
def save(data: str | None = None):
	body = validate_in(InvoiceSaveIn, {"data": data or ""})
	payload = validate_in(InvoiceSyncBody, json.loads(body.data))
	return dump_out(InvoiceSaveOut, InvoiceService().save(payload.model_dump()))


@frappe.whitelist(methods=["POST"])
def submit(data: str | None = None):
	body = validate_in(InvoiceSubmitIn, {"data": data or ""})
	payload = validate_in(InvoiceSyncBody, json.loads(body.data))
	return dump_out(InvoiceSubmitOut, InvoiceService().submit(payload.model_dump()))


@frappe.whitelist(methods=["POST"])
def return_invoice(data: str | None = None):
	body = validate_in(InvoiceReturnIn, {"data": data or ""})
	payload = validate_in(InvoiceSyncBody, json.loads(body.data))
	return dump_out(InvoiceReturnOut, InvoiceService().make_return(payload.model_dump()))


@frappe.whitelist(methods=["POST"])
def void(data: str | None = None):
	body = validate_in(InvoiceVoidIn, {"data": data or ""})
	payload = validate_in(InvoiceSyncBody, json.loads(body.data))
	return dump_out(InvoiceVoidOut, InvoiceService().void(payload.model_dump()))


@frappe.whitelist(methods=["POST"])
def validate_cart(data: str | None = None):
	body = validate_in(InvoiceValidateCartIn, {"data": data or ""})
	payload = validate_in(InvoiceSyncBody, json.loads(body.data))
	payload_data = payload.model_dump()
	cart = validate_in(
		CartValidateIn,
		{"items": payload_data.get("items", []), "warehouse": payload_data.get("warehouse") or ""},
	)
	return dump_out(CartValidateOut, ValidationService.validate_cart_items(cart.model_dump()))
