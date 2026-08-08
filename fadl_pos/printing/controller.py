# Copyright (c) 2026, FadlTech team and contributors

"""printing controller — django-like actions."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import cint

from fadl_pos.core.permission import BaseController
from fadl_pos.printing import qz as qz_svc

REPRINT_DOCTYPES = ("Sales Invoice", "POS Invoice")


class PrintingController(BaseController):
	def get_print_formats(self, doctype: str = "Sales Invoice"):
		"""Returns available print format names for a doctype."""
		print_formats = frappe.get_all(
			"Print Format",
			filters={"doc_type": doctype, "disabled": 0},
			fields=["name"],
		)
		return [p.name for p in print_formats]

	def get_receipt_context(self, pos_profile: str, print_format: str | None = None) -> dict:
		"""Resolve everything the desktop app needs to render a receipt offline."""
		profile = frappe.get_cached_doc("POS Profile", pos_profile)
		company = frappe.get_cached_doc("Company", profile.company)

		address = ""
		if company.get("company_address"):
			addr = frappe.get_cached_doc("Address", company.company_address)
			address = ", ".join(
				p
				for p in [
					addr.address_line1,
					addr.address_line2,
					addr.city,
					addr.state,
					addr.pincode,
				]
				if p
			)

		fmt = print_format or profile.get("default_print_format") or "XPOS Thermal Receipt"
		css = frappe.db.get_value("Print Format", fmt, "css") or ""

		return {
			"company_name": company.company_name or company.name,
			"company_phone": company.get("phone_no") or "",
			"company_email": company.get("email") or "",
			"company_website": company.get("website") or "",
			"company_address": address,
			"company_tax_id": company.get("tax_id") or "",
			"company_logo": company.get("company_logo") or "",
			"receipt_header": company.get("receipt_header") or "",
			"receipt_footer": company.get("receipt_footer") or "",
			"currency": company.get("default_currency") or "",
			"print_discount_amount": cint(profile.get("print_discount_amount")),
			"print_format": fmt,
			"css": css,
		}

	def mark_invoice_printed(self, doctype: str, name: str) -> dict:
		"""Record that a POS receipt has printed, so later prints count as reprints."""
		if doctype not in REPRINT_DOCTYPES:
			frappe.throw(_("Unsupported doctype for print tracking: {0}").format(doctype))
		current = cint(frappe.db.get_value(doctype, name, "print_count"))
		frappe.db.set_value(doctype, name, "print_count", current + 1, update_modified=False)
		return {"name": name, "print_count": current + 1}

	def get_certificate(self, *args, **kwargs):
		return qz_svc.get_certificate(*args, **kwargs)

	def get_certificate_download(self, *args, **kwargs):
		return qz_svc.get_certificate_download(*args, **kwargs)

	def sign_message(self, *args, **kwargs):
		return qz_svc.sign_message(*args, **kwargs)

	def setup_qz_certificate(self, *args, **kwargs):
		return qz_svc.setup_qz_certificate(*args, **kwargs)
