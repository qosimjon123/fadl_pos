# Copyright (c) 2026, FadlTech team and contributors

"""Payment RPC — one whitelist per operation."""

from __future__ import annotations

import frappe

from fadl_pos.api.rpc_boundary import dump_out, validate_in
from fadl_pos.schemas import (
	CouponOut,
	CouponValidateIn,
	LoyaltyDetailsIn,
	LoyaltyDetailsOut,
	PaymentUpdateIn,
	PaymentUpdateOut,
)
from fadl_pos.services.payment_service import PaymentService


@frappe.whitelist()
def update_invoice_payments(invoice_name: str | None = None, payments: object | None = None):
	"""``/api/method/fadl_pos.api.payment.update_invoice_payments``"""
	body = validate_in(
		PaymentUpdateIn,
		{"invoice_name": invoice_name or "", "payments": payments},
	)
	payments = [p.model_dump() for p in body.payments]
	return dump_out(
		PaymentUpdateOut,
		PaymentService().update_invoice_payments(body.invoice_name, payments),
	)


@frappe.whitelist()
def validate_coupon(coupon_code: str | None = None):
	"""``/api/method/fadl_pos.api.payment.validate_coupon``"""
	body = validate_in(CouponValidateIn, {"coupon_code": coupon_code or ""})
	return dump_out(CouponOut, PaymentService().validate_coupon(body.coupon_code))


@frappe.whitelist()
def get_loyalty_details(customer: str | None = None, posting_date: str | None = None):
	"""``/api/method/fadl_pos.api.payment.get_loyalty_details``"""
	body = validate_in(
		LoyaltyDetailsIn,
		{"customer": customer or "", "posting_date": posting_date},
	)
	return dump_out(
		LoyaltyDetailsOut,
		PaymentService().get_loyalty_details(body.customer, posting_date=body.posting_date),
	)
