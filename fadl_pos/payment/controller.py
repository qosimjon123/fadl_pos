# Copyright (c) 2026, FadlTech team and contributors

"""payment controller — django-like actions (whitelist → controller → processing)."""

from __future__ import annotations

import json

import frappe
from frappe import _
from frappe.utils import flt, nowdate

from fadl_pos.core.permission import BaseController
from fadl_pos.payment.processing import credit as credit_svc
from fadl_pos.payment.processing import data as payment_data
from fadl_pos.payment.processing.processor import process_pos_payment as _process_pos_payment


class PaymentController(BaseController):
	def get_available_credit(self, customer: str, company: str):
		return credit_svc.get_available_credit(customer, company)

	def get_outstanding_invoices(self, *args, **kwargs):
		return payment_data.get_outstanding_invoices(*args, **kwargs)

	def get_unallocated_payments(self, *args, **kwargs):
		return payment_data.get_unallocated_payments(*args, **kwargs)

	def create_payment_entry(self, data: str | dict) -> dict:
		"""Create a Payment Entry from a POS client payload (dict/JSON)."""
		if isinstance(data, str):
			data = json.loads(data)

		customer = data.get("customer")
		company = data.get("company")
		amount = flt(data.get("amount"))
		mode_of_payment = data.get("mode_of_payment")

		if not all([customer, company, amount, mode_of_payment]):
			frappe.throw(_("Customer, Company, Amount, and Mode of Payment are required"))

		from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account

		account_details = get_bank_cash_account(mode_of_payment, company)

		pe = frappe.new_doc("Payment Entry")
		pe.payment_type = "Receive"
		pe.party_type = "Customer"
		pe.party = customer
		pe.company = company
		pe.paid_amount = amount
		pe.received_amount = amount
		pe.mode_of_payment = mode_of_payment
		pe.paid_to = account_details.get("account")
		pe.posting_date = nowdate()
		pe.reference_no = data.get("reference_no", "POS Payment")
		pe.reference_date = nowdate()

		if data.get("reference_doctype") and data.get("reference_name"):
			pe.append(
				"references",
				{
					"reference_doctype": data["reference_doctype"],
					"reference_name": data["reference_name"],
					"allocated_amount": amount,
				},
			)

		pe.insert(ignore_permissions=True)

		if data.get("submit"):
			pe.submit()

		return {
			"name": pe.name,
			"paid_amount": pe.paid_amount,
			"status": "Submitted" if pe.docstatus == 1 else "Draft",
		}

	def create_payment_request(self, doc: str | dict):
		return credit_svc.create_payment_request(doc)

	def process_pos_payment(self, *args, **kwargs):
		return _process_pos_payment(*args, **kwargs)
