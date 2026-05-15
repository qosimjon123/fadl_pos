import frappe
from fadl_pos.api.login.rpc_params import strip_rpc_noise
from fadl_pos.services.invoice_list_service import InvoiceListService


@frappe.whitelist()
def get(action: str, **kwargs):
	"""
	Past POS orders using ERPNext consolidated listing (POS + POS-created Sales Invoice).

	**Route:** ``/api/method/fadl_pos.api.invoice_list.get``

	**Input:**

	- ``action`` (str, required): ``history``.
	- ``history``: optional ``search_term`` (str), ``status`` (str; e.g. ``Paid``, ``Draft``, ``Return``),
	  ``limit`` (int, capped by service).

	**Output:**

	- ``{"invoices": [...]}`` — each row includes ``doctype`` (``POS Invoice`` or ``Sales Invoice``)
	  plus native ``get_past_order_list`` fields (``name``, ``grand_total``, ``currency``, ``customer``, …).
	"""
	return InvoiceListService().get(action, **strip_rpc_noise(kwargs))
