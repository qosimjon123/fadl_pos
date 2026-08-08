# Copyright (c) 2026, FadlTech team and contributors

"""Payment entry creation for sales orders."""

from __future__ import annotations

import frappe
from frappe.utils import nowdate

from fadl_pos.payment.processing.creation import create_payment_entry


def _payment_entry_job(order_name: str, payments: list[dict]):
	"""Background task to create payment entries."""
	so_doc = frappe.get_doc("Sales Order", order_name)
	create_payment_entries(so_doc, payments)


def create_payment_entries(so_doc, payments: list[dict]):
	"""Create payment entries referencing the sales order."""
	for pay in payments or []:
		if not pay.get("amount"):
			continue

		# Create payment entry using helper to ensure exchange rates are set
		pe = create_payment_entry(
			company=so_doc.company,
			customer=so_doc.customer,
			amount=pay.get("amount"),
			currency=pay.get("currency") or so_doc.currency,
			mode_of_payment=pay.get("mode_of_payment"),
			reference_no=so_doc.get("pos_opening_entry"),
			reference_date=nowdate(),
			posting_date=nowdate(),
			submit=0,
		)

		# Link payment entry to the sales order
		pe.append(
			"references",
			{
				"allocated_amount": pay.get("amount"),
				"reference_doctype": "Sales Order",
				"reference_name": so_doc.name,
			},
		)

		pe.flags.ignore_permissions = True
		frappe.flags.ignore_account_permission = True
		pe.save()
		pe.submit()
