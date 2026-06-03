# Copyright (c) 2026, FadlTech team and contributors

"""Offers and coupons RPC."""

from __future__ import annotations

import frappe

from fadl_pos.api.rpc_boundary import dump_out, validate_in
from fadl_pos.schemas import (
	ApplyOfferIn,
	ApplyOfferOut,
	OffersActiveIn,
	OffersActiveOut,
	OffersCouponsIn,
	OffersCouponsOut,
)
from fadl_pos.services.offers_service import OffersService


@frappe.whitelist()
def active(pos_profile: str | None = None):
	"""``/api/method/fadl_pos.api.offers.active``"""
	body = validate_in(OffersActiveIn, {"pos_profile": pos_profile})
	return dump_out(OffersActiveOut, OffersService().get_active_offers(pos_profile=body.pos_profile))


@frappe.whitelist()
def coupons(customer: str | None = None):
	"""``/api/method/fadl_pos.api.offers.coupons``"""
	body = validate_in(OffersCouponsIn, {"customer": customer})
	return dump_out(OffersCouponsOut, OffersService().get_coupons(customer=body.customer))


@frappe.whitelist(methods=["POST"])
def apply(invoice_name: str | None = None, coupon_code: str | None = None):
	"""``/api/method/fadl_pos.api.offers.apply``"""
	body = validate_in(
		ApplyOfferIn,
		{"invoice_name": invoice_name or "", "coupon_code": coupon_code},
	)
	result = OffersService().apply_offer(body.invoice_name, coupon_code=body.coupon_code)
	return dump_out(ApplyOfferOut, result)
