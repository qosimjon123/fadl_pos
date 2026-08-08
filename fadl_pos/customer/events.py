# Copyright (c) 2026, FadlTech team and contributors

"""Customer domain events + Document hooks (xpos.x_pos.api.customer parity)."""

from __future__ import annotations

from typing import Any

import frappe
from frappe import _

from fadl_pos.core.events import emit
from fadl_pos.fadl_pos.doctype.referral_code.referral_code import create_referral_code

CUSTOMER_CREATED = "customer.created"
CUSTOMER_UPDATED = "customer.updated"
LOYALTY_REGISTERED = "customer.loyalty_registered"
LOYALTY_UNENROLLED = "customer.loyalty_unenrolled"


def customer_created(*, customer: str, user: str) -> None:
	emit(CUSTOMER_CREATED, customer=customer, user=user)


def customer_updated(*, customer: str, user: str) -> None:
	emit(CUSTOMER_UPDATED, customer=customer, user=user)


def loyalty_registered(*, customer: str, loyalty_program: str, user: str) -> None:
	emit(LOYALTY_REGISTERED, customer=customer, loyalty_program=loyalty_program, user=user)


def loyalty_unenrolled(*, customer: str, user: str) -> None:
	emit(LOYALTY_UNENROLLED, customer=customer, user=user)


# --- Document hooks (registered in hooks.py doc_events) ---


def after_insert(doc: Any, method: str | None = None) -> None:
	create_customer_referral_code(doc)
	create_gift_coupon(doc)


def validate(doc: Any, method: str | None = None) -> None:
	validate_referral_code(doc)


def create_customer_referral_code(doc: Any) -> None:
	if not doc.get("referral_company"):
		return
	company = frappe.get_cached_doc("Company", doc.referral_company)
	if not company.get("auto_referral"):
		return
	create_referral_code(
		doc.referral_company,
		doc.name,
		company.get("final_customer_offer"),
		company.get("primary_customer_offer"),
		company.get("referral_campaign"),
	)


def create_gift_coupon(doc: Any) -> None:
	if not doc.get("referral_code"):
		return
	coupon = frappe.new_doc("POS Coupon")
	coupon.customer = doc.name
	coupon.referral_code = doc.referral_code
	coupon.create_coupon_from_referral()


def validate_referral_code(doc: Any) -> None:
	referral_code = doc.get("referral_code")
	if not referral_code:
		return
	exist = frappe.db.exists("Referral Code", referral_code)
	if not exist:
		exist = frappe.db.exists("Referral Code", {"referral_code": referral_code})
	if not exist:
		frappe.throw(_("This Referral Code {0} not exists").format(referral_code))
