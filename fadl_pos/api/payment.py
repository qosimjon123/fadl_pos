import frappe

from fadl_pos.api.login.rpc_params import strip_rpc_noise
from fadl_pos.services.payment_service import PaymentService


@frappe.whitelist()
def manage(action: str, **kwargs):
	"""
	Loyalty lookup, coupon validation, and POS Invoice partial payments.

	**Route:** ``/api/method/fadl_pos.api.payment.manage`` (GET or POST)

	**Input:**

	- ``action`` (str, required):

	  - ``update_invoice_payments`` — kwargs: ``invoice_name`` (str), ``payments`` (list or JSON string).
	    Each payment row matches native POS Invoice expectations (e.g. ``mode_of_payment``, ``amount``).
	  - ``validate_coupon`` — kwargs: ``coupon_code`` (str).
	  - ``get_loyalty_details`` — kwargs: ``customer`` (str), optional ``posting_date`` (str ``YYYY-MM-DD``).

	Additional kwargs may appear from Frappe RPC; noise keys are stripped via ``strip_rpc_noise``.

	**Output:**

	- ``update_invoice_payments``: ``{"status": "success", "name": "...", "paid_amount": float,
	  "outstanding_amount": float}``
	- ``validate_coupon``: ``{"coupon_code": str, "valid": bool, "message": str}``
	  (uses ``erpnext.accounts.doctype.pricing_rule.utils.validate_coupon_code``).
	- ``get_loyalty_details``: dict from ``erpnext...loyalty_program.get_loyalty_details`` (program/points).
	"""
	kwargs = strip_rpc_noise(kwargs)
	service = PaymentService()
	if "payments" in kwargs and isinstance(kwargs["payments"], str):
		kwargs["payments"] = frappe.parse_json(kwargs["payments"])

	return service.manage(action, **kwargs)
