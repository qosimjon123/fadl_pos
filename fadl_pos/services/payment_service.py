"""
Payments, coupons, loyalty — thin wrappers over ERPNext POS / accounts helpers.

**PaymentService.manage(action, **kwargs)**

* ``update_invoice_payments`` — ``invoice_name`` (POS Invoice only), ``payments`` list → calls
  :meth:`erpnext.accounts.doctype.pos_invoice.pos_invoice.POSInvoice.update_payments`; response includes
  ``paid_amount`` / ``outstanding_amount`` from the saved document.
* ``validate_coupon`` — ``coupon_code`` → ``{\"coupon_code\", \"valid\", \"message\"}``.
* ``get_loyalty_details`` — ``customer``, optional ``posting_date`` → native loyalty detail dict.

Errors use ``frappe.ValidationError`` for wrong doctype or missing documents.
"""

import frappe
from frappe import _
from frappe.utils import today

from fadl_pos.serializers.payment import CouponSerializer, PaymentUpdateResponse
from fadl_pos.services._base import BaseService


class PaymentService(BaseService):
	"""Partial POS payments, coupon validation, loyalty lookup."""

	def manage(self, action: str, **kwargs):
		if action == "update_invoice_payments":
			return self.update_invoice_payments(**kwargs)
		elif action == "validate_coupon":
			return self.validate_coupon(**kwargs)
		elif action == "get_loyalty_details":
			return self.get_loyalty_details(**kwargs)
		else:
			frappe.throw(_("Invalid action: {0}").format(action))

	def update_invoice_payments(self, invoice_name: str, payments: list) -> PaymentUpdateResponse:
		"""
		Uses native :meth:`erpnext.accounts.doctype.pos_invoice.pos_invoice.POSInvoice.update_payments`
		(partial payments / Payment Entry submission). Only **POS Invoice** implements this helper;
		Sales Invoice POS flows use different payment handling.
		"""
		if frappe.db.exists("Sales Invoice", invoice_name):
			frappe.throw(
				_(
					"Partial payments via update_payments are only supported for POS Invoice, "
					"not Sales Invoice ({0}). Use Sales Invoice payment entries."
				).format(invoice_name),
				frappe.ValidationError,
			)
		if not frappe.db.exists("POS Invoice", invoice_name):
			frappe.throw(
				_("POS Invoice {0} was not found.").format(invoice_name),
				frappe.ValidationError,
			)
		doc = frappe.get_doc("POS Invoice", invoice_name)
		doc.update_payments(payments)

		return {
			"status": "success",
			"name": doc.name,
			"paid_amount": doc.paid_amount,
			"outstanding_amount": doc.outstanding_amount,
		}

	def validate_coupon(self, coupon_code: str) -> CouponSerializer:
		"""
		Native wrapper: Validate if a coupon code is still valid.
		"""
		from erpnext.accounts.doctype.pricing_rule.utils import validate_coupon_code

		try:
			validate_coupon_code(coupon_code)
			return {"coupon_code": coupon_code, "valid": True, "message": _("Coupon is valid.")}
		except frappe.ValidationError as e:
			return {"coupon_code": coupon_code, "valid": False, "message": str(e)}

	def get_loyalty_details(self, customer: str, posting_date: str | None = None) -> dict:
		"""
		Native logic: Get customer loyalty program and available points.
		"""
		from erpnext.accounts.doctype.loyalty_program.loyalty_program import get_loyalty_details

		if not posting_date:
			posting_date = today()

		lp_details = get_loyalty_details(customer, posting_date)
		return lp_details
